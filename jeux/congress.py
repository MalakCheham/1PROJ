import tkinter as tk
import subprocess
import sys
import os
import threading

from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles
from tkinter import messagebox
from PIL import Image, ImageTk

class JeuCongress:
    def __init__(self, plateau, joueurs, mode="1v1", sock=None, is_host=False, noms_joueurs=None):
        self.plateau = plateau
        self.joueurs = joueurs
        self.mode = mode
        self.sock = sock
        self.is_host = is_host
        self.noms_joueurs = noms_joueurs or [joueur.nom for joueur in joueurs]
        self.reseau = sock is not None
        self.pions = {
            'X': {(0, 3), (0, 4), (1, 3), (1, 4)},
            'O': {(6, 3), (6, 4), (7, 3), (7, 4)}
        }
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.selection = None

        self.root = tk.Tk()
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

    def lock_ui_if_needed(self):
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
        if self.reseau and self.noms_joueurs:
            joueur = self.joueur_actuel()
            self.tour_label.config(text=f"Tour de {self.noms_joueurs[self.tour % 2]}")
        else:
            joueur = self.joueur_actuel()
            self.tour_label.config(text=f"Tour du Joueur {joueur.id + 1}")

    def afficher_plateau(self):
        self.canvas.delete("all")
        taille = 50
        couleurs = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}

        for i in range(8):
            for j in range(8):
                couleur = self.plateau.cases[i][j]
                fill = couleurs.get(couleur, 'white')
                self.canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, (i+1)*taille, fill=fill)

                for symbole, color in [('X', 'black'), ('O', 'white')]:
                    if (i, j) in self.pions[symbole]:
                        self.canvas.create_oval(j*taille+10, i*taille+10, (j+1)*taille-10, (i+1)*taille-10, fill=color)

    def on_click(self, event):
        ligne, colonne = event.y // 50, event.x // 50
        joueur, symbole = self.joueur_actuel(), self.joueur_actuel().symbole
        position = (ligne, colonne)
        if self.selection is None:
            if position in self.pions[symbole]:
                self.selection = position
        else:
            if position not in self.pions['X'] and position not in self.pions['O']:
                from_pos = self.selection
                self.pions[symbole].remove(self.selection)
                self.pions[symbole].add(position)
                self.selection = None
                self.tour += 1
                self.update_info_joueur()
                self.afficher_plateau()
                self.verifier_victoire()
                if self.reseau:
                    self.send_move(from_pos, position)
                    self.lock_ui_if_needed()
            else:
                self.selection = None

    def apply_network_move(self, from_pos, to_pos):
        joueur, symbole = self.joueur_actuel(), self.joueur_actuel().symbole
        self.pions[symbole].remove(from_pos)
        self.pions[symbole].add(to_pos)
        self.selection = None
        self.tour += 1
        self.update_info_joueur()
        self.afficher_plateau()
        self.verifier_victoire()
        if self.reseau:
            self.lock_ui_if_needed()

    def verifier_victoire(self):
        joueur = self.joueur_actuel()
        symbole = joueur.symbole
        positions = self.pions[symbole]
        lignes = [pos[0] for pos in positions]
        colonnes = [pos[1] for pos in positions]
        if max(lignes) - min(lignes) <= 1 and max(colonnes) - min(colonnes) <= 1:
            messagebox.showinfo("Victoire", f"Joueur {joueur.id + 1} a gagné !")
            self.rejouer()

    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
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
        self.root.destroy()
        subprocess.Popen([sys.executable, "menu_gui.py"])

    def rejouer(self):
        self.root.destroy()
        from plateau_builder import lancer_plateau_builder
        lancer_plateau_builder("congress", self.mode)

def lancer_jeu_reseau(sock, nom_local, nom_distant, is_host):
    # Synchronisation des noms
    if is_host:
        noms = [nom_local, nom_distant]
        sock.sendall(f"noms:{noms[0]},{noms[1]}".encode())
    else:
        data = sock.recv(4096)
        msg = data.decode()
        noms = msg[5:].split(',')
    joueurs = [Joueur(noms[0], symbole='X', id=0), Joueur(noms[1], symbole='O', id=1)]
    plateau = Plateau()
    jeu = JeuCongress(plateau, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=noms)
    jeu.jouer()
# Pour test indépendant
if __name__ == '__main__':
    plateau = Plateau()
    joueurs = [Joueur("Joueur 1"), Joueur("Joueur 2")]
    jeu = JeuCongress(plateau, joueurs)
    jeu.jouer()
