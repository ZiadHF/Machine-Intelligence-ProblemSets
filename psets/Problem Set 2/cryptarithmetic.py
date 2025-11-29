from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

# Constraint functions to ensure the sum at each digit position is correct
def constraint_lhs0(letter : int, aux : int) -> bool:
    return letter == aux // 20

def constraint_lhs1(letter: int, aux: int) -> bool:
    return letter == (aux // 2) % 10

def constraint_cin(letter: int, aux: int) -> bool:
    return letter == aux % 2

def constraint_rhs(aux: int, rhs: int) -> bool:
    lhs0 = aux // 20
    lhs1 = (aux // 2) % 10
    cin = aux % 2
    return rhs == (lhs0 + lhs1 + cin) % 10

def constraint_cout(aux: int, cout: int) -> bool:
    lhs0 = aux // 20
    lhs1 = (aux // 2) % 10
    cin = aux % 2
    return cout == (lhs0 + lhs1 + cin) // 10

# This is a class to define for cryptarithmetic puzzles as CSPs
class CryptArithmeticProblem(Problem):
    LHS: Tuple[str, str]
    RHS: str

    # Convert an assignment into a string (so that is can be printed).
    def format_assignment(self, assignment: Assignment) -> str:
        LHS0, LHS1 = self.LHS
        RHS = self.RHS
        letters = set(LHS0 + LHS1 + RHS)
        formula = f"{LHS0} + {LHS1} = {RHS}"
        postfix = []
        valid_values = list(range(10))
        for letter in letters:
            value = assignment.get(letter)
            if value is None: continue
            if value not in valid_values:
                postfix.append(f"{letter}={value}")
            else:
                formula = formula.replace(letter, str(value))
        if postfix:
            formula = formula + " (" + ", ".join(postfix) +  ")" 
        return formula

    @staticmethod
    def from_text(text: str) -> 'CryptArithmeticProblem':
        # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
        # matches and extracts LHS0, LHS1 & RHS
        # For example, it would parse "SEND + MORE = MONEY" and extract the
        # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match: raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        # Variables are the letters and the carrying digits.
        letters = set(LHS0 + LHS1 + RHS)
        carries = len(RHS)  # Maximum possible number of carry digits
        carry_vars = [f"C{i}" for i in range(carries + 1)] # C0 is always 0
        problem.variables = list(letters) + carry_vars

        # Each letter should map to a domain containing digits 0-9
        problem.domains = {letter: set(range(10)) for letter in letters}
        # Each carry variable should map to a domain containing digits 0-1
        for carry in carry_vars:
            problem.domains[carry] = {0, 1}

        problem.constraints = []
        # Add unary constraints to ensure that the leading letters are not assigned the value 0
        leading_letters = {LHS0[0], LHS1[0], RHS[0]}
        for letter in leading_letters:
            problem.constraints.append(
                UnaryConstraint(
                    variable=letter,
                    condition=lambda value: value != 0
                )
            )

        # Add a binary constraint to ensure that the letters are assigned different digits
        letters_list = list(letters)
        for i, letter1 in enumerate(letters_list):
            for letter2 in letters_list[i+1:]:
                problem.constraints.append(
                    BinaryConstraint(
                        variables=(letter1, letter2),
                        condition=lambda val1, val2: val1 != val2
                    )
                )

        # For each position i (from right to left), add a constraint to ensure that:
        # LHS0[i] + LHS1[i] + C[i-1] = RHS[i] + 10*C[i]
        # We will create an auxiliary variable that encodes the sum LHS0[i] + LHS1[i] + C[i-1]

        for i in range(carries):
            # Get the letters from i (rightmost)
            lhs0 = LHS0[-(i+1)] if i < len(LHS0) else None
            lhs1 = LHS1[-(i+1)] if i < len(LHS1) else None
            rhs = RHS[-(i+1)]

            cin = f"C{i}" if i > 0 else None
            cout = f"C{i+1}"

            aux = f"AUX{i}"
            problem.variables.append(aux)

            # We encode the sum as: AUX = lhs0 * 20 + lhs1 * 2 + cin
            # This allows us to extract lhs0, lhs1 and cin from AUX which
            # allows to work as a binary constraint
            problem.domains[aux] = set(range(200))  # Max value is 9*20 + 9*2 + 1 = 189

            # If lhs0 exists, add a binary constraint between lhs0 and aux
            if lhs0 is not None:
                problem.constraints.append(
                    BinaryConstraint(
                        variables=(lhs0, aux),
                        condition=constraint_lhs0
                    )
                )
            else:
                # If lhs0 does not exist, restrict aux domain accordingly
                # we remove all values where lhs0 != 0 which makes our domain now from 0 to 19
                problem.domains[aux] = {value for value in problem.domains[aux] if (value // 20) == 0}
            
            # If lhs1 exists, add a binary constraint between lhs1 and aux
            if lhs1 is not None:
                problem.constraints.append(
                    BinaryConstraint(
                        variables=(lhs1, aux),
                        condition=constraint_lhs1
                    )
                )
            else:
                # If lhs1 does not exist, restrict aux domain accordingly
                # we remove all values where lhs1 != 0 which makes our domain now from 0 to 9 and 180 to 189
                problem.domains[aux] = {value for value in problem.domains[aux] if ((value // 2) % 10) == 0}

            # If cin exists, add a binary constraint between cin and aux
            if cin is not None:
                problem.constraints.append(
                    BinaryConstraint(
                        variables=(cin, aux),
                        condition=constraint_cin
                    )
                )
            else:
                # If cin does not exist, restrict aux domain accordingly
                # we remove all values where cin != 0 which makes our domain now even numbers only
                problem.domains[aux] = {value for value in problem.domains[aux] if (value % 2) == 0}

            # Add binary constraints between aux and rhs, cout
            problem.constraints.append(
                BinaryConstraint(
                    variables=(aux, rhs),
                    condition=constraint_rhs
                )
            )
            problem.constraints.append(
                BinaryConstraint(
                    variables=(aux, cout),
                    condition=constraint_cout
                )
            )

        # C0 should always be 0
        problem.constraints.append(
            UnaryConstraint(
                variable="C0",
                condition=lambda value: value == 0
            )
        )

        # The final carry must also be 0
        problem.constraints.append(
            UnaryConstraint(
                variable=f"C{carries}",
                condition=lambda value: value == 0
            )
        )

        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())