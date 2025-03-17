import random  
from BoardClasses import Move
from copy import deepcopy
from BoardClasses import Board
import math

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
        """run random simulation from current position"""
        temp_board = self.fast_copy_board(self.game_board)
        current_player = opponent_dict[self.turn]
        
        for i in range(50): # depth
            possible_moves = temp_board.get_all_possible_moves(current_player)
            if not possible_moves:
                return opponent_dict[current_player] # no moves are available, the current player loses
            
            selected_checker_moves = random.choice(possible_moves)
            selected_move = random.choice(selected_checker_moves)
            
            temp_board.make_move(selected_move, current_player)
            current_player = opponent_dict[current_player]
            
        player_score = self.evaluate_position(temp_board, self.turn)
        opponent_score = self.evaluate_position(temp_board, opponent_dict[self.turn])
        
        if player_score > opponent_score:
            return self.turn
        elif player_score < opponent_score:
            return opponent_dict[self.turn]
        else:
            return 0
    
    def select_child(self):
        """select child with highest uct value"""
        return max(self.child_nodes, key=lambda child: child.calculate_uct())
    
    def backpropagate(self, winner):
        node = self
        while node is not None:
            node.num_visits += 1
            if winner == node.turn:
                node.win_count += 1
            elif node.parent_node and winner == node.parent_node.turn:
                node.win_count -= 1
            node = node.parent_node
    
    def calculate_uct(self):        
        if self.parent_node is None or self.num_visits == 0: return float('inf')
        exploitation = self.win_count/self.num_visits            
        exploration = math.sqrt(math.log(self.parent_node.num_visits)/self.num_visits)
        return exploitation + (math.sqrt(2) * exploration)
    
    def evaluate_position(self, board, player):
        score = 0
        color = 'B' if player is 1 else 'W'
        for row in board.board:
            for checker in row:
                if checker is not None and hasattr(checker, 'color'):
                    if checker.color[0] == color:
                        score += 10
                        if checker.is_king:
                            score += 5          
        return score

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
            
    def mcts(self):
        default_move = Move([])
        root = Node(deepcopy(self.board), self.opponent[self.color], default_move, None)
        root.expand(self.opponent)
        
        for i in range(1000): # number of iterations
            node = root
            winner = 0
            
            while True:
                if not node.child_nodes:
                    if node.num_visits >= 10: 
                        new_node = node.expand(self.opponent)
                        if new_node is None:
                            winner = node.turn
                            break
                        node = new_node
                        continue
                    winner = node.simulate(self.opponent)
                    break
                node = node.select_child()
            
            node.backpropagate(winner)
        
        best_node = None
        max_visits = -1
        
        for child in root.child_nodes:
            if child.num_visits > max_visits:
                max_visits = child.num_visits
                best_node = child
                
        return best_node.this_move if best_node else default_move
        
    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
            
        best_move = self.mcts()
        self.board.make_move(best_move, self.color)
        return best_move
