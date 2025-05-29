import json
import os

"""Managing quadrants"""
class Board:
    def __init__(self, num_rows=8, num_columns=8):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.grid = [[None for _ in range(num_columns)] for _ in range(num_rows)]

    def place_quadrant(self, quadrant, face="recto", orientation=0, position=(0, 0)):
        block = quadrant[face]
        if orientation == 90:
            block = list(zip(*block[::-1]))
        elif orientation == 180:
            block = [row[::-1] for row in block[::-1]]
        elif orientation == 270:
            block = list(zip(*block))[::-1]

        start_row, start_col = position
        for row_offset in range(4):
            for col_offset in range(4):
                self.grid[start_row + row_offset][start_col + col_offset] = block[row_offset][col_offset]

    def place(self, row_index, col_index, value):
        if self.grid[row_index][col_index] is None:
            self.grid[row_index][col_index] = value
            return True
        return False

    def get_cell(self, row_index, col_index):
        return self.grid[row_index][col_index]

    def display(self):
        print("  " + " ".join(str(col_index) for col_index in range(self.num_columns)))
        for row_index, row in enumerate(self.grid):
            print(f"{row_index} " + " ".join(str(cell) if cell else "." for cell in row))


def load_custom_quadrants(directory):
    if not os.path.exists(directory):
        return []

    quadrants = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            path = os.path.join(directory, filename)
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict) and "recto" in data:
                    quadrants.append(data)
    return quadrants

