import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import sys
from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles

class JeuIsolation:
    def __init__(self, plateau, joueurs, mode="1v1"):
        self.plateau = plateau
        self.joueurs = joueurs
        self.mode = mode
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.coups_possibles = set()

        for joueur in joueurs:
            joueur.pions = set()

    def joueur_actuel(self):
        return self.joueurs[self.tour % 2]

    def jouer(self):
        self.root = tk.Tk()
        self.root.title("Isolation")
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

        self.coups_possibles = self.generer_coups_possibles()
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

        for (i, j) in self.coups_possibles:
            self.canvas.create_oval(j*taille+20, i*taille+20, (j+1)*taille-20, (i+1)*taille-20, fill="lightgreen")

    def on_click(self, event):
        i, j = event.y // 50, event.x // 50
        pos = (i, j)
        joueur = self.joueur_actuel()

        if pos not in self.coups_possibles:
            messagebox.showinfo("Invalide", "Ce placement n'est pas autorisé.")
            return

        joueur.pions.add(pos)
        self.tour += 1

        if not self.joueur_peut_jouer(self.joueur_actuel()):
            gagnant = self.joueurs[(self.tour - 1) % 2]
            self.afficher_plateau()
            messagebox.showinfo("Victoire", f"Le joueur {gagnant.id + 1} a gagné !")
            self.rejouer()
            return

        self.coups_possibles = self.generer_coups_possibles()
        self.afficher_plateau()
        self.update_info_joueur()

    def generer_coups_possibles(self):
        possibles = set()
        for i in range(8):
            for j in range(8):
                pos = (i, j)
                if any(pos in jtr.pions for jtr in self.joueurs):
                    continue
                if not any(self.est_adjacent(pos, p) for jtr in self.joueurs for p in jtr.pions):
                    possibles.add(pos)
        return possibles

    def est_adjacent(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1

    def joueur_peut_jouer(self, joueur):
        return bool(self.generer_coups_possibles())

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
        aide = tk.Toplevel(self.root)
        aide.title("Règles du jeu")
        aide.geometry("400x400")
        aide.configure(bg="#f0f4f8")

        tk.Label(aide, text="Règles de Isolation", font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)

        texte = tk.Text(aide, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        texte.pack(expand=True, fill="both", padx=10, pady=10)
        texte.insert("1.0", get_regles("isolation"))
        texte.configure(state="disabled")

    def rejouer(self):
        self.root.destroy()
        from plateau_builder import lancer_plateau_builder
        lancer_plateau_builder("isolation", self.mode)
