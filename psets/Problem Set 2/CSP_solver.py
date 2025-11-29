from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented

# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        new_domain = {value for value in problem.domains[variable] if constraint.condition(value)}
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable

# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument 
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic, 
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min((len(domains[variable]), index, variable) for index, variable in enumerate(problem.variables) if variable in domains)
    return variable

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    for constraint in problem.constraints:
        # Only consider binary constraints involving the assigned variable
        if not isinstance(constraint, BinaryConstraint) or assigned_variable not in constraint.variables:
            continue
        # Get the other involved variable
        other_variable = constraint.variables[0] if constraint.variables[1] == assigned_variable else constraint.variables[1]
        # If the other variable has no domain, skip this constraint
        if other_variable not in domains:
            continue
        # Update the other variable's domain
        # Make sure to pass arguments in the correct order based on the constraint's variable order
        if constraint.variables[0] == assigned_variable:
            new_domain = {value for value in domains[other_variable] if constraint.condition(assigned_value, value)}
        else:
            new_domain = {value for value in domains[other_variable] if constraint.condition(value, assigned_value)}
        if not new_domain:
            return False
        domains[other_variable] = new_domain
    return True

# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    value_restriction = []
    for value in domains[variable_to_assign]:
        # Create a copy of the domains to simulate the assignment
        local_domains = {var: domains[var].copy() for var in domains if var != variable_to_assign}
        
        # Perform forward checking
        if forward_checking(problem, variable_to_assign, value, local_domains):
            # Calculate the total size of the remaining domains
            total_size = sum(len(local_domains[var]) for var in local_domains)
        else:
            # If forward checking fails, a domain became empty. This is maximally restraining
            # We assign a value smaller than any possible sum (which is 0) to ensure it is sorted last
            total_size = -1
            
        value_restriction.append((total_size, value))

    # Sort values by the size of remaining domains (DESCENDING) and then by value (ASCENDING)
    # We use -x[0] to achieve descending sort for the size
    value_restriction.sort(key=lambda x: (-x[0], x[1]))
    return [value for _, value in value_restriction]

# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    # Apply 1-Consistency first
    if not one_consistency(problem):
        return None
    # Start backtracking with the current domains (which contain all variables initially)
    return backtrack({}, problem, problem.domains)

def backtrack(assignment: Assignment, csp: Problem, domains: Dict[str, set]) -> Optional[Assignment]:
    # Check if the assignment is complete
    if csp.is_complete(assignment):
        return assignment

    # Select the next variable to assign using MRV heuristic
    variable = minimum_remaining_values(csp, domains)

    # Get the values for the variable using least restraining values heuristic
    values = least_restraining_values(csp, variable, domains)

    for value in values:
        # Create a local assignment to test the value
        local_assignment = assignment.copy()
        local_assignment[variable] = value
        
        # Create a copy of domains for the next step, removing the current variable
        local_domains = {var: domains[var].copy() for var in domains if var != variable}
        
        # Perform forward checking
        if forward_checking(csp, variable, value, local_domains):
            # Continue with the backtracking using the new domains
            result = backtrack(local_assignment, csp, local_domains)
            if result is not None:
                return result
                
    # Failure: no valid assignment found
    return None