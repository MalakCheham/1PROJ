import tkinter as tk
from core.constantes import BOARD_SIZE, COLOR_MAP

"""Display module"""
class BoardGUI:
    def __init__(self, root, board, pieces, on_selection):
        self.root = root
        self.board = board
        self.pieces = pieces
        self.on_selection = on_selection
        self.selected = None

        self.cell_size = 60
        canvas_size = BOARD_SIZE * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_click)

        self.display_board()

    def on_click(self, event):
        row_index = event.y // self.cell_size
        col_index = event.x // self.cell_size
        if 0 <= row_index < BOARD_SIZE and 0 <= col_index < BOARD_SIZE:
            self.on_selection((row_index, col_index))

    def display_board(self):
        self.canvas.delete("all")
        for row_index in range(BOARD_SIZE):
            for col_index in range(BOARD_SIZE):
                x1 = col_index * self.cell_size
                y1 = row_index * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color_code = self.board.lire(row_index, col_index)
                color_hex = COLOR_MAP.get(color_code, "#dddddd")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color_hex, outline="black")

                piece = self.pieces.get((row_index, col_index))
                if piece:
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10,
                                            fill="black" if piece == 'X' else "white")

    def update(self):
        self.display_board()
