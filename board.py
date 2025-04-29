import random

COLORS = ["B", "V", "J", "R"]
BOARD_SIZE = 8

def generate_quadrant():
    """Génère un quadrant aléatoire (4x4) avec les couleurs B, V, J, R."""
    return [[random.choice(COLORS) for _ in range(4)] for _ in range(4)]

def generate_board():
    """Construit un plateau de 8x8 à partir de 4 quadrants."""
    q1, q2, q3, q4 = generate_quadrant(), generate_quadrant(), generate_quadrant(), generate_quadrant()
    board = [q1[row] + q2[row] for row in range(4)] + [q3[row] + q4[row] for row in range(4)]
    return board

def display_board(board, pieces):
    """Affiche le plateau avec les pions."""
    print("  " + " ".join(str(i) for i in range(BOARD_SIZE)))
    for i in range(BOARD_SIZE):
        row = [board[i][j] for j in range(BOARD_SIZE)]
        for color, positions in pieces.items():
            for (r, c) in positions:
                if r == i:
                    row[c] = color
        print(i, " ".join(row))
