class Joueur:
    def __init__(self, identifiant, symbole):
        self.id = identifiant
        self.symbole = symbole
        self.score = 0

    def __str__(self):
        return f"Joueur {self.id} ({self.symbole})"