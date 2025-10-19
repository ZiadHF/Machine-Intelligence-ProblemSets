from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use
import heapq

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    queue = deque()
    queue.append((initial_state, []))
    visited = set([initial_state])
    while queue:
        state, path_taken = queue.popleft()
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            if successor not in visited and successor not in queue:
                if problem.is_goal(successor):
                    return path_taken + [action]
                queue.append((successor, path_taken + [action]))
                visited.add(successor)
    return None

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    stack = [(initial_state, [])]
    visited = set([initial_state])
    while stack:
        state, path_taken = stack.pop()
        if problem.is_goal(state):
            return path_taken
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            if successor not in visited:
                visited.add(successor)
                stack.append((successor, path_taken + [action]))
    return None

def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()