from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented


# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state) 

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that 
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].

def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    terminal_check, terminal_values = game.is_terminal(state)
    if terminal_check:
        return terminal_values[0], None
    if max_depth == 0:
        return heuristic(game, state, 0), None
    
    available_actions = game.get_actions(state)
    agent_turn = game.get_turn(state)
    optimal_action = None
    optimal_value = None
    
    for current_action in available_actions:
        next_state = game.get_successor(state, current_action)
        evaluated_value, _ = minimax(game, next_state, heuristic, max_depth - 1 if max_depth > 0 else -1)
        
        # Update optimal choice based on agent type
        if optimal_value is None:
            optimal_value = evaluated_value
            optimal_action = current_action
        elif agent_turn == 0 and evaluated_value > optimal_value:
            # Maximizing agent
            optimal_value = evaluated_value
            optimal_action = current_action
        elif agent_turn > 0 and evaluated_value < optimal_value:
            # Minimizing agent
            optimal_value = evaluated_value
            optimal_action = current_action
    
    return optimal_value, optimal_action

# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    terminal_check, terminal_values = game.is_terminal(state)
    if terminal_check:
        return terminal_values[0], None
    if max_depth == 0:
        return heuristic(game, state, 0), None
    
    available_actions = game.get_actions(state)
    optimal_action = None
    optimal_value = None
    alpha = float('-inf')
    beta = float('inf')
    
    def alphabeta_search(current_state: S, current_depth: int, alpha_val: float, beta_val: float) -> float:
        term_check, term_values = game.is_terminal(current_state)
        if term_check:
            return term_values[0]
        if current_depth == 0:
            return heuristic(game, current_state, 0)
        
        actions = game.get_actions(current_state)
        turn = game.get_turn(current_state)
        
        # Maximizing player
        if turn == 0:
            max_eval = float('-inf')
            for action in actions:
                next_state = game.get_successor(current_state, action)
                eval_score = alphabeta_search(next_state, current_depth - 1 if current_depth > 0 else -1, alpha_val, beta_val)
                max_eval = max(max_eval, eval_score)
                alpha_val = max(alpha_val, eval_score)
                
                if beta_val <= alpha_val:
                    break  
            return max_eval
        # Minimizing player
        else:
            min_eval = float('inf')
            for action in actions:
                next_state = game.get_successor(current_state, action)
                eval_score = alphabeta_search(next_state, current_depth - 1 if current_depth > 0 else -1, alpha_val, beta_val)
                min_eval = min(min_eval, eval_score)
                beta_val = min(beta_val, eval_score)

                if beta_val <= alpha_val:
                    break 
            return min_eval
    
    # Root level to find best action for player 0
    for current_action in available_actions:
        next_state = game.get_successor(state, current_action)
        evaluated_value = alphabeta_search(next_state, max_depth - 1 if max_depth > 0 else -1, alpha, beta)
        
        if optimal_value is None or evaluated_value > optimal_value:
            optimal_value = evaluated_value
            optimal_action = current_action
            alpha = max(alpha, evaluated_value)
    
    return optimal_value, optimal_action

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    terminal_check, terminal_values = game.is_terminal(state)
    if terminal_check:
        return terminal_values[0], None  
    if max_depth == 0:
        return heuristic(game, state, 0), None
    
    available_actions = game.get_actions(state)
    optimal_action = None
    optimal_value = None
    alpha = float('-inf')
    beta = float('inf')
    
    def order_moves(current_state, actions, is_maximizing):
        action_scores = []
        for action in actions:
            next_state = game.get_successor(current_state, action)
            score = heuristic(game, next_state, 0)
            action_scores.append((action, score))
            
        action_scores.sort(key=lambda x: x[1], reverse=is_maximizing)
        result = []
        for action, _ in action_scores:
            result.append(action)
        return result
    
    def alphabeta_search(current_state: S, current_depth: int, alpha_val: float, beta_val: float) -> float:
        term_check, term_values = game.is_terminal(current_state)
        if term_check:
            return term_values[0]
        if current_depth == 0:
            return heuristic(game, current_state, 0)
        
        actions = game.get_actions(current_state)
        turn = game.get_turn(current_state)
        is_maximizing = (turn == 0)
        ordered_actions = order_moves(current_state, actions, is_maximizing)
        
        # Maximizing player
        if turn == 0:
            max_eval = float('-inf')
            for action in ordered_actions:
                next_state = game.get_successor(current_state, action)
                eval_score = alphabeta_search(next_state, current_depth - 1 if current_depth > 0 else -1, alpha_val, beta_val)
                max_eval = max(max_eval, eval_score)
                alpha_val = max(alpha_val, eval_score)
                if beta_val <= alpha_val:
                    break
            return max_eval
        # Minimizing player
        else:
            min_eval = float('inf')
            for action in ordered_actions:
                next_state = game.get_successor(current_state, action)
                eval_score = alphabeta_search(next_state, current_depth - 1 if current_depth > 0 else -1, alpha_val, beta_val)
                min_eval = min(min_eval, eval_score)
                beta_val = min(beta_val, eval_score)
                if beta_val <= alpha_val:
                    break
            return min_eval
        
    ordered_root_actions = order_moves(state, available_actions, True)
    # Root level to find best action for player 0
    for current_action in ordered_root_actions:
        next_state = game.get_successor(state, current_action)
        evaluated_value = alphabeta_search(next_state, max_depth - 1 if max_depth > 0 else -1, alpha, beta)
        
        if optimal_value is None or evaluated_value > optimal_value:
            optimal_value = evaluated_value
            optimal_action = current_action
        
        alpha = max(alpha, evaluated_value)
    
    return optimal_value, optimal_action

# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    terminal_check, terminal_values = game.is_terminal(state)
    if terminal_check:
        return terminal_values[0], None
    if max_depth == 0:
        return heuristic(game, state, 0), None

    available_actions = game.get_actions(state)
    agent_turn = game.get_turn(state)
    optimal_action = None
    optimal_value = None

    # maximizing agent
    if agent_turn == 0:
        for current_action in available_actions:
            next_state = game.get_successor(state, current_action)
            evaluated_value, _ = expectimax(game, next_state, heuristic, max_depth - 1 if max_depth > 0 else -1)
            if optimal_value is None or evaluated_value > optimal_value:
                optimal_value = evaluated_value
                optimal_action = current_action
    
    # Opponents (chance nodes - act randomly)
    else:
        total_value = 0
        action_count = len(available_actions)
        for current_action in available_actions:
            next_state = game.get_successor(state, current_action)
            evaluated_value, _ = expectimax(game, next_state, heuristic, max_depth - 1 if max_depth > 0 else -1)
            total_value += evaluated_value

        optimal_value = total_value / action_count if action_count > 0 else 0
        optimal_action = None 
        
    return optimal_value, optimal_action