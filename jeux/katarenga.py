import os
import subprocess
import sys
import threading
import tkinter as tk

from PIL import Image, ImageTk
from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles
from tkinter import messagebox

class JeuKatarenga:
    def __init__(self, plateau, joueurs, mode="1v1", root=None, sock=None, is_host=False, noms_joueurs=None):
        self.plateau, self.joueurs, self.mode = plateau, joueurs, mode
        self.pions = {'X': {(0, j) for j in range(8)}, 'O': {(7, j) for j in range(8)}}
        self.tour, self.timer_seconds, self.timer_running, self.selection = 0, 0, True, None
        self.coups_possibles = set()
        self.sock = sock
        self.is_host = is_host
        self.root = root if root else tk.Tk()
        self.root.title("Katarenga")
        self.root.configure(bg="#e6f2ff")
        self.noms_joueurs = noms_joueurs or ["Joueur Blanc", "Joueur Noir"]

        self.top_frame = tk.Frame(self.root, bg="#e6f2ff")
        self.top_frame.pack(fill="x", pady=5, padx=5)

        self.tour_label = tk.Label(self.top_frame, text="", font=("Helvetica", 12, "bold"), bg="#e6f2ff", fg="#003366")
        self.tour_label.pack(side="top")

        self.pions_restants_label = tk.Label(self.top_frame, text="", font=("Helvetica", 10), bg="#e6f2ff", fg="#003366")
        self.pions_restants_label.pack(side="top")

        self.timer_label = tk.Label(self.top_frame, text="00:00", font=("Helvetica", 12, "bold"), bg="#e6f2ff", fg="#003366")
        self.timer_label.pack(side="top")

        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.afficher_plateau()
        self.canvas.bind("<Button-1>", self.on_click)

        self.load_and_pack_button("en-arriere.png", "<", self.top_frame, self.retour_menu, "left")
        self.load_and_pack_button("point-dinterrogation.png", "?", self.top_frame, self.aide_popup, "right")
        self.load_and_pack_button("fleche-pivotante-vers-la-gauche.png", "Rejouer", self.root, self.rejouer, "bottom", pady=10)

        self.update_info_joueur()
        self.start_timer()
        if self.sock:
            threading.Thread(target=self.network_listener, daemon=True).start()
            self.lock_ui_if_needed()
        else:
            self.canvas.bind("<Button-1>", self.on_click)

    def jouer(self):
        self.root.mainloop()

    def load_and_pack_button(self, image_path, text, parent, command, side="top", padx=5, pady=5):
        try:
            img = Image.open(os.path.join("assets", image_path)).resize((24, 24) if "arriere" in image_path or "interrogation" in image_path else (32, 32))
            icon = ImageTk.PhotoImage(img)
            btn = tk.Button(parent, image=icon, command=command, bg="#e6f2ff", bd=0)
            btn.image = icon
        except:
            btn = tk.Button(parent, text=text, command=command, bg="#e6f2ff", bd=0)
        btn.pack(side=side, padx=padx, pady=pady)

    def joueur_actuel(self):
        return self.joueurs[self.tour % 2]

    def lock_ui_if_needed(self):
        if not self.sock:
            return
        mon_symbole = 'X' if self.is_host else 'O'
        if (self.tour % 2 == 0 and mon_symbole != 'X') or (self.tour % 2 == 1 and mon_symbole != 'O'):
            self.canvas.unbind("<Button-1>")
        else:
            self.canvas.bind("<Button-1>", self.on_click)

    def network_listener(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                msg = data.decode()
                if msg.startswith('move:'):
                    coords = msg[5:].split('->')
                    depart = tuple(map(int, coords[0].split(',')))
                    arrivee = tuple(map(int, coords[1].split(',')))
                    self.apply_network_move(depart, arrivee)
            except Exception:
                break

    def send_move(self, depart, arrivee):
        if self.sock:
            msg = f"move:{depart[0]},{depart[1]}->{arrivee[0]},{arrivee[1]}".encode()
            self.sock.sendall(msg)

    def update_info_joueur(self):
        # Affiche toujours 'Noir' au premier tour, puis alterne
        if self.tour % 2 == 0:
            couleur = 'Noir'
        else:
            couleur = 'Blanc'
        if self.sock and self.noms_joueurs:
            self.tour_label.config(text=f"Tour de {self.noms_joueurs[self.tour % 2]} ({couleur})")
        else:
            self.tour_label.config(text=f"Tour du Joueur {couleur}")
        pions_x_restants = len(self.pions['X'])
        pions_o_restants = len(self.pions['O'])
        self.pions_restants_label.config(text=f"Pions Restants - Blanc: {pions_x_restants}, Noir: {pions_o_restants}")

    def afficher_plateau(self):
        taille = 50
        self.canvas.delete("all")
        colors = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}
        for i in range(8):
            for j in range(8):
                fill = colors.get(self.plateau.cases[i][j], 'white')
                self.canvas.create_rectangle(j * taille, i * taille, (j + 1) * taille, (i + 1) * taille, fill=fill)
                for symbol, color in [('X', 'black'), ('O', 'white')]:
                    if (i, j) in self.pions[symbol]:
                        self.canvas.create_oval(j * taille + 10, i * taille + 10, (j + 1) * taille - 10, (i + 1) * taille - 10, fill=color)
                if self.selection == (i, j):
                    self.canvas.create_rectangle(j * taille, i * taille, (j + 1) * taille, (i + 1) * taille, outline='blue', width=3)
                if (i, j) in self.coups_possibles:
                    self.canvas.create_oval(j * taille + 20, i * taille + 20, (j + 1) * taille - 20, (i + 1) * taille - 20, fill='lightgreen')

    def on_click(self, event):
        ligne, colonne = event.y // 50, event.x // 50
        joueur, symbole = self.joueur_actuel(), self.joueur_actuel().symbole
        position_cliquee = (ligne, colonne)

        if self.selection is None:
            if position_cliquee in self.pions[symbole]:
                self.selection = position_cliquee
                couleur_depart = self.plateau.cases[self.selection[0]][self.selection[1]]
                self.coups_possibles = self.generer_coups_possibles(self.selection, couleur_depart, symbole)
                self.afficher_plateau()
        else:
            depart, arrivee = self.selection, position_cliquee
            couleur_depart = self.plateau.cases[depart[0]][depart[1]]
            piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pions[s]), None)

            if arrivee in self.coups_possibles:
                if piece_arrivee and self.tour > 0:
                    self.pions[piece_arrivee].discard(arrivee)
                elif piece_arrivee:
                    messagebox.showinfo("Invalide", "Les captures ne sont pas autorisées au premier tour.")
                    return
                self.pions[symbole].discard(depart)
                self.pions[symbole].add(arrivee)
                self.tour += 1
                self.selection = None
                self.coups_possibles = set()
                self.afficher_plateau()
                self.update_info_joueur()
                self.verifier_victoire()
                if self.sock:
                    self.send_move(depart, arrivee)
                self.lock_ui_if_needed()
            else:
                self.selection = None
                self.coups_possibles = set()
                if position_cliquee in self.pions[symbole]:
                    self.selection = position_cliquee
                    couleur_depart = self.plateau.cases[self.selection[0]][self.selection[1]]
                    self.coups_possibles = self.generer_coups_possibles(self.selection, couleur_depart, symbole)
                    self.afficher_plateau()

    def apply_network_move(self, depart, arrivee):
        joueur, symbole = self.joueur_actuel(), self.joueur_actuel().symbole
        piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pions[s]), None)
        if piece_arrivee and self.tour > 0:
            self.pions[piece_arrivee].discard(arrivee)
        self.pions[symbole].discard(depart)
        self.pions[symbole].add(arrivee)
        self.tour += 1
        self.selection = None
        self.coups_possibles = set()
        self.afficher_plateau()
        self.update_info_joueur()
        self.verifier_victoire()
        self.lock_ui_if_needed()

    def generer_coups_possibles(self, depart, couleur, symbole):
        coups = set()
        for i in range(8):
            for j in range(8):
                arrivee = (i, j)
                piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pions[s]), None)
                if piece_arrivee is None or piece_arrivee != symbole:
                    mouvement_valide = (couleur == 'B' and self.est_mouvement_roi(depart, arrivee)) or \
                                       (couleur == 'V' and self.est_mouvement_cavalier(depart, arrivee)) or \
                                       (couleur == 'J' and self.est_mouvement_fou(depart, arrivee)) or \
                                       (couleur == 'R' and self.est_mouvement_tour(depart, arrivee))
                    if mouvement_valide:
                        coups.add(arrivee)
        return coups

    def est_mouvement_roi(self, depart, arrivee):
        dl, dc = abs(arrivee[0] - depart[0]), abs(arrivee[1] - depart[1])
        return dl <= 1 and dc <= 1 and (dl != 0 or dc != 0)

    def est_mouvement_cavalier(self, depart, arrivee):
        dl, dc = abs(arrivee[0] - depart[0]), abs(arrivee[1] - depart[1])
        return (dl == 2 and dc == 1) or (dl == 1 and dc == 2)

    def est_mouvement_fou(self, depart, arrivee):
        if abs(arrivee[0] - depart[0]) != abs(arrivee[1] - depart[1]):
            return False
        sl, sc = (1 if arrivee[i] > depart[i] else -1 for i in range(2))
        l, c = depart[0] + sl, depart[1] + sc
        while (l, c) != arrivee:
            if not (0 <= l < 8 and 0 <= c < 8) or (l, c) in self.pions['X'] or (l, c) in self.pions['O']:
                return False
            if self.plateau.cases[l][c] == 'J':
                return (l, c) == arrivee
            l += sl
            c += sc
        return self.plateau.cases[arrivee[0]][arrivee[1]] == 'J'

    def est_mouvement_tour(self, depart, arrivee):
        if depart[0] != arrivee[0] and depart[1] != arrivee[1]:
            return False
        sl, sc = (1 if arrivee[i] > depart[i] else -1 if arrivee[i] < depart[i] else 0 for i in range(2))
        l, c = depart[0] + sl, depart[1] + sc
        while (l, c) != arrivee:
            if not (0 <= l < 8 and 0 <= c < 8) or (l, c) in self.pions['X'] or (l, c) in self.pions['O']:
                return False
            if self.plateau.cases[l][c] == 'R':
                return (l, c) == arrivee
            l += sl
            c += sc
        return self.plateau.cases[arrivee[0]][arrivee[1]] == 'R'

    def verifier_victoire(self):
        joueur = self.joueur_actuel()
        ligne_victoire = 7 if joueur.symbole == 'X' else 0
        if any(p[0] == ligne_victoire for p in self.pions[joueur.symbole]):
            self.pause_timer()
            messagebox.showinfo("Victoire!", f"Joueur {joueur.nom} ({'Blanc' if joueur.symbole == 'X' else 'Noir'}) a atteint la ligne adverse et a gagné!")
            self.reprendre_timer()
            self.rejouer()
        elif not self.pions['O' if joueur.symbole == 'X' else 'X']:
            self.pause_timer()
            messagebox.showinfo("Victoire!", f"Joueur {joueur.nom} ({'Blanc' if joueur.symbole == 'X' else 'Noir'}) a gagné par capture!")
            self.reprendre_timer()
            self.rejouer()

    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running or not self.root.winfo_exists():
            return
        minutes, seconds = divmod(self.timer_seconds, 60)
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.timer_seconds += 1
        self.root.after(1000, self.update_timer)

    def pause_timer(self):
        self.timer_running = False

    def reprendre_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def retour_menu(self):
        self.timer_running = False
        self.root.destroy()
        subprocess.Popen([sys.executable, "menu_gui.py"])

    def aide_popup(self):
        self.pause_timer()
        aide = tk.Toplevel(self.root)
        aide.title("Règles du jeu")
        aide.geometry("400x400")
        aide.configure(bg="#f0f4f8")

        tk.Label(aide, text="Règles de Katarenga", font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)
        text_widget = tk.Text(aide, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", get_regles("katarenga"))
        text_widget.configure(state="disabled")

        def on_close():
            self.reprendre_timer()
            aide.destroy()

        aide.protocol("WM_DELETE_WINDOW", on_close)

    def rejouer(self):
        self.timer_running = False
        self.root.destroy()
        from plateau_builder import lancer_plateau_builder
        lancer_plateau_builder("katarenga", self.mode)

def lancer_jeu_reseau(root, is_host, player_name_blanc, player_name_noir, sock):
    # Synchronisation des noms
    if is_host:
        sock.sendall(f"nom:{player_name_blanc}".encode())
        data = sock.recv(4096)
        player_name_noir = data.decode()[4:]
    else:
        data = sock.recv(4096)
        player_name_blanc = data.decode()[4:]
        sock.sendall(f"nom:{player_name_noir}".encode())
    joueurs = [Joueur(player_name_blanc, 'X'), Joueur(player_name_noir, 'O')]
    plateau = Plateau()
    jeu = JeuKatarenga(plateau, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=[player_name_blanc, player_name_noir], root=root)
    jeu.jouer()

# Pour test indépendant
if __name__ == '__main__':
    plateau = Plateau()
    joueurs = [Joueur("Joueur 1", 'O'), Joueur("Joueur 2", 'X')]
    jeu = JeuKatarenga(plateau, joueurs)
    jeu.jouer()
