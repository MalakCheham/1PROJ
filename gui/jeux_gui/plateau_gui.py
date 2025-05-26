# Remplacer toute la logique Tkinter par Pygame dans chaque fichier de jeux_gui (congress.py, isolation.py, katarenga.py, plateau_builder.py, plateau_gui.py, quadrant_editor_live.py déjà fait).
# Pour chaque fichier, créer une classe principale qui gère l'affichage, les boutons, la grille, etc. avec Pygame.
# Utiliser pygame.font pour les textes, pygame.draw pour les boutons et la grille, et gérer les événements souris/clavier.

import tkinter as tk
from core.constantes import TAILLE_PLATEAU, COLOR_MAP

class PlateauGUI:
    def __init__(self, root, plateau, pions, on_selection):
        self.root = root
        self.plateau = plateau
        self.pions = pions
        self.on_selection = on_selection
        self.selected = None

        self.cell_size = 60
        canvas_size = TAILLE_PLATEAU * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_size, height=canvas_size)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.clic)

        self.afficher_plateau()

    def clic(self, event):
        row = event.y // self.cell_size
        col = event.x // self.cell_size
        if 0 <= row < 8 and 0 <= col < 8:
            self.on_selection((row, col))

    def afficher_plateau(self):
        self.canvas.delete("all")
        for i in range(TAILLE_PLATEAU):
            for j in range(TAILLE_PLATEAU):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                couleur = self.plateau.lire(i, j)
                couleur_hex = COLOR_MAP.get(couleur, "#dddddd")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=couleur_hex, outline="black")

                pion = self.pions.get((i, j))
                if pion:
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10,
                                            fill="black" if pion == 'X' else "white")

    def mise_a_jour(self):
        self.afficher_plateau()
