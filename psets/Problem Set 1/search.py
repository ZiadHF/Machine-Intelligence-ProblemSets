from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use
import heapq

def pop_frontier(frontier):
    i = 0
    min_cost, min_state, curr_path = frontier[0]
    for index, (cost, state, path) in enumerate(frontier):
        if (min_cost > cost):
            min_cost = cost
            min_state = state
            curr_path = path
            i = index
    del frontier[i]
    return min_cost, min_state, curr_path

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
    frontier = [(0, initial_state, [])]  # (cost, state, path)
    visited = dict([(initial_state, 0)])  # state: cost
    explored = set()
    while frontier:
        cost, state, path_taken = pop_frontier(frontier)
        if problem.is_goal(state):
            return path_taken

        explored.add(state)
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            new_cost = cost + problem.get_cost(state, action)
            if successor not in explored and successor not in visited:
                visited[successor] = new_cost
                frontier.append((new_cost, successor, path_taken + [action]))
            elif successor in visited and new_cost < visited[successor]:
                visited[successor] = new_cost
                for index, (_, s, _) in enumerate(frontier):
                    if s == successor:
                        frontier[index] = (new_cost, successor, path_taken + [action])
                        break
    return None

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    frontier = []
    counter = 0
    current_costs = {initial_state: 0}
    heapq.heappush(frontier, (heuristic(problem, initial_state), counter, (initial_state, 0, [])))  # (h, counter, (state, cost, path))
    while frontier:
        _, _, (state, cost,  path_taken) = heapq.heappop(frontier)
        if problem.is_goal(state):
            return path_taken

        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            n_cost = cost + problem.get_cost(state, action)
            if successor not in current_costs or n_cost < current_costs[successor]:
                counter += 1
                current_costs[successor] = n_cost
                heapq.heappush(frontier, (heuristic(problem, successor) + n_cost, counter, (successor, n_cost, path_taken + [action])))

    return None


def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    frontier = []
    counter = 0
    heapq.heappush(frontier, (heuristic(problem, initial_state), counter, (initial_state, [])))  # (h, counter, (state, path))
    visited = set([initial_state])
    while frontier:
        _, _, (state, path_taken) = heapq.heappop(frontier)
        if problem.is_goal(state):
            return path_taken

        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            if successor not in visited:
                counter += 1
                heapq.heappush(frontier, (heuristic(problem, successor), counter, (successor, path_taken + [action])))
                visited.add(successor)

    return None