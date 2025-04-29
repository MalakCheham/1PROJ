from board import generate_board
from game import Katarenga

if __name__ == "__main__":
    board = generate_board()
    game = Katarenga(board)
    game.play()
