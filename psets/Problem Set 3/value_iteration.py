from typing import Dict, Optional
from agents import Agent
from environment import Environment
from mdp import MarkovDecisionProcess, S, A
import json
from helpers.utils import NotImplemented

# This is a class for a generic Value Iteration agent
class ValueIterationAgent(Agent[S, A]):
    mdp: MarkovDecisionProcess[S, A] # The MDP used by this agent for training 
    utilities: Dict[S, float] # The computed utilities
                                # The key is the string representation of the state and the value is the utility
    discount_factor: float # The discount factor (gamma)

    def __init__(self, mdp: MarkovDecisionProcess[S, A], discount_factor: float = 0.99) -> None:
        super().__init__()
        self.mdp = mdp
        self.utilities = {state:0 for state in self.mdp.get_states()} # We initialize all the utilities to be 0
        self.discount_factor = discount_factor
    
    # Given a state, compute its utility using the bellman equation
    # if the state is terminal, return 0
    def compute_bellman(self, state: S) -> float:
        # If the state is terminal, its utility is 0 since there are no actions to take
        if self.mdp.is_terminal(state):
            return 0.0
        curr_bellman = float('-INF')
        # For each action, compute its bellman equation value and take the maximum
        for action in self.mdp.get_actions(state):
            bellman = 0.0
            next_states = self.mdp.get_successor(state, action)
            for s, p in next_states.items():
                r = self.mdp.get_reward(state, action , s)
                bellman += p * (r + self.discount_factor * self.utilities[s])
            curr_bellman = max(curr_bellman, bellman)
        return curr_bellman
                   
    
    # Applies a single utility update
    # then returns True if the utilities has converged (the maximum utility change is less or equal the tolerance)
    # and False otherwise
    def update(self, tolerance: float = 0) -> bool:
        U = self.utilities.copy()
        max_diff = 0.0
        # For each state, compute its new utility using the bellman equation
        for state in self.mdp.get_states():
            new_utility = self.compute_bellman(state)
            max_diff = max(max_diff, abs(new_utility - self.utilities[state]))
            # Store the new utility in U(i+1)
            U[state] = new_utility
        # Update the utilities to U(i+1)
        self.utilities = U
        return max_diff <= tolerance

    # This function applies value iteration starting from the current utilities stored in the agent and stores the new utilities in the agent
    # NOTE: this function does incremental update and does not clear the utilities to 0 before running
    # In other words, calling train(M) followed by train(N) is equivalent to just calling train(N+M)
    def train(self, iterations: Optional[int] = None, tolerance: float = 0) -> int:
        it = 0
        while True:
            it += 1 # iteration count
            converged = self.update(tolerance) # update the utilities
            # Check for convergence or max iterations
            if converged or (iterations is not None and it >= iterations):
                break
        return it
    
    # Given an environment and a state, return the best action as guided by the learned utilities and the MDP
    # If the state is terminal, return None
    def act(self, env: Environment[S, A], state: S) -> A:
        if self.mdp.is_terminal(state):
            return None
        best_action = None
        # Find the action that maximizes the expected utility
        for action in self.mdp.get_actions(state):
            next_states = self.mdp.get_successor(state, action)
            expected_utility = 0.0
            # For each action, compute its bellman equation value
            for s, p in next_states.items():
                r = self.mdp.get_reward(state, action , s)
                expected_utility += p * (r + self.discount_factor * self.utilities[s])
            # Take the first action if best_action is None or if the expected utility is better than the best found so far
            if best_action is None or expected_utility > best_expected_utility:
                best_action = action
                best_expected_utility = expected_utility
        return best_action # Return the best action found
    
    # Save the utilities to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            utilities = {self.mdp.format_state(state): value for state, value in self.utilities.items()}
            json.dump(utilities, f, indent=2, sort_keys=True)
    
    # loads the utilities from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            utilities = json.load(f)
            self.utilities = {self.mdp.parse_state(state): value for state, value in utilities.items()}
