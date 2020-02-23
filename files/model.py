import itertools
import random
def find_subsets(S,m):
    return set(itertools.combinations(S, m))

class Square:
    def __init__(self, number, selected_by):
        self.number = number
        self.selected_by = selected_by
    
    def __repr__(self):
        return f"{self.number} selected by {self.selected_by.name}" if self.selected_by is not None else f"{self.number}"


class Player:
    def __init__(self, game, name, num):
        self.selected_square_set = set()
        self.game = game
        self.name = name
        self.num = num

    def select_square(self, square_number):
        if not self.game.started:
            raise GameNotStartedError("The game hasn't started.")
        if self.game.current_player != self:
            raise NotCurrentPlayerError("It is not your turn.")
        if self.game.board.get_square_object(square_number).selected_by != None:
            raise InvalidSelectionError(f"Square number: {square_number} is already selected")
        self.selected_square_set.add(square_number)
        self.game.board.get_square_object(square_number).selected_by = self


        
    
class Board:

    def __init__(self, board_values, board_sum):
        self.board_values = board_values
        self.board_sum = board_sum
        square_list = []
        for square_value in board_values:
            square_list.append(Square(square_value, None))


        self.square_list = square_list
        self.solution_set = self.generate_solutions(board_values, board_sum)
    
    def get_square_object(self, num):
        for square in self.square_list:
            if square.number == num:
                return square
        raise ValueError(f"Square object with num: {num} does not exist")


    @staticmethod
    def generate_solutions(board_values, sum_goal):
        solutions = []
        subsets = find_subsets(board_values, 3)
        for subset in subsets:
            if sum(subset) == sum_goal:
                solutions.append(set(subset))
        return solutions
    
    def __repr__(self):
        max_length = -1
        output = f"```diff\nYou're trying to get a sum of {self.board_sum}!\n\n"
        for square in self.square_list:
            if len(str(square.number)) > max_length:
                max_length = len(str(square.number))
        max_length += 1
        for square in self.square_list:
            if square.selected_by is None:
                output += "* " + str(square.number) + "\n"
            elif square.selected_by.num == 0:
                output += "* " + str(square.number) + " 💚\n"
            else:
                output += "* " + str(square.number) + " ❤️\n"
        output += "```"
        return output




class Game:
    def __init__(self, board):
        self.board = board
        self.player1 = Player(self, "Player 1", 0)
        self.player2 = Player(self, "Player 2", 1)
        self.current_player = self.player1
        self.started = False

    def start(self):
        if self.started:
            raise GameAlreadyStartedError("The game has already started.") 
        self.started = True
    def next_turn(self):
        self.current_player = (self.player1 if self.current_player == self.player2 else self.player2)
    def game_finished(self):

        for answer_set in self.board.solution_set:
            if answer_set.issubset(self.player1.selected_square_set):
                return (True, self.player1, answer_set)

        for answer_set in self.board.solution_set:
            if answer_set.issubset(self.player2.selected_square_set):
                return (True, self.player2, answer_set)

        return False





def board_solution_generator():
    
    config1 = ((1, 2, 3, 4, 5, 6, 7, 8, 9), 15)
    config2 = ((6,7,8,9,11,12,13,15,17),36)
    config3 = ((2,10,15,18,23,28,31,36,44),69)
    config4 = ((-4,-3,-2,-1,0,1,2,3,4), 0)
    config5 = ((-10,-7, -5, -4, -2, 0, 1, 3, 6), -6)
    config6 = ((-19, -1, 1, 2, 4, 5, 6, 17, 40), 20)
    return random.choice((config1, config2, config4, config5,config6))
class InvalidSelectionError(Exception):
    pass
class NotCurrentPlayerError(Exception):
    pass
class GameNotStartedError(Exception):
    pass
class GameAlreadyStartedError(Exception):
    pass


def BoardGenerateTest():

    board = Board((1, 2, 3, 4, 5, 6, 7, 8, 9), 15)
    print(board.square_list)
    print(Board.generate_solutions((1,2,3,4,5,6,7,8,9), 15))
