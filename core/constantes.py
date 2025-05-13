TAILLE_PLATEAU = 8
TAILLE_QUADRANT = 4

SYMBOL_JOUEUR_0 = 'X'
SYMBOL_JOUEUR_1 = 'O'

COLOR_MAP = {
    'J': '\033[93m',  # Jaune
    'B': '\033[94m',  # Bleu
    'V': '\033[92m',  # Vert
    'R': '\033[91m',  # Rouge
    'reset': '\033[0m'
}
PIONS_INITIAUX = {
    (0, 1): 'X', (0, 4): 'X', (1, 0): 'X', (1, 7): 'X',
    (7, 1): 'O', (7, 4): 'O', (6, 0): 'O', (6, 7): 'O'
}
