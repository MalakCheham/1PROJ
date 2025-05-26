# Remplacer toute la logique Tkinter par Pygame dans chaque fichier de jeux_gui (congress.py, isolation.py, katarenga.py, plateau_builder.py, plateau_gui.py, quadrant_editor_live.py déjà fait).
# Pour chaque fichier, créer une classe principale qui gère l'affichage, les boutons, la grille, etc. avec Pygame.
# Utiliser pygame.font pour les textes, pygame.draw pour les boutons et la grille, et gérer les événements souris/clavier.

import tkinter as tk
import threading
import os
import subprocess
import sys

from core.mouvement import est_mouvement_roi, est_mouvement_cavalier, est_mouvement_fou, est_mouvement_tour
from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles
from tkinter import messagebox
from PIL import Image, ImageTk
from core.musique import jouer_musique
jouer_musique()

class JeuIsolation:
    def __init__(self, plateau, joueurs, mode="1v1", sock=None, is_host=False, noms_joueurs=None, root=None):
        # Nettoyer le root si fourni
        if root:
            for widget in root.winfo_children():
                widget.destroy()
        self.plateau = plateau
        self.joueurs = joueurs
        self.mode = mode
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.pions = {'X': set(), 'O': set()}  # Ajout pour gestion des pions posés
        self.sock = sock
        self.is_host = is_host
        self.noms_joueurs = noms_joueurs or ["Joueur Blanc", "Joueur Noir"]
        self.reseau = sock is not None
        self.root = root if root else tk.Tk()
        self.root.title("Isolation")
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
                    pos = tuple(map(int, msg[5:].split(',')))
                    self.apply_network_move(pos)
            except Exception:
                break

    def send_move(self, position):
        if self.sock:
            msg = f"move:{position[0]},{position[1]}".encode()
            self.sock.sendall(msg)

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

    def update_info_joueur(self):
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
                # Affichage des cases non disponibles (ni vides ni posables)
                if self.plateau.cases[i][j] not in ['X', 'O'] and not self.case_non_en_prise((i, j)):
                    # Tiret noir horizontal au centre de la case
                    y = i*taille + taille//2
                    self.canvas.create_line(j*taille+10, y, (j+1)*taille-10, y, fill='black', width=3)
        for symbole in ['X', 'O']:
            for (x, y) in self.pions[symbole]:
                color = "black" if symbole == "X" else "white"
                self.canvas.create_oval(y*taille+10, x*taille+10, (y+1)*taille-10, (x+1)*taille-10, fill=color)

    def on_click(self, event):
        ligne, colonne = event.y // 50, event.x // 50
        # Vérifie que le clic est dans les limites du plateau
        if not (0 <= ligne < 8 and 0 <= colonne < 8):
            return
        joueur = self.joueur_actuel()
        symbole = joueur.symbole
        position = (ligne, colonne)
        # Vérifie que la case est vide et non "en prise"
        if self.plateau.cases[ligne][colonne] in ['X', 'O']:
            return
        if not self.case_non_en_prise(position):
            messagebox.showinfo("Invalide", "La case est en prise par un pion déjà posé.")
            return
        self.pions[symbole].add(position)
        # Ne pas modifier la couleur de la case, elle reste d'origine
        self.tour += 1
        self.afficher_plateau()
        self.update_info_joueur()
        # Appeler verifier_victoire APRÈS l'incrémentation du tour
        self.verifier_victoire()
        if self.reseau:
            self.send_move(position)
            self.lock_ui_if_needed()

    def apply_network_move(self, position):
        joueur = self.joueur_actuel()
        symbole = joueur.symbole
        self.pions[symbole].add(position)
        # Ne pas modifier la couleur de la case, elle reste d'origine
        self.tour += 1
        self.afficher_plateau()
        self.update_info_joueur()
        self.verifier_victoire()
        if self.reseau:
            self.lock_ui_if_needed()

    def case_non_en_prise(self, pos):
        # Une case est "en prise" si un pion adverse pourrait la capturer selon la couleur de la case
        for symbole in ['X', 'O']:
            for pion in self.pions[symbole]:
                couleur = self.plateau.cases[pion[0]][pion[1]]
                coups = self.generer_coups_possibles(pion, couleur, symbole)
                if pos in coups:
                    return False
        return True

    def generer_coups_possibles(self, depart, couleur, symbole):
        coups = set()
        for i in range(8):
            for j in range(8):
                arrivee = (i, j)
                piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pions[s]), None)
                if piece_arrivee is None or piece_arrivee != symbole:
                    mouvement_valide = (couleur == 'B' and est_mouvement_roi(depart, arrivee)) or \
                                       (couleur == 'V' and est_mouvement_cavalier(depart, arrivee)) or \
                                       (couleur == 'J' and est_mouvement_fou(depart, arrivee, self.plateau, self.pions)) or \
                                       (couleur == 'R' and est_mouvement_tour(depart, arrivee, self.plateau, self.pions))
                    if mouvement_valide:
                        coups.add(arrivee)
        return coups

    def position_valide(self, symbole, pos):
        x, y = self.positions[symbole]
        dx, dy = abs(pos[0] - x), abs(pos[1] - y)
        if (0 <= pos[0] < 8 and 0 <= pos[1] < 8 and
            self.plateau.cases[pos[0]][pos[1]] not in ['X', 'O'] and
            (dx <= 1 and dy <= 1) and (dx + dy) != 0):
            return True
        return False

    def verifier_victoire(self):
        # Le vainqueur est le dernier joueur à pouvoir poser un pion
        joueur_actuel = self.joueur_actuel()
        symbole = joueur_actuel.symbole
        coups_possibles = False
        for i in range(8):
            for j in range(8):
                if self.plateau.cases[i][j] in ['X', 'O']:
                    continue
                if self.case_non_en_prise((i, j)):
                    coups_possibles = True
                    break
            if coups_possibles:
                break
        if not coups_possibles:
            self.pause_timer()
            # Le vainqueur est le joueur précédent (dernier à avoir joué)
            vainqueur_index = (self.tour - 1) % 2
            joueur = self.joueurs[vainqueur_index]
            couleur = 'Blanc' if joueur.symbole == 'X' else 'Noir'
            nom = getattr(joueur, 'nom', str(joueur))
            messagebox.showinfo("Victoire", f"Joueur {nom} ({couleur}) a gagné !")
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

        tk.Label(aide, text="Règles de Isolation", font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)
        text_widget = tk.Text(aide, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", get_regles("isolation"))
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
        lancer_plateau_builder("isolation", self.mode)

    def est_mouvement_roi(self, depart, arrivee):
        dl, dc = abs(arrivee[0] - depart[0]), abs(arrivee[1] - depart[1])
        return dl <= 1 and dc <= 1 and (dl != 0 or dc != 0)

    def est_mouvement_cavalier(self, depart, arrivee):
        dl, dc = abs(arrivee[0] - depart[0]), abs(arrivee[1] - depart[1])
        return (dl == 2 and dc == 1) or (dl == 1 and dc == 2)

    def est_mouvement_fou(self, depart, arrivee):
        if abs(arrivee[0] - depart[0]) != abs(arrivee[1] - depart[1]):
            return False
        sl = 1 if arrivee[0] > depart[0] else -1
        sc = 1 if arrivee[1] > depart[1] else -1
        l, c = depart[0] + sl, depart[1] + sc
        while (l, c) != arrivee:
            if not (0 <= l < 8 and 0 <= c < 8):
                return False
            if (l, c) in self.pions['X'] or (l, c) in self.pions['O']:
                return False
            if self.plateau.cases[l][c] == 'J':
                return (l, c) == arrivee
            l += sl
            c += sc
        return True

    def est_mouvement_tour(self, depart, arrivee):
        if depart[0] != arrivee[0] and depart[1] != arrivee[1]:
            return False
        sl = 0 if depart[0] == arrivee[0] else (1 if arrivee[0] > depart[0] else -1)
        sc = 0 if depart[1] == arrivee[1] else (1 if arrivee[1] > depart[1] else -1)
        l, c = depart[0] + sl, depart[1] + sc
        while (l, c) != arrivee:
            if not (0 <= l < 8 and 0 <= c < 8):
                return False
            if (l, c) in self.pions['X'] or (l, c) in self.pions['O']:
                return False
            if self.plateau.cases[l][c] == 'R':
                return (l, c) == arrivee
            l += sl
            c += sc
        return True

def plateau_to_str(plateau):
    return '\n'.join(''.join(row) for row in plateau.cases)
def positions_to_str(positions):
    return f"{positions['X'][0]},{positions['X'][1]};{positions['O'][0]},{positions['O'][1]}"
def str_to_plateau(s):
    lines = s.strip().split('\n')
    cases = [list(line) for line in lines]
    from core.plateau import Plateau
    plateau = Plateau()
    plateau.cases = cases
    return plateau
def str_to_positions(s):
    parts = s.strip().split(';')
    pos = {}
    pos['X'] = tuple(map(int, parts[0].split(',')))
    pos['O'] = tuple(map(int, parts[1].split(',')))
    return pos

def lancer_jeu_reseau(root, is_host, player_name_blanc, player_name_noir, sock, plateau=None, pions=None, wait_win=None):
    import threading
    if is_host:
        noms = [player_name_blanc, player_name_noir]
        sock.sendall(f"noms:{noms[0]},{noms[1]}".encode())
        # Générer ou utiliser le plateau/positions
        if plateau is None or pions is None:
            from plateau_builder import creer_plateau
            plateau, _ = creer_plateau()
            positions = {'X': (0, 0), 'O': (7, 7)}
        else:
            positions = {'X': (0, 0), 'O': (7, 7)}
        plateau_str = plateau_to_str(plateau)
        positions_str = positions_to_str(positions)
        sock.sendall((plateau_str + '\nENDPLATEAU\n').encode())
        sock.sendall((positions_str + '\nENDPOSITIONS\n').encode())
        joueurs = [Joueur(noms[0], 'X'), Joueur(noms[1], 'O')]
        jeu = JeuIsolation(plateau, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=noms)
        jeu.root = root
        jeu.positions = {'X': (0, 0), 'O': (7, 7)}
        jeu.afficher_plateau()
        jeu.jouer()
    else:
        def client_receive_and_start():
            data = sock.recv(4096)
            msg = data.decode()
            noms = msg[5:].split(',')
            def recv_until(sock, end_marker):
                data = b''
                while not data.decode(errors='ignore').endswith(end_marker):
                    data += sock.recv(1024)
                return data.decode().replace(end_marker, '').strip()
            plateau_str = recv_until(sock, '\nENDPLATEAU\n')
            positions_str = recv_until(sock, '\nENDPOSITIONS\n')
            plateau_local = str_to_plateau(plateau_str)
            positions_local = str_to_positions(positions_str)
            def start_game():
                if wait_win is not None:
                    wait_win.destroy()
                joueurs = [Joueur(noms[0], 'X'), Joueur(noms[1], 'O')]
                jeu = JeuIsolation(plateau_local, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=noms)
                jeu.root = root
                jeu.positions = positions_local
                jeu.afficher_plateau()
                jeu.jouer()
            root.after(0, start_game)
        threading.Thread(target=client_receive_and_start, daemon=True).start()

# Test indépendant
if __name__ == '__main__':
    plateau = Plateau()
    joueurs = [Joueur("Joueur 1", 'O'), Joueur("Joueur 2", 'X')]
    jeu = JeuIsolation(plateau, joueurs)
    jeu.jouer()
