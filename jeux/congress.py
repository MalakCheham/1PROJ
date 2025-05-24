import tkinter as tk
import subprocess
import sys
import os
import threading
import random

from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles
from tkinter import messagebox
from PIL import Image, ImageTk

class JeuCongress:
    def __init__(self, plateau, joueurs, mode="1v1", sock=None, is_host=False, noms_joueurs=None, root=None):
        # Nettoyer le root si fourni
        if root:
            for widget in root.winfo_children():
                widget.destroy()
        self.plateau = plateau
        self.joueurs = joueurs
        self.mode = mode
        self.sock = sock
        self.is_host = is_host
        self.noms_joueurs = noms_joueurs or ["Joueur Blanc", "Joueur Noir"]
        self.reseau = sock is not None
        # Placement initial demandé par l'utilisateur
        self.pions = {
            'X': set(),
            'O': set()
        }
        
        self.pions['X'].update([(0,1), (0,4)])
        self.pions['O'].update([(0,3), (0,6)])

        self.pions['O'].add((1,0))
        self.pions['X'].add((1,7))

        self.pions['X'].add((3,0))
        self.pions['O'].add((3,7))

        self.pions['O'].add((4,0))
        self.pions['X'].add((4,7))

        self.pions['X'].add((6,0))
        self.pions['O'].add((6,7))

        self.pions['O'].update([(7,1), (7,4)])
        self.pions['X'].update([(7,3), (7,6)])
        
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.selection = None
        self.root = root if root else tk.Tk()
        self.root.title("Congress")
        self.root.configure(bg="#e6f2ff")

        self.top_frame = tk.Frame(self.root, bg="#e6f2ff")
        self.top_frame.pack(fill="x", pady=5, padx=5)

        self.tour_label = tk.Label(self.top_frame, text="", font=("Helvetica", 12, "bold"), bg="#e6f2ff", fg="#003366")
        self.tour_label.pack(side="top")

        self.timer_label = tk.Label(self.top_frame, text="00:00", font=("Helvetica", 12, "bold"), bg="#e6f2ff", fg="#003366")
        self.timer_label.pack(side="top")

        self.canvas = tk.Canvas(self.root, width=400, height=400)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.load_and_pack_button("en-arriere.png", "<", self.top_frame, self.retour_menu, "left")
        self.load_and_pack_button("point-dinterrogation.png", "?", self.top_frame, self.aide_popup, "right")
        self.load_and_pack_button("fleche-pivotante-vers-la-gauche.png", "Rejouer", self.root, self.rejouer, "bottom", pady=10)

        self.afficher_plateau()
        self.update_info_joueur()
        self.start_timer()
        if self.reseau:
            self.lock_ui_if_needed()
            threading.Thread(target=self.network_listener, daemon=True).start()
        else:
            self.canvas.bind("<Button-1>", self.on_click)

    def lock_ui_if_needed(self):
        if not self.reseau:
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
                    from_pos = tuple(map(int, coords[0].split(',')))
                    to_pos = tuple(map(int, coords[1].split(',')))
                    self.apply_network_move(from_pos, to_pos)
            except Exception:
                break

    def send_move(self, from_pos, to_pos):
        if self.sock:
            msg = f"move:{from_pos[0]},{from_pos[1]}->{to_pos[0]},{to_pos[1]}".encode()
            self.sock.sendall(msg)

    def jouer(self):
        if self.mode == "ia" and self.tour % 2 == 1:
            self.root.after(500, self.jouer_coup_ia)
        self.root.mainloop()

    def jouer_coup_ia(self):
        symbole = self.joueurs[self.tour % 2].symbole
        # Sélectionne tous les pions IA qui ont au moins un coup possible
        pions_possibles = []
        for pion in self.pions[symbole]:
            couleur = self.plateau.cases[pion[0]][pion[1]]
            coups = self.generer_coups_possibles(pion, couleur, symbole)
            if coups:
                pions_possibles.append((pion, list(coups)))
        if not pions_possibles:
            return  # Aucun coup possible
        pion, coups = random.choice(pions_possibles)
        arrivee = random.choice(coups)
        self.pions[symbole].remove(pion)
        self.pions[symbole].add(arrivee)
        self.selection = None
        self.coups_possibles = set()
        self.tour += 1
        self.update_info_joueur()
        self.afficher_plateau()
        self.verifier_victoire()
        # Si c'est encore à l'IA de jouer (ex: l'humain a perdu), rejouer
        if self.mode == "ia" and self.tour % 2 == 1:
            self.root.after(500, self.jouer_coup_ia)

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

    def update_info_joueur(self):
        if self.mode == "ia":
            if self.tour % 2 == 0:
                self.tour_label.config(text="Tour du Joueur Noir (Humain)")
            else:
                self.tour_label.config(text="Tour du Joueur Blanc (IA)")
        else:
            joueur = self.joueur_actuel()
            # Affiche toujours 'Noir' au premier tour, puis alterne
            if self.tour % 2 == 0:
                couleur = 'Noir'
            else:
                couleur = 'Blanc'
            if self.reseau and self.noms_joueurs:
                self.tour_label.config(text=f"Tour de {self.noms_joueurs[self.tour % 2]} ({couleur})")
            else:
                self.tour_label.config(text=f"Tour du Joueur {couleur}")

    def afficher_plateau(self):
        self.canvas.delete("all")
        taille = 50
        couleurs = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}

        for i in range(8):
            for j in range(8):
                couleur = self.plateau.cases[i][j]
                fill = couleurs.get(couleur, 'white')
                self.canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, (i+1)*taille, fill=fill)
                # Affichage du cadre de sélection
                if self.selection == (i, j):
                    self.canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, (i+1)*taille, outline='blue', width=3)
                # Affichage des mouvements possibles
                if hasattr(self, 'coups_possibles') and (i, j) in getattr(self, 'coups_possibles', set()):
                    self.canvas.create_oval(j*taille+20, i*taille+20, (j+1)*taille-20, (i+1)*taille-20, fill='lightgreen')
        for symbole, color in [('X', 'black'), ('O', 'white')]:
            for (i, j) in self.pions[symbole]:
                self.canvas.create_oval(j*taille+10, i*taille+10, (j+1)*taille-10, (i+1)*taille-10, fill=color)

    def on_click(self, event):
        if self.mode == "ia" and self.tour % 2 == 1:
            return  # Bloque l'interaction humaine pendant le tour IA
        ligne, colonne = event.y // 50, event.x // 50
        joueur, symbole = self.joueur_actuel(), self.joueur_actuel().symbole
        position = (ligne, colonne)
        if self.selection is None:
            if position in self.pions[symbole]:
                self.selection = position
                couleur_depart = self.plateau.cases[self.selection[0]][self.selection[1]]
                self.coups_possibles = self.generer_coups_possibles(self.selection, couleur_depart, symbole)
                self.afficher_plateau()
        else:
            if position in getattr(self, 'coups_possibles', set()):
                from_pos = self.selection
                self.pions[symbole].remove(self.selection)
                self.pions[symbole].add(position)
                self.selection = None
                self.coups_possibles = set()
                self.tour += 1
                self.update_info_joueur()
                self.afficher_plateau()
                self.verifier_victoire()
                if self.reseau:
                    self.send_move(from_pos, position)
                    self.lock_ui_if_needed()
            else:
                self.selection = None
                self.coups_possibles = set()
                self.afficher_plateau()

    def apply_network_move(self, from_pos, to_pos):
        joueur, symbole = self.joueur_actuel(), self.joueur_actuel().symbole
        self.pions[symbole].remove(from_pos)
        self.pions[symbole].add(to_pos)
        self.selection = None
        self.coups_possibles = set()
        self.tour += 1
        self.update_info_joueur()
        self.afficher_plateau()
        self.verifier_victoire()
        if self.reseau:
            self.lock_ui_if_needed()

    def verifier_victoire(self):
        # Le but : tous les pions d'un joueur forment un bloc connexe orthogonalement
        joueur = self.joueur_actuel()
        symbole = joueur.symbole
        positions = self.pions[symbole]
        if not positions:
            return
        # Parcours en largeur pour vérifier la connexité
        from collections import deque
        visited = set()
        queue = deque([next(iter(positions))])
        while queue:
            pos = queue.popleft()
            if pos in visited:
                continue
            visited.add(pos)
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                voisin = (pos[0]+dx, pos[1]+dy)
                if voisin in positions and voisin not in visited:
                    queue.append(voisin)
        if len(visited) == len(positions):
            self.pause_timer()
            couleur = 'Blanc' if joueur.symbole == 'X' else 'Noir'
            messagebox.showinfo("Victoire", f"Joueur {joueur.nom} ({couleur}) a gagné !")
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
        self.timer_id = self.root.after(1000, self.update_timer)

    def pause_timer(self):
        self.timer_running = False

    def reprendre_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def aide_popup(self):
        self.pause_timer()
        aide = tk.Toplevel(self.root)
        aide.title("Règles du jeu")
        aide.geometry("400x400")
        aide.configure(bg="#f0f4f8")

        tk.Label(aide, text="Règles de Congress", font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)
        text_widget = tk.Text(aide, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", get_regles("congress"))
        text_widget.configure(state="disabled")

        def on_close():
            self.reprendre_timer()
            aide.destroy()

        aide.protocol("WM_DELETE_WINDOW", on_close)

    def retour_menu(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        self.root.destroy()
        subprocess.Popen([sys.executable, "menu_gui.py"])

    def rejouer(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        self.root.destroy()
        from plateau_builder import lancer_plateau_builder
        lancer_plateau_builder("congress", self.mode)

    def generer_coups_possibles(self, depart, couleur, symbole):
        coups = set()
        for i in range(8):
            for j in range(8):
                arrivee = (i, j)
                piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pions[s]), None)
                if piece_arrivee is None:
                    mouvement_valide = (
                        couleur == 'B' and self.est_mouvement_roi(depart, arrivee)
                        or couleur == 'V' and self.est_mouvement_cavalier(depart, arrivee)
                        or couleur == 'J' and self.est_mouvement_fou(depart, arrivee)
                        or couleur == 'R' and self.est_mouvement_tour(depart, arrivee)
                    )
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
# Pour test indépendant
if __name__ == '__main__':
    plateau = Plateau()
    joueurs = [Joueur("Joueur 1", 'O'), Joueur("Joueur 2", 'X')]
    jeu = JeuCongress(plateau, joueurs)
    jeu.jouer()
