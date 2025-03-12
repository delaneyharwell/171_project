import random
import multiprocessing
import numpy as np
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor, as_completed
from BoardClasses import Move, Board
from copy import deepcopy
import math
import heapq


#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

class Node:
    def __init__(self, game_board, turn, this_move, parent_node):
        self.game_board = game_board
        self.turn = turn
        self.this_move = this_move
        self.parent_node = parent_node
        self.win_count = 0
        self.num_visits = 1
        self.child_nodes = []

    def expand(self, opponent_dict):
        """create child nodes"""
        possible_actions = self.game_board.get_all_possible_moves(opponent_dict[self.turn])
        for moves in possible_actions:
            for m in moves:
                board = self.fast_copy_board(self.game_board)
                board.make_move(m, opponent_dict[self.turn])
                child = Node(board, opponent_dict[self.turn], m, self)
                self.child_nodes.append(child)
        return self.child_nodes[0] if self.child_nodes else None

    def simulate(self, opponent_dict):
        """run smarter simulation from current position"""
        temp_board = self.fast_copy_board(self.game_board)
        current_player = opponent_dict[self.turn]

        for i in range(50):  #range
            possible_moves = temp_board.get_all_possible_moves(current_player)
            if not possible_moves:
                return opponent_dict[current_player]

            if random.random() < 0.9: #choose random 10% of time and best move 90
                best_move = None
                best_eval_diff = -float('inf')
                candidate_moves = [move for move_list in possible_moves for move in move_list]
                capture_moves = []
                for move in candidate_moves:
                    if len(move.seq) > 1:
                        capture_moves.append(move)
                eval_candidates = capture_moves if capture_moves else candidate_moves
                #pool because made time abysmal
                with ThreadPoolExecutor() as executor:
                    futures = {
                        executor.submit(self.evaluate_candidate, temp_board, current_player, move, opponent_dict): move
                        for move in eval_candidates}
                    for future in as_completed(futures):
                        eval_diff, move = future.result()
                        if eval_diff > best_eval_diff:
                            best_eval_diff = eval_diff
                            best_move = move
                if best_move is None:
                    best_move = random.choice(candidate_moves)
            else:
                candidate_moves = [move for move_list in possible_moves for move in move_list]
                best_move = random.choice(candidate_moves)

            temp_board.make_move(best_move, current_player)

            # early termination if poss
            eval_player = self.evaluate_position(temp_board, self.turn)
            eval_opponent = self.evaluate_position(temp_board, opponent_dict[self.turn])
            if abs(eval_player - eval_opponent) > 30:  # Increased from 20
                return self.turn if eval_player > eval_opponent else opponent_dict[self.turn]
            current_player = opponent_dict[current_player]

        player_score = self.evaluate_position(temp_board, self.turn)
        opponent_score = self.evaluate_position(temp_board, opponent_dict[self.turn])

        if player_score > opponent_score:
            return self.turn
        elif player_score < opponent_score:
            return opponent_dict[self.turn]
        else:
            return 0  # Draw

    def evaluate_candidate(self, board, current_player, move, opponent_dict):
        """Helper function to evaluate a candidate move concurrently."""
        board_copy = self.fast_copy_board(board)
        board_copy.make_move(move, current_player)
        eval_diff = self.evaluate_position(board_copy, self.turn) - self.evaluate_position(board_copy,                                                                                opponent_dict[self.turn])
        return eval_diff, move
    
    def select_child(self):
        """select child with highest uct value"""
        return heapq.nlargest(1, self.child_nodes, key=lambda child: child.calculate_uct())[0]

    def backpropagate(self, winner):
        node = self
        while node is not None:
            node.num_visits += 1
            if winner == node.turn:
                node.win_count += 1.5
            elif winner == 0:
                node.win_count += 0.5
            node = node.parent_node
    
    def calculate_uct(self):        
        if self.parent_node is None or self.num_visits == 0: return float('inf')
        exploitation = self.win_count / self.num_visits
        exploration = np.sqrt(np.log(self.parent_node.num_visits)/self.num_visits)
        return exploitation + (1.2 * exploration)

    def evaluate_position(self, board, player):
        score = 0
        color = 'B' if player == 1 else 'W'
        opponent_color = 'W' if player == 1 else 'B'

        for row in range(len(board.board)):
            for col in range(len(board.board[row])):
                checker = board.board[row][col]
                if checker is not None and hasattr(checker, 'color'):
                    if checker.color[0] == color:
                        #base piece
                        score += 10
                        #king value
                        if checker.is_king:
                            score += 15
                        else:
                            #bonus for advancement
                            advancement = row if color == 'B' else (len(board.board) - 1 - row)
                            score += advancement * 3
                        #points for who controls the center
                        center_dist = abs(col - len(board.board[row]) // 2) + abs(row - len(board.board) // 2)
                        score += max(0, 5 - center_dist)
                        if col == 0 or col == len(board.board[row]) - 1:
                            score -= 2
                        # back row
                        if (color == 'B' and row == 0) or (color == 'W' and row == len(board.board) - 1):
                            score += 5
                        # check for protected pieces (unavle to die)
                        if self.is_protected(board, row, col, color):
                            score += 3
                    # opponent piece
                    elif checker.color[0] == opponent_color:
                        score -= 10
                        if checker.is_king:
                            score -= 15

        possible_moves = board.get_all_possible_moves(player)
        move_count = sum(len(moves) for moves in possible_moves)
        score += move_count * 2
        return score

    def is_protected(self, board, row, col, color):
        directions = [(-1, -1), (-1, 1)] if color == 'W' else [(1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < len(board.board) and 0 <= c < len(board.board[r]):
                checker = board.board[r][c]
                if checker is not None and hasattr(checker, 'color') and checker.color[0] == color:
                    return True
        return False

    def fast_copy_board(self, board):
        new_board = Board(board.col, board.row, board.p)
        new_board.tie_counter = board.tie_counter
        new_board.tie_max = board.tie_max
        new_board.board = [[deepcopy(checker) if checker is not None else None for checker in row]
                           for row in board.board]
        new_board.saved_move = deepcopy(board.saved_move)
        new_board.black_count = board.black_count
        new_board.white_count = board.white_count
        return new_board

def parallel_simulate_wrapper(args):
    node, opponent = args
    return node.simulate(opponent)

class StudentAI():
    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2

    # def parallel_simulate(self, node):
    #     return node.simulate(self.opponent)
            
    def mcts(self):
        default_move = Move([])
        root = Node(deepcopy(self.board), self.opponent[self.color], default_move, None)
        root.expand(self.opponent)

        num_simulations = 3000
        num_workers = 8

        with Pool(num_workers) as pool:
            for _ in range(num_simulations // num_workers):
                if not root.child_nodes:
                    root.expand(self.opponent)
                selected_nodes = heapq.nlargest(num_workers, root.child_nodes, key=lambda child: child.calculate_uct())
                args = [(node, self.opponent) for node in selected_nodes]
                results = pool.map(parallel_simulate_wrapper, args)
                for i, winner in enumerate(results):
                        selected_nodes[i].backpropagate(winner)
        best_node = max(root.child_nodes, key=lambda child: child.num_visits, default=None)
        return best_node.this_move if best_node else Move([])
        
    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
            
        best_move = self.mcts()
        self.board.make_move(best_move, self.color)
        return best_move
