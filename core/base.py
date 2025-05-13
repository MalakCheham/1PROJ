class JeuBase:
    def __init__(self, plateau, joueurs):
        self.plateau = plateau        # Le plateau de jeu, partagé par tous les jeux
        self.joueurs = joueurs        # Liste des deux joueurs
        self.tour = 0                 # Numéro du tour actuel

    def joueur_actuel(self):
        return self.joueurs[self.tour % 2]  # Alterne entre joueur 0 et 1 à chaque tour

    def afficher_plateau(self):
        self.plateau.afficher()      # Méthode commune pour afficher le plateau

    def jouer(self):
        raise NotImplementedError("Cette méthode doit être implémentée dans les sous-classes.")
        # On force les classes enfants à implémenter leur propre logique de jeu
