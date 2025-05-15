from core.constantes import TAILLE_PLATEAU, PIONS_INITIAUX

class Plateau:
    def __init__(self):
        self.cases = [[None for _ in range(TAILLE_PLATEAU)] for _ in range(TAILLE_PLATEAU)]
        self.pions = [[None for _ in range(TAILLE_PLATEAU)] for _ in range(TAILLE_PLATEAU)]

    def charger_couleurs(self, grille_couleurs):
        """Charge un plateau 8x8 avec les couleurs données (lettres 'R', 'J', 'B', 'V')."""
        for i in range(TAILLE_PLATEAU):
            for j in range(TAILLE_PLATEAU):
                self.cases[i][j] = grille_couleurs[i][j]

    def charger_pions_initiaux(self):
        """Ajoute les pions initiaux selon le dictionnaire PIONS_INITIAUX."""
        for (ligne, colonne), symbole in PIONS_INITIAUX.items():
            self.pions[ligne][colonne] = symbole

    def afficher(self):
        """Affichage texte du plateau avec les couleurs (console uniquement)."""
        print("  " + " ".join(str(i) for i in range(TAILLE_PLATEAU)))
        for i in range(TAILLE_PLATEAU):
            ligne_affichee = []
            for j in range(TAILLE_PLATEAU):
                case = self.cases[i][j] or '.'
                pion = self.pions[i][j]
                ligne_affichee.append(pion if pion else case)
            print(f"{i} {' '.join(ligne_affichee)}")
    def lire(self, x, y):
        return self.cases[x][y]
