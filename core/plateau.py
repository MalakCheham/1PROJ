from core.constantes import BOARD_SIZE, INITIAL_PIECES

class Board:
    def __init__(self):
        self.cells = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.pieces = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def load_colors(self, color_grid):
        """Load an 8x8 board with the given colors (letters 'R', 'J', 'B', 'V')."""
        for row_index in range(BOARD_SIZE):
            for col_index in range(BOARD_SIZE):
                self.cells[row_index][col_index] = color_grid[row_index][col_index]

    def load_initial_pieces(self):
        """Add initial pieces according to the INITIAL_PIECES dictionary."""
        for (row_index, col_index), symbol in INITIAL_PIECES.items():
            self.pieces[row_index][col_index] = symbol

    def display(self):
        """Text display of the board with colors (console only)."""
        print("  " + " ".join(str(i) for i in range(BOARD_SIZE)))
        for row_index in range(BOARD_SIZE):
            display_row = []
            for col_index in range(BOARD_SIZE):
                cell = self.cells[row_index][col_index] or '.'
                piece = self.pieces[row_index][col_index]
                display_row.append(piece if piece else cell)
            print(f"{row_index} {' '.join(display_row)}")

    def get_cell(self, row_index, col_index):
        return self.cells[row_index][col_index]
