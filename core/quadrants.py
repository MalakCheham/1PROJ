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