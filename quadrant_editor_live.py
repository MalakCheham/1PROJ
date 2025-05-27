import tkinter as tk
from tkinter import messagebox

COULEURS = ["R", "J", "B", "V"]
COULEURS_HEX = {
    "R": "#ff9999", "J": "#ffffb3", "B": "#99ccff", "V": "#b3ffb3"
}

class QuadrantEditorLive:
    def __init__(self, root, retour_callback, network_callback=None):
        self.root = root
        self.retour_callback = retour_callback
        self.network_callback = network_callback
        self.current_color = "R"
        self.quadrants = []
        self.grille = [[None for _ in range(4)] for _ in range(4)]

        # Nettoyer la fenêtre
        for widget in root.winfo_children():
            widget.destroy()

        root.configure(bg="#fff8e1")
        tk.Label(root, text="Créer un Quadrant 4x4", font=("Helvetica", 16, "bold"), fg="#006644", bg="#fff8e1").pack(pady=10)

        self.cadre = tk.Frame(root, bg="#fff8e1")
        self.cadre.pack(pady=5)

        self.boutons = [[None for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                btn = tk.Button(self.cadre, text="", width=4, height=2,
                                command=lambda x=i, y=j: self.peindre_case(x, y))
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.boutons[i][j] = btn

        self.choix_couleurs = tk.Frame(root, bg="#fff8e1")
        self.choix_couleurs.pack(pady=10)

        for c in COULEURS:
            tk.Button(self.choix_couleurs, bg=COULEURS_HEX[c], width=4, height=2,
                      command=lambda col=c: self.choisir_couleur(col)).pack(side="left", padx=10)

        self.controls = tk.Frame(root, bg="#fff8e1")
        self.controls.pack(pady=10)

        tk.Button(self.controls, text="✅ Sauvegarder Quadrant", command=self.valider_quadrant,
                  font=("Helvetica", 10), bg="#4CAF50", fg="white", padx=10, pady=5).pack(pady=5)

        tk.Button(self.controls, text="📋 Nouveau Quadrant", command=self.reset,
                  font=("Helvetica", 10), padx=10, pady=5).pack()

        self.info = tk.Label(root, text="Quadrant 1/4", font=("Helvetica", 12), bg="#fff8e1")
        self.info.pack(pady=5)

        self.play_button = tk.Button(root, text="🎮 Jouer avec ces quadrants", command=self.construire_plateau,
                                     font=("Helvetica", 12, "bold"), bg="#0066cc", fg="white")
        self.play_button.pack(pady=10)
        self.play_button.config(state="disabled")

        # Bouton retour vers le menu de choix du jeu
        tk.Button(root, text="⬅ Retour", command=self.retour_callback,
                  font=("Helvetica", 10), bg="#eeeeee").pack(pady=5)

    def choisir_couleur(self, couleur):
        self.current_color = couleur

    def peindre_case(self, i, j):
        self.boutons[i][j].config(bg=COULEURS_HEX[self.current_color])
        self.grille[i][j] = self.current_color

    def valider_quadrant(self):
        if any(None in row for row in self.grille):
            messagebox.showwarning("Incomplet", "Toutes les cases doivent être colorées.")
            return
        self.quadrants.append({"recto": [row[:] for row in self.grille]})
        if len(self.quadrants) == 4:
            messagebox.showinfo("OK", "Les 4 quadrants sont prêts. Cliquez sur 'Jouer avec ces quadrants'.")
            self.play_button.config(state="normal")
        else:
            self.reset()
            self.info.config(text=f"Quadrant {len(self.quadrants)+1}/4")

    def reset(self):
        self.grille = [[None for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                self.boutons[i][j].config(bg="SystemButtonFace")

    def construire_plateau(self):
        if len(self.quadrants) != 4:
            messagebox.showerror("Erreur", "Il faut 4 quadrants pour construire le plateau.")
            return

        from core.plateau import Plateau
        from core.joueur import Joueur
        from jeux.katarenga import JeuKatarenga

        plateau = Plateau()
        positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for i, q in enumerate(self.quadrants):
            bloc = q["recto"]
            for dx in range(4):
                for dy in range(4):
                    plateau.cases[positions[i][0] + dx][positions[i][1] + dy] = bloc[dx][dy]

        pions = {
            'X': {(0, j) for j in range(8)},
            'O': {(7, j) for j in range(8)}
        }  # Seulement pour Katarenga
        joueurs = [Joueur(0, 'X'), Joueur(1, 'O')]
        if self.network_callback:
            self.network_callback(plateau, pions)
        else:
            for widget in self.root.winfo_children():
                widget.destroy()
            JeuKatarenga(plateau, joueurs, pions=pions).jouer()
