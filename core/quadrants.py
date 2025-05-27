import json
import os
import random

class Plateau:
    def __init__(self, lignes=8, colonnes=8):
        self.lignes = lignes
        self.colonnes = colonnes
        self.grille = [[None for _ in range(colonnes)] for _ in range(lignes)]

    def placer_quadrant(self, quadrant, face="recto", orientation=0, position=(0, 0)):
        bloc = quadrant[face]
        if orientation == 90:
            bloc = list(zip(*bloc[::-1]))
        elif orientation == 180:
            bloc = [ligne[::-1] for ligne in bloc[::-1]]
        elif orientation == 270:
            bloc = list(zip(*bloc))[::-1]

        start_x, start_y = position
        for i in range(4):
            for j in range(4):
                self.grille[start_x + i][start_y + j] = bloc[i][j]

    def placer(self, x, y, valeur):
        if self.grille[x][y] is None:
            self.grille[x][y] = valeur
            return True
        return False

    def lire(self, x, y):
        return self.grille[x][y]

    def afficher(self):
        print("  " + " ".join(str(i) for i in range(self.colonnes)))
        for i, ligne in enumerate(self.grille):
            print(f"{i} " + " ".join(str(cell) if cell else "." for cell in ligne))


def charger_quadrants_personnalises(dossier):
    if not os.path.exists(dossier):
        print(f"[AVERTISSEMENT] Dossier introuvable : {dossier}")
        return []

    quadrants = []
    for fichier in os.listdir(dossier):
        if fichier.endswith(".json"):
            chemin = os.path.join(dossier, fichier)
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "recto" in data:
                    quadrants.append(data)
    return quadrants

def rotate_quadrant(bloc, k):
    # Tourne la matrice 4x4 de k*90°
    for _ in range(k):
        bloc = [list(row) for row in zip(*bloc[::-1])]
    return bloc

# Quadrants par défaut (exemple, à remplacer par chargement réel si besoin)
QUADRANTS_DEFAUT = [
    {
        'recto': [
            ['B','B','R','R'],
            ['J','V','V','J'],
            ['R','V','J','B'],
            ['V','J','B','R'],
        ],
        'verso': [
            ['V','V','J','J'],
            ['B','R','R','B'],
            ['J','B','V','R'],
            ['R','J','B','V'],
        ]
    },
    {
        'recto': [
            ['J','J','V','V'],
            ['B','R','R','B'],
            ['V','B','J','R'],
            ['R','J','B','V'],
        ],
        'verso': [
            ['B','B','J','J'],
            ['V','R','R','V'],
            ['J','V','B','R'],
            ['R','J','V','B'],
        ]
    },
    {
        'recto': [
            ['R','R','B','B'],
            ['J','V','V','J'],
            ['B','J','V','R'],
            ['V','B','J','R'],
        ],
        'verso': [
            ['J','J','R','R'],
            ['B','V','V','B'],
            ['R','B','J','V'],
            ['V','J','B','R'],
        ]
    },
    {
        'recto': [
            ['V','V','B','B'],
            ['J','R','R','J'],
            ['B','J','V','R'],
            ['R','V','J','B'],
        ],
        'verso': [
            ['R','R','V','V'],
            ['B','J','J','B'],
            ['V','B','R','J'],
            ['J','V','B','R'],
        ]
    },
]

def generer_plateau_automatique(quadrants=None):
    """
    Génère un plateau 8x8 à partir de 4 quadrants double face, chacun placé avec une face et une orientation aléatoire.
    quadrants : liste de quadrants (dict recto/verso), sinon QUADRANTS_DEFAUT
    Retourne une matrice 8x8 (liste de listes)
    """
    quadrants = quadrants or QUADRANTS_DEFAUT
    placements = []
    for _ in range(4):
        idx = random.randint(0, len(quadrants)-1)
        face = random.choice(['recto', 'verso'])
        rot = random.randint(0, 3)
        placements.append((idx, face, rot))
    plateau = [[None for _ in range(8)] for _ in range(8)]
    for q, (qx, qy) in enumerate([(0,0),(0,1),(1,0),(1,1)]):
        idx, face, rot = placements[q]
        quad = [row[:] for row in quadrants[idx][face]]
        quad = rotate_quadrant(quad, rot)
        for i in range(4):
            for j in range(4):
                plateau[qx*4+i][qy*4+j] = quad[i][j]
    return plateau

