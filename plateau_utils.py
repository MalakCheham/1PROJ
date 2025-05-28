from core.plateau import Plateau
import random

def creer_plateau():
    couleurs = ['R', 'J', 'B', 'V']
    plateau = Plateau()
    plateau.cases = [[random.choice(couleurs) for _ in range(8)] for _ in range(8)]
    return plateau
