import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import sys
from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles

class JeuCongress:
    def __init__(self, plateau, joueurs, mode="1v1"):
        self.plateau = plateau
        self.joueurs = joueurs
        self.tour = 0
        self.mode = mode
        self.timer_seconds = 0
        self.timer_running = True
        self.pion_selectionne = None

        # === Placement initial officiel ===
        pions_noirs = {(0,1), (0,3), (0,5), (0,7), (1,0), (3,0), (5,0), (7,1), (7,3), (7,5), (7,7)}
        pions_blancs = {(0,0), (0,2), (0,4), (0,6), (1,7), (3,7), (5,7), (7,0), (7,2), (7,4), (7,6)}

        for joueur in self.joueurs:
            if joueur.symbole == "X":
                joueur.pions = set(pions_noirs)
            elif joueur.symbole == "O":
                joueur.pions = set(pions_blancs)

    def joueur_actuel(self):
        return self.joueurs[self.tour % 2]

    def jouer(self):
        self.root = tk.Tk()
        self.root.title("Congress")
        self.root.configure(bg="#e6f2ff")

        # === Barre du haut ===
        top_frame = tk.Frame(self.root, bg="#e6f2ff")
        top_frame.pack(fill="x", pady=5, padx=5)

        try:
            retour_img = Image.open("assets/en-arriere.png").resize((24, 24))
            self.retour_icon = ImageTk.PhotoImage(retour_img)
            tk.Button(top_frame, image=self.retour_icon, command=self.retour_menu, bg="#e6f2ff", bd=0).pack(side="left")
        except:
            tk.Button(top_frame, text="<", command=self.retour_menu, bg="#e6f2ff", bd=0).pack(side="left")

        self.timer_label = tk.Label(top_frame, text="00:00", font=("Helvetica", 12, "bold"), bg="#e6f2ff", fg="#003366")
        self.timer_label.pack(side="top")

        try:
            help_img = Image.open("assets/point-dinterrogation.png").resize((24, 24))
            self.help_icon = ImageTk.PhotoImage(help_img)
            tk.Button(top_frame, image=self.help_icon, command=self.aide_popup, bg="#e6f2ff", bd=0).pack(side="right")
        except:
            tk.Button(top_frame, text="?", command=self.aide_popup, bg="#e6f2ff", bd=0).pack(side="right")

        # === Canvas de jeu ===
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        self.afficher_plateau()

        self.update_timer()
        self.root.mainloop()

    def afficher_plateau(self):
        taille = 50
        self.canvas.delete("all")

        for i in range(8):
            for j in range(8):
                couleur = self.plateau.cases[i][j]
                fill = {
                    'R': '#ff9999', 'J': '#ffffb3',
                    'B': '#99ccff', 'V': '#b3ffb3'
                }.get(couleur, 'white')
                self.canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, (i+1)*taille, fill=fill)

        for joueur in self.joueurs:
            for (i, j) in joueur.pions:
                couleur = "black" if joueur.symbole == "X" else "white"
                self.canvas.create_oval(j*taille+10, i*taille+10, (j+1)*taille-10, (i+1)*taille-10, fill=couleur)

        # Afficher sélection
        if self.pion_selectionne:
            i, j = self.pion_selectionne
            self.canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, (i+1)*taille, outline="red", width=3)

    def on_click(self, event):
        i, j = event.y // 50, event.x // 50
        joueur = self.joueur_actuel()

        if self.pion_selectionne is None:
            if (i, j) in joueur.pions:
                self.pion_selectionne = (i, j)
        else:
            if not self.case_occupee(i, j):
                joueur.pions.remove(self.pion_selectionne)
                joueur.pions.add((i, j))
                self.pion_selectionne = None
                self.tour += 1
                self.afficher_plateau()

                if self.verifier_bloc_connecte(joueur):
                    messagebox.showinfo("Victoire", f"Le joueur {joueur.symbole} a gagné !")
                    self.root.quit()
            else:
                messagebox.showinfo("Erreur", "Déplacement invalide (case occupée)")
                self.pion_selectionne = None

        self.afficher_plateau()

    def case_occupee(self, i, j):
        return any((i, j) in jtr.pions for jtr in self.joueurs)

    def voisins_orthogonaux(self, pos):
        i, j = pos
        return [(i+di, j+dj) for (di, dj) in [(-1,0), (1,0), (0,-1), (0,1)]
                if 0 <= i+di < 8 and 0 <= j+dj < 8]

    def verifier_bloc_connecte(self, joueur):
        if not joueur.pions:
            return False

        à_visiter = set()
        visités = set()
        start = next(iter(joueur.pions))
        à_visiter.add(start)

        while à_visiter:
            pion = à_visiter.pop()
            visités.add(pion)
            for voisin in self.voisins_orthogonaux(pion):
                if voisin in joueur.pions and voisin not in visités:
                    à_visiter.add(voisin)

        return len(visités) == len(joueur.pions)

    def update_timer(self):
        if self.timer_running:
            m, s = divmod(self.timer_seconds, 60)
            self.timer_label.config(text=f"{m:02d}:{s:02d}")
            self.timer_seconds += 1
            self.root.after(1000, self.update_timer)

    def retour_menu(self):
        self.root.destroy()
        subprocess.Popen([sys.executable, "menu_gui.py"])

    def aide_popup(self):
        fen = tk.Toplevel(self.root)
        fen.title("Règles du jeu Congress")
        fen.geometry("400x300")
        fen.configure(bg="#f0f4f8")

        titre = tk.Label(fen, text="Règles du jeu Congress", font=("Helvetica", 14, "bold"), bg="#f0f4f8")
        titre.pack(pady=10)

        texte = tk.Text(fen, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        texte.pack(expand=True, fill="both", padx=10, pady=10)
        texte.insert("1.0", get_regles("congress"))
        texte.configure(state="disabled")
