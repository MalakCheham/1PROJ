MOVES = {
    "B": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],  # Roi
    "V": [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)],  # Cavalier
    "J": "diagonal",  # Fou
    "R": "straight"  # Tour
}

def get_possible_moves(board, pieces, r, c):
    """Retourne les mouvements possibles pour un pion donné."""
    piece_color = "W" if (r, c) in pieces["W"] else "B"
    case_type = board[r][c]
    moves = []

    if case_type in ["B", "V"]:
        for dr, dc in MOVES[case_type]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and (nr, nc) not in pieces[piece_color]:
                moves.append((nr, nc))

    elif case_type == "J":
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = r, c
            while True:
                nr, nc = nr + dr, nc + dc
                if not (0 <= nr < 8 and 0 <= nc < 8):
                    break
                if (nr, nc) in pieces[piece_color]:
                    break
                moves.append((nr, nc))
                if board[nr][nc] == "J":
                    break

    elif case_type == "R":
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r, c
            while True:
                nr, nc = nr + dr, nc + dc
                if not (0 <= nr < 8 and 0 <= nc < 8):
                    break
                if (nr, nc) in pieces[piece_color]:
                    break
                moves.append((nr, nc))
                if board[nr][nc] == "R":
                    break

    return moves
