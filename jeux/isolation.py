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
        self.tour = 0
        self.mode = mode
        self.timer_seconds = 0
        self.timer_running = True

    def joueur_actuel(self):
        return self.joueurs[self.tour % 2]

    def jouer(self):
        self.root = tk.Tk()
        self.root.title("Isolation")
        self.root.configure(bg="#e6f2ff")

        # ==== BARRE DU HAUT ====
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

        # ==== CANVAS ====
        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.afficher_plateau()
        self.canvas.bind("<Button-1>", self.on_click)

        # ==== BOUTON REJOUER ====
        try:
            rejouer_img = Image.open("assets/fleche-pivotante-vers-la-gauche.png").resize((32, 32))
            self.rejouer_icon = ImageTk.PhotoImage(rejouer_img)
            tk.Button(self.root, image=self.rejouer_icon, command=self.rejouer, bg="#e6f2ff", bd=0).pack(pady=10)
        except:
            tk.Button(self.root, text="Rejouer", command=self.rejouer, bg="#e6f2ff", bd=0).pack(pady=10)

        self.update_timer()
        self.root.mainloop()

    def afficher_plateau(self):
        taille = 50
        self.canvas.delete("all")
        for i in range(8):
            for j in range(8):
                couleur = self.plateau.cases[i][j]
                fill = {
                    'R': '#ff9999',
                    'J': '#ffffb3',
                    'B': '#99ccff',
                    'V': '#b3ffb3'
                }.get(couleur, 'white')
                self.canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, (i+1)*taille, fill=fill)

        for joueur in self.joueurs:
            if hasattr(joueur, "pions"):
                for (i, j) in joueur.pions:
                    couleur = "black" if joueur.symbole == "X" else "white"
                    self.canvas.create_oval(j*taille+10, i*taille+10, (j+1)*taille-10, (i+1)*taille-10, fill=couleur)

    def on_click(self, event):
        ligne, colonne = event.y // 50, event.x // 50
        joueur = self.joueur_actuel()
        symbole = joueur.symbole

        # Initialiser si pas encore
        if not hasattr(joueur, "pions"):
            joueur.pions = set()

        # Vérifie que la case est vide
        for j in self.joueurs:
            if hasattr(j, "pions") and (ligne, colonne) in j.pions:
                messagebox.showinfo("Invalide", "Case déjà occupée.")
                return

        # Ajoute le pion
        joueur.pions.add((ligne, colonne))
        self.tour += 1
        self.afficher_plateau()

    def update_timer(self):
        if self.timer_running:
            minutes, seconds = divmod(self.timer_seconds, 60)
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
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

        titre = tk.Label(aide, text="Règles de Isolation", font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366")
        titre.pack(pady=10)

        texte = tk.Text(aide, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        texte.pack(expand=True, fill="both", padx=10, pady=10)
        texte.insert("1.0", get_regles("isolation"))
        texte.configure(state="disabled")


    def rejouer(self):
        self.root.destroy()
        from plateau_builder import lancer_plateau_builder
        lancer_plateau_builder("isolation", self.mode)
