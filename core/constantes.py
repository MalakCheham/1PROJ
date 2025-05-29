"""Constantes"""
BOARD_SIZE = 8
QUADRANT_SIZE = 4

PLAYER_0_SYMBOL = 'X'
PLAYER_1_SYMBOL = 'O'

COLOR_MAP = {
    'Y': '\033[93m',
    'B': '\033[94m',
    'G': '\033[92m',
    'R': '\033[91m',
    'reset': '\033[0m'
}
INITIAL_PIECES = {
    (0, 1): 'X', (0, 4): 'X', (1, 0): 'X', (1, 7): 'X',
    (7, 1): 'O', (7, 4): 'O', (6, 0): 'O', (6, 7): 'O'
}
