import tkinter as tk
import random
from PIL import Image, ImageTk
import os

from core.plateau import Plateau
from core.joueur import Joueur
from jeux.katarenga import JeuKatarenga
from jeux.congress import JeuCongress
from jeux.isolation import JeuIsolation

try:
    from core.quadrants import charger_quadrants_personnalises
except ImportError:
    charger_quadrants_personnalises = None  # fallback si non défini

def creer_plateau():
    couleurs = ['R', 'J', 'B', 'V']
    plateau = Plateau()
    plateau.cases = [[random.choice(couleurs) for _ in range(8)] for _ in range(8)]
    pions = {
        'X': {(0, 1), (0, 4), (1, 0), (1, 7)},
        'O': {(7, 1), (7, 4), (6, 0), (6, 7)}
    }
    return plateau, pions

def lancer_plateau_builder(type_jeu, mode_ia=False, plateau_mode="auto"):
    root = tk.Tk()
    root.title("Aperçu du Plateau")
    root.configure(bg="#f0f4f8")

    try:
        icon_img = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
        root.iconphoto(False, icon_img)
    except:
        pass

    if plateau_mode == "auto" or charger_quadrants_personnalises is None:
        plateau, pions = creer_plateau()
    else:
        plateau = Plateau()
        quadrants = charger_quadrants_personnalises(os.path.join("assets", "quadrants_custom"))
        positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for i, q in enumerate(quadrants[:4]):
            if 'recto' in q:
                bloc = q['recto']
                for dx in range(4):
                    for dy in range(4):
                        plateau.cases[positions[i][0] + dx][positions[i][1] + dy] = bloc[dx][dy]
        pions = {
            'X': {(0, 1), (0, 4), (1, 0), (1, 7)},
            'O': {(7, 1), (7, 4), (6, 0), (6, 7)}
        }

    titre = tk.Label(root, text="Plateau généré", font=("Helvetica", 16, "bold"), bg="#f0f4f8")
    titre.pack(pady=10)

    canvas = tk.Canvas(root, width=400, height=400, bg="#f0f4f8", highlightthickness=0)
    canvas.pack()

    taille = 50
    for i in range(8):
        for j in range(8):
            couleur = plateau.cases[i][j] if hasattr(plateau, 'cases') else plateau.lire(i, j)
            fill = {
                'R': '#ff9999', 'J': '#ffffb3',
                'B': '#99ccff', 'V': '#b3ffb3'
            }.get(couleur, 'white')
            canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, i*taille + taille, fill=fill, outline="black")

    def lancer_partie():
        root.destroy()
        joueurs = [Joueur(0, 'X'), Joueur(1, 'O')]
        if type_jeu == "katarenga":
            JeuKatarenga(plateau, joueurs, pions).jouer()
        elif type_jeu == "congress":
            JeuCongress(plateau, joueurs, pions).jouer()
        elif type_jeu == "isolation":
            JeuIsolation(plateau, joueurs).jouer()

    btn = tk.Button(root, text="Lancer la Partie", command=lancer_partie,
                    bg="green", fg="white", font=("Helvetica", 12, "bold"))
    btn.pack(pady=15)

    root.mainloop()
