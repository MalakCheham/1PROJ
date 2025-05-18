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
        self.mode = mode
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.pion_selectionne = None
        self.coups_possibles = set()

        pions_x = {(0,1), (0,3), (0,5), (0,7), (1,0), (3,0), (5,0), (7,1), (7,3), (7,5), (7,7)}
        pions_o = {(0,0), (0,2), (0,4), (0,6), (1,7), (3,7), (5,7), (7,0), (7,2), (7,4), (7,6)}

        for joueur in self.joueurs:
            joueur.pions = pions_x if joueur.symbole == 'X' else pions_o

    def joueur_actuel(self):
        return self.joueurs[self.tour % 2]

    def jouer(self):
        self.root = tk.Tk()
        self.root.title("Congress")
        self.root.configure(bg="#e6f2ff")

        top_frame = tk.Frame(self.root, bg="#e6f2ff")
        top_frame.pack(fill="x", pady=5, padx=5)

        self.load_and_pack_button("assets/en-arriere.png", "<", top_frame, self.retour_menu, "left")
        self.load_and_pack_button("assets/point-dinterrogation.png", "?", top_frame, self.aide_popup, "right")

        self.tour_label = tk.Label(top_frame, text="", font=("Helvetica", 12, "bold"), bg="#e6f2ff", fg="#003366")
        self.tour_label.pack(side="top")

        self.timer_label = tk.Label(top_frame, text="00:00", font=("Helvetica", 12, "bold"), bg="#e6f2ff", fg="#003366")
        self.timer_label.pack(side="top")

        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.load_and_pack_button("assets/fleche-pivotante-vers-la-gauche.png", "Rejouer", self.root, self.rejouer, "bottom", pady=10)

        self.afficher_plateau()
        self.update_info_joueur()
        self.update_timer()

        self.root.mainloop()

    def load_and_pack_button(self, image_path, text, parent, command, side="top", padx=5, pady=5):
        try:
            img = Image.open(image_path).resize((24, 24) if "interrogation" in image_path or "arriere" in image_path else (32, 32))
            icon = ImageTk.PhotoImage(img)
            btn = tk.Button(parent, image=icon, command=command, bg="#e6f2ff", bd=0)
            btn.image = icon
        except:
            btn = tk.Button(parent, text=text, command=command, bg="#e6f2ff", bd=0)
        btn.pack(side=side, padx=padx, pady=pady)

    def update_info_joueur(self):
        joueur = self.joueur_actuel()
        self.tour_label.config(text=f"Tour du Joueur {joueur.id + 1}")

    def afficher_plateau(self):
        taille = 50
        self.canvas.delete("all")
        colors = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}

        for i in range(8):
            for j in range(8):
                fill = colors.get(self.plateau.cases[i][j], 'white')
                self.canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, (i+1)*taille, fill=fill)

        for joueur in self.joueurs:
            couleur = "black" if joueur.symbole == "X" else "white"
            for (i, j) in joueur.pions:
                self.canvas.create_oval(j*taille+10, i*taille+10, (j+1)*taille-10, (i+1)*taille-10, fill=couleur)

        if self.pion_selectionne:
            i, j = self.pion_selectionne
            self.canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, (i+1)*taille, outline="red", width=3)

        for (i, j) in self.coups_possibles:
            self.canvas.create_oval(j*taille+20, i*taille+20, (j+1)*taille-20, (i+1)*taille-20, fill="lightgreen")

    def on_click(self, event):
        i, j = event.y // 50, event.x // 50
        joueur = self.joueur_actuel()

        if self.pion_selectionne is None:
            if (i, j) in joueur.pions:
                self.pion_selectionne = (i, j)
                self.coups_possibles = self.generer_coups_possibles(joueur)
        else:
            if (i, j) in self.coups_possibles:
                joueur.pions.remove(self.pion_selectionne)
                joueur.pions.add((i, j))
                self.pion_selectionne = None
                self.coups_possibles = set()
                self.tour += 1
                self.afficher_plateau()
                self.update_info_joueur()

                if self.verifier_bloc_connecte(joueur):
                    messagebox.showinfo("Victoire", f"Le joueur {joueur.symbole} a gagné !")
                    self.rejouer()
                return
            else:
                self.pion_selectionne = None
                self.coups_possibles = set()

        self.afficher_plateau()

    def generer_coups_possibles(self, joueur):
        possibles = set()
        for i in range(8):
            for j in range(8):
                if not self.case_occupee(i, j):
                    possibles.add((i, j))
        return possibles

    def case_occupee(self, i, j):
        return any((i, j) in jtr.pions for jtr in self.joueurs)

    def voisins_orthogonaux(self, pos):
        i, j = pos
        return [(i+di, j+dj) for (di, dj) in [(-1,0), (1,0), (0,-1), (0,1)] if 0 <= i+di < 8 and 0 <= j+dj < 8]

    def verifier_bloc_connecte(self, joueur):
        if not joueur.pions:
            return False
        a_visiter = {next(iter(joueur.pions))}
        visites = set()

        while a_visiter:
            pion = a_visiter.pop()
            visites.add(pion)
            for voisin in self.voisins_orthogonaux(pion):
                if voisin in joueur.pions and voisin not in visites:
                    a_visiter.add(voisin)

        return len(visites) == len(joueur.pions)

    def update_timer(self):
        if self.timer_running:
            m, s = divmod(self.timer_seconds, 60)
            self.timer_label.config(text=f"{m:02d}:{s:02d}")
            self.timer_seconds += 1
            self.root.after(1000, self.update_timer)

    def pause_timer(self):
        self.timer_running = False

    def reprendre_timer(self):
        self.timer_running = True

    def retour_menu(self):
        self.root.destroy()
        subprocess.Popen([sys.executable, "menu_gui.py"])

    def aide_popup(self):
        self.pause_timer()
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

        def on_close():
            self.reprendre_timer()
            fen.destroy()

        fen.protocol("WM_DELETE_WINDOW", on_close)
    
    def rejouer(self):
        self.root.destroy()
        from plateau_builder import lancer_plateau_builder
        lancer_plateau_builder("congress", self.mode)
