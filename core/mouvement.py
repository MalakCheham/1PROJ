"""Mouvement rules"""

MOVES = {
    "B": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],
    "V": [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)],
    "J": "diagonal",
    "R": "straight"
}
class Movement:
    def __init__(self, board, pieces):
        self.board = board
        self.pieces = pieces

    def get_possible_moves(self, board, pieces, row, col):
        symbol = "W" if (row, col) in pieces["W"] else "B"
        cell_type = board[row][col]
        possible_moves = []

        if cell_type in ["B", "V"]:
            for delta_row, delta_col in MOVES[cell_type]:
                new_row, new_col = row + delta_row, col + delta_col
                if 0 <= new_row < 10 and 0 <= new_col < 10 and (new_row, new_col) not in pieces[symbol]:
                    possible_moves.append((new_row, new_col))

        elif cell_type == "J":
            for delta_row, delta_col in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                new_row, new_col = row, col
                while True:
                    new_row, new_col = new_row + delta_row, new_col + delta_col
                    if not (0 <= new_row < 10 and 0 <= new_col < 10):
                        break
                    if (new_row, new_col) in pieces[symbol]:
                        break
                    possible_moves.append((new_row, new_col))
                    if board[new_row][new_col] == "J":
                        break

        elif cell_type == "R":
            for delta_row, delta_col in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                new_row, new_col = row, col
                while True:
                    new_row, new_col = new_row + delta_row, new_col + delta_col
                    if not (0 <= new_row < 10 and 0 <= new_col < 10):
                        break
                    if (new_row, new_col) in pieces[symbol]:
                        break
                    possible_moves.append((new_row, new_col))
                    if board[new_row][new_col] == "R":
                        break

        return possible_moves

    def is_valid_move(self, pieces, symbol, start, end):
        start_row, start_col = start
        return end in self.get_possible_moves(self.board.grille, pieces, start_row, start_col)


def is_king_move(start, end):
    delta_row, delta_col = abs(end[0] - start[0]), abs(end[1] - start[1])
    return delta_row <= 1 and delta_col <= 1 and (delta_row != 0 or delta_col != 0)

def is_knight_move(start, end):
    delta_row, delta_col = abs(end[0] - start[0]), abs(end[1] - start[1])
    return (delta_row == 2 and delta_col == 1) or (delta_row == 1 and delta_col == 2)

def is_bishop_move(start, end, board, pieces):
    if abs(end[0] - start[0]) != abs(end[1] - start[1]):
        return False
    step_row = 1 if end[0] > start[0] else -1
    step_col = 1 if end[1] > start[1] else -1
    row, col = start[0] + step_row, start[1] + step_col
    size = len(board.cells)
    while (row, col) != end:
        if not (0 <= row < size and 0 <= col < size):
            return False
        if (row, col) in pieces['X'] or (row, col) in pieces['O']:
            return False
        if board.cells[row][col] == 'J':
            return (row, col) == end
        row += step_row
        col += step_col
    return True

def is_rook_move(start, end, board, pieces):
    if start[0] != end[0] and start[1] != end[1]:
        return False
    step_row = 0 if start[0] == end[0] else (1 if end[0] > start[0] else -1)
    step_col = 0 if start[1] == end[1] else (1 if end[1] > start[1] else -1)
    row, col = start[0] + step_row, start[1] + step_col
    size = len(board.cells)
    while (row, col) != end:
        if not (0 <= row < size and 0 <= col < size):
            return False
        if (row, col) in pieces['X'] or (row, col) in pieces['O']:
            return False
        if board.cells[row][col] == 'R':
            return (row, col) == end
        row += step_row
        col += step_col
    return True

def generate_possible_moves(start, color, symbol, board, pieces, capture=True):
    possible_moves = set()
    size = len(board.cells)
    for row in range(size):
        for col in range(size):
            end = (row, col)
            piece_at_end = next((s for s in ['X', 'O'] if end in pieces[s]), None)
            if capture:
                if piece_at_end is None or piece_at_end != symbol:
                    valid_move = (
                        (color == 'B' and is_king_move(start, end)) or
                        (color == 'V' and is_knight_move(start, end)) or
                        (color == 'J' and is_bishop_move(start, end, board, pieces)) or
                        (color == 'R' and is_rook_move(start, end, board, pieces))
                    )
                    if valid_move:
                        possible_moves.add(end)
            else:
                if (end in pieces['X']) or (end in pieces['O']):
                    continue
                valid_move = (
                    (color == 'B' and is_king_move(start, end)) or
                    (color == 'V' and is_knight_move(start, end)) or
                    (color == 'J' and is_bishop_move(start, end, board, pieces)) or
                    (color == 'R' and is_rook_move(start, end, board, pieces))
                )
                if valid_move:
                    possible_moves.add(end)
    return possible_moves

def can_enter_camp(symbol, position, start=None):
    if symbol == 'X' and position in [(9,0), (9,9)] and (start is None or start[0] == 8):
        return True
    if symbol == 'O' and position in [(0,0), (0,9)] and (start is None or start[0] == 1):
        return True
    return False
