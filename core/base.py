""""Utility funtions for the game"""
class GameBase:
    def __init__(self, board, players):
        self.board = board
        self.players = players
        self.turn = 0

    def current_player(self):
        return self.players[self.turn % 2]

    def display_board(self):
        self.board.display()

    def play(self):
        raise NotImplementedError("This method must be implemented in subclasses.")
