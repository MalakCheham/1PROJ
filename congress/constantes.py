COLOR_MAP = {
    'J': '\033[93m',  # Jaune
    'B': '\033[94m',  # Bleu
    'V': '\033[92m',  # Vert
    'R': '\033[91m',  # Rouge
    'reset': '\033[0m'  # Réinitialisation
}

ORIENTATIONS_VALIDES = [0, 90, 180, 270]

TAILLE_PLATEAU = 8
TAILLE_QUADRANT = 4

SYMBOL_JOUEUR_0 = 'X'
SYMBOL_JOUEUR_1 = 'O'

EMPLACEMENTS_COORDONNEES = {
    1: (0, 0),
    2: (0, 4),
    3: (4, 0),
    4: (4, 4)
}

PIONS_INITIAUX = {
    (0, 1): 'X',
    (0, 3): 'O',
    (0, 4): 'X',
    (0, 6): 'O',
    (1, 0): 'O',
    (1, 7): 'X',
    (3, 0): 'X',
    (3, 7): 'O',
    (4, 0): 'O',
    (4, 7): 'X',
    (6, 0): 'X',
    (6, 7): 'O',
    (7, 1): 'O',
    (7, 3): 'X',
    (7, 4): 'O',
    (7, 6): 'X'
}

QUADRANTS_COULEURS = {
    1: {
        "recto": [['J', 'B', 'V', 'R'], ['R', 'V', 'J', 'J'], ['V', 'R', 'B', 'B'], ['B', 'J', 'R', 'V']],
        "verso": [['R', 'V', 'B', 'J'], ['J', 'B', 'R', 'R'], ['B', 'J', 'V', 'V'], ['V', 'R', 'J', 'B']]
    },
    2: {
        "recto": [['V', 'B', 'J', 'R'], ['R', 'B', 'J', 'V'], ['J', 'R', 'V', 'B'], ['B', 'V', 'R', 'J']],
        "verso": [['J', 'R', 'B', 'V'], ['V', 'R', 'B', 'J'], ['B', 'V', 'J', 'R'], ['R', 'J', 'V', 'B']]
    },
    3: {
        "recto": [['V', 'B', 'R', 'J'], ['B', 'V', 'B', 'R'], ['J', 'R', 'J', 'V'], ['R', 'V', 'J', 'B']],
        "verso": [['J', 'R', 'B', 'V'], ['V', 'J', 'V', 'B'], ['B', 'V', 'R', 'J'], ['R', 'J', 'V', 'B']]
    },
    4: {
        "recto": [['J', 'B', 'V', 'R'], ['R', 'B', 'J', 'J'], ['B', 'V', 'R', 'V'], ['V', 'R', 'J', 'B']],
        "verso": [['R', 'V', 'B', 'J'], ['J', 'V', 'R', 'R'], ['V', 'B', 'J', 'V'], ['B', 'R', 'V', 'J']]
    }
}

MODELE_QUADRANT = [['.', '.', '.', '.'], ['.', '.', '.', '.'], ['.', '.', '.', '.'], ['.', '.', '.', '.']]