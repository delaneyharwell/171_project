from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
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

    def simulate_random_game(self, board, player):
        """random game to determine winner"""

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        moves = self.board.get_all_possible_moves(self.color)
        if not moves:
            return None
        best_move = None
        best_score = -1
        for move_list in moves:
            for move in move_list:
                temp_board = self.board.get_copy()
                temp_board.make_move(move, self.color)
                wins = sum(self.simulate_random_game(temp_board, self.opponent[self.color]) for _ in range(5))
                if wins > best_score:
                    best_score = wins
                    best_move = move
        self.board.make_move(best_move,self.color)
        return best_move
