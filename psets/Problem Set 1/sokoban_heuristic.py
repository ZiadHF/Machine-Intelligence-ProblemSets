from typing import Dict, FrozenSet, List
from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

from collections import deque
import itertools

# SokobanState has the following attributes:
# layout: SokobanLayout
# player: Point
# crates: FrozenSet[Point]

# SokobanLayout has the following attributes:
# width: int
# height: int
# walkable: FrozenSet[Point]
# goals: FrozenSet[Point]

def is_unwalkable(p: Point, problem: SokobanProblem) -> bool:
    '''
    Checks if a position is unwalkable (i.e., a deadlock position)
    A position is unwalkable if it is a corner (i.e., has walls on two adjacent sides)
    '''
    directions = [
        Direction.UP,
        Direction.DOWN,
        Direction.LEFT,
        Direction.RIGHT
    ]

    # lambda function to check if a position is a wall
    is_wall = lambda p: p not in problem.layout.walkable

    # check for corner deadlock (UL, UR, DL, DR)
    for i in range(2):
        dir = p + directions[i].to_vector()
        left = p + directions[2].to_vector()
        right = p + directions[3].to_vector()
        if is_wall(dir) and (is_wall(left) or is_wall(right)):
            return True
    return False

def compute_deadlocks(problem: SokobanProblem) -> FrozenSet[Point]:
    '''
    Computes all deadlock positions in the sokoban layout
    A deadlock position is a position where if a crate is pushed there, it can never be moved to a goal
    '''
    deadlocks = set()
    layout = problem.layout
    for p in layout.walkable:
        if p in layout.goals:
            continue
        if is_unwalkable(p, problem):
            deadlocks.add(p)
    return frozenset(deadlocks)


def calculate_dist(problem: SokobanProblem) -> Dict[Point, Dict[Point, int]]:
    '''
    For each goal, perform a BFS to calculate the distance to all reachable points
    Returns a dictionary mapping each goal to a dictionary of point distances
    '''
    goals = problem.layout.goals
    layout = problem.layout
    total_dist = dict()
    for goal in goals:
        queue = deque([(goal, 0)])
        visited = set([goal])
        dist = dict()
        while queue:
            current, cost = queue.popleft()
            dist[current] = cost
            for direction in Direction:
                neighbor = current + direction.to_vector() # position of neighbor
                push = neighbor + direction.to_vector() # position of push
                if neighbor in layout.walkable and push in layout.walkable:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, cost + 1))
        total_dist[goal] = dist
    return total_dist

def minimum_iteration(matrix : List[List[float]]) -> float:
    '''
    Finds the minimum value in each row and returns the sum of these minimums
    '''
    workers = len(matrix)
    jobs = len(matrix[0]) if workers > 0 else 0
    current_min = float('inf')
    for cols in itertools.permutations(range(jobs), workers):
        sum = 0
        for i in range(workers):
            sum += matrix[i][cols[i]]
        current_min = min(current_min, sum)
    if current_min >= 1e9:
        return float('inf')
    return current_min


def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    '''
    This heuristic computes the minimum cost to move all crates to goals using the Hungarian Algorithm
    It also checks for deadlocks and returns infinity if any crate is in a deadlock position
    '''
    cache = problem.cache()
    if "deadlocks" not in cache:
        cache["deadlocks"] = compute_deadlocks(problem)
    if "dist" not in cache:
        cache["dist"] = calculate_dist(problem)
    
    deadlocks = cache["deadlocks"]
    dist = cache["dist"]

    if problem.is_goal(state):
        return 0.0
    
    if any(crate in deadlocks for crate in state.crates):
        return float('inf')

    crates = list(state.crates)
    goals = list(problem.layout.goals)
    crates_number = len(crates)
    distances = [[1e9] * crates_number for _ in range(crates_number)]

    # Calculate the cost matrix
    for i in range(crates_number):
        crate = crates[i]
        for j in range(crates_number):
            goal = goals[j]
            distances[i][j] = dist[goal].get(crate, 1e9)
    
    # Use the minimum iteration method to find the minimum sum
    total_sum = minimum_iteration(distances)
    return total_sum


# ---------------- Unused Hungarian Algorithm Implementation ---------------- #

def find_path(location: tuple, zero_matrix: List[List[int]]):
    '''
    Finds an augmenting path in the zero matrix
    '''
    path = [location]
    while True:
        # find starred zero in this column
        row_star = [i for i in range(len(zero_matrix)) if zero_matrix[i][path[-1][1]] == 1]
        if len(row_star) == 0:
            break
        else:
            path.append((row_star[0], path[-1][1]))
            col_prime = [j for j in range(len(zero_matrix[0])) if zero_matrix[path[-1][0]][j] == 2][0]
            path.append((path[-1][0], col_prime))
    return path

def mark_zeroes(matrix: List[List[float]]):
    '''
    Marks the zeroes in the matrix and returns the number of rows and columns covered
    '''
    workers = len(matrix)
    jobs = len(matrix[0]) if workers > 0 else 0
    zero_matrix = [[0 for _ in range(jobs)] for _ in range(workers)]
    rows_covered = [False] * workers
    cols_covered = [False] * jobs
    used_cols = [False] * jobs
    
    # For each row, find an arbitrary zero and mark it (I mark the first zero I find that still works within the constraints)
    for i in range(workers):
        for j in range(jobs):
            if matrix[i][j] == 0 and not used_cols[j]:
                zero_matrix[i][j] = 1  # Star the zero
                used_cols[j] = True
                break
    
    done = False
    while not done:
        # Cover columns containing a starred zero
        for j in range(jobs):
            if any(zero_matrix[i][j] == 1 for i in range(workers)):
                cols_covered[j] = True
        found = False
        for i in range(workers):
            for j in range(jobs):
                if matrix[i][j] == 0 and not rows_covered[i] and not cols_covered[j]:
                    zero_matrix[i][j] = 2  # Prime the zero
                    found_starred = False
                    # Check if there is a starred zero in the same row
                    for col in range(jobs):
                        if zero_matrix[i][col] == 1:
                            rows_covered[i] = True
                            cols_covered[col] = False
                            found_starred = True
                            break
                    if not found_starred:
                        path = find_path((i, j), zero_matrix)
                        # For all zeros in the path, unstar starred zeros and star primed zeros
                        for r, c in path:
                            zero_matrix[r][c] = zero_matrix[r][c] - 1
                    # Clear all covers and erase all primes
                    rows_covered = [False] * workers
                    cols_covered = [False] * jobs
                    for r in range(workers):
                        for c in range(jobs):
                            if zero_matrix[r][c] == 2:
                                zero_matrix[r][c] = 0
                    found = True
        done = not found
    
    num_covered = sum(cols_covered) + sum(rows_covered)
    return num_covered, zero_matrix, rows_covered, cols_covered

def kuhn_munkres(matrix : List[List[float]]) -> float:
    '''
    Implementation of the Hungarian Algorithm (Kuhn-Munkres) to find the minimum cost matching
    '''
    workers = len(matrix)
    jobs = len(matrix[0]) if workers > 0 else 0
    original = [row[:] for row in matrix]
    
    # Step 1: Minimization of rows
    for i in range(workers):
        row_min = min(matrix[i])
        for j in range(jobs):
            if matrix[i][j] < 1e9:
                matrix[i][j] -= row_min
    
    # Step 2: Minimization of columns
    for j in range(jobs):
        col_min = min(matrix[i][j] for i in range(workers))
        for i in range(workers):
            if matrix[i][j] < 1e9:
                matrix[i][j] -= col_min
    
    # Step 3: Cover zeros with minimum number of lines
    done = False
    while not done:
        num_covered, zero_matrix, rows_covered, cols_covered = mark_zeroes(matrix)
        
        if num_covered == min(workers, jobs):
            done = True
        else:
            uncovered_values = [matrix[i][j] for i in range(workers) for j in range(jobs) 
                              if not rows_covered[i] and not cols_covered[j]]
            
            if uncovered_values:
                min_uncovered = min(uncovered_values)
                for i in range(workers):
                    for j in range(jobs):
                        if not rows_covered[i]:
                            matrix[i][j] -= min_uncovered
                        if cols_covered[j]:
                            matrix[i][j] += min_uncovered
            else:
                done = True
                
    # Calculate the total cost based on the original matrix
    total_cost = 0.0
    for i in range(workers):
        for j in range(jobs):
            if zero_matrix[i][j] == 1:  # Find the starred zeros
                total_cost += original[i][j]

    # Return infinity if cost is too high
    if total_cost >= 1e9:
        return float('inf')
        
    return total_cost
# -------------------------------------------------------------------------- #

