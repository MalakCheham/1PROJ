import tkinter as tk
import threading
import os
import subprocess
import sys

from core.mouvement import est_mouvement_roi, est_mouvement_cavalier, est_mouvement_fou, est_mouvement_tour, generer_coups_possibles
from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles
from tkinter import messagebox
from PIL import Image, ImageTk
from core.musique import jouer_musique
from core.network.utils import plateau_to_str, pions_to_str, str_to_plateau, str_to_pions
jouer_musique()

class JeuIsolation:
    def __init__(self, plateau, joueurs, mode="1v1", sock=None, is_host=False, noms_joueurs=None, root=None):
        if root:
            for widget in root.winfo_children():
                widget.destroy()
        self.plateau = plateau
        self.joueurs = joueurs
        self.mode = mode
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.pions = {'X': set(), 'O': set()}
        self.sock = sock
        self.is_host = is_host
        self.noms_joueurs = noms_joueurs or ["Joueur Blanc", "Joueur Noir"]
        self.reseau = sock is not None
        self.root = root if root else tk.Tk()
        self.root.title("Isolation")
        self.root.configure(bg="#f0f0f0")
        self.setup_ui()
        self.update_info_joueur()
        self.start_timer()
        if self.reseau:
            self.lock_ui_if_needed()
            threading.Thread(target=self.network_listener, daemon=True).start()
        else:
            self.canvas.bind("<Button-1>", self.on_click)

    def setup_ui(self):
        from core.langues import traduire
        header_bg = "#e0e0e0"
        self.root.configure(bg="#f0f0f0")
        header = tk.Frame(self.root, bg=header_bg, height=80)
        header.pack(side="top", fill="x")
        bienvenue = tk.Label(header, text="Isolation", font=("Arial", 22, "bold"), bg=header_bg, fg="#5b7fce")
        bienvenue.pack(side="left", padx=32, pady=18)
        img = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
        icon = ImageTk.PhotoImage(img, master=self.root)
        self.icon = icon
        btn_icon = tk.Button(header, image=self.icon, bg=header_bg, bd=0, relief="flat", cursor="hand2", activebackground=header_bg, highlightthickness=0)
        btn_icon.image = self.icon
        btn_icon.pack(side="right", padx=28, pady=12)
        def show_logout_menu(event):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label=traduire("a_propos"), command=lambda: messagebox.showinfo(traduire("a_propos"), traduire("a_propos_texte")))
            menu.add_command(label=traduire("credits"), command=lambda: messagebox.showinfo(traduire("credits"), traduire("credits_texte")))
            menu.add_separator()
            def go_to_login():
                import login
                try:
                    current_volume = self.root.volume_var.get()
                except AttributeError:
                    try:
                        from core.musique import SoundBar
                        current_volume = SoundBar.last_volume
                    except Exception:
                        current_volume = None
                for w in self.root.winfo_children():
                    w.destroy()
                login.show_login(self.root, volume=current_volume)
            menu.add_command(label=traduire("se_deconnecter"), command=go_to_login)
            menu.add_command(label=traduire("fermer"), command=self.root.quit)
            menu.tk_popup(event.x_root, event.y_root)
        btn_icon.bind("<Button-1>", show_logout_menu)
        """barre de soon"""
        from core.musique import SoundBar, regler_volume
        from core.parametres import LanguageSelector
        initial_volume = 50
        if hasattr(self.root, 'volume_var'):
            try:
                initial_volume = self.root.volume_var.get()
            except Exception:
                pass
        else:
            self.root.volume_var = tk.IntVar(value=initial_volume)
        soundbar = SoundBar(self.root, volume_var=self.root.volume_var)
        regler_volume(self.root.volume_var.get())
        soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)
        def on_language_changed(new_lang):
            import importlib
            import core.langues
            importlib.reload(core.langues)
            self.redraw_ui_only()
        lang_selector = LanguageSelector(self.root, assets_dir="assets", callback=on_language_changed)
        lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(pady=10, expand=True, fill="both")
        """Bouton de retour"""
        left_frame = tk.Frame(main_frame, bg="#f0f0f0")
        left_frame.pack(side="left", fill="y", padx=(18, 0), pady=0)
        img_retour = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
        if hasattr(self.root, 'tk'):
            icon_retour = ImageTk.PhotoImage(img_retour, master=self.root)
        else:
            icon_retour = ImageTk.PhotoImage(img_retour)
        self.icon_retour = icon_retour
        def retour_config():
            import config_gui
            try:
                current_volume = self.root.volume_var.get()
            except Exception:
                current_volume = None
            for w in self.root.winfo_children():
                w.destroy()
            try:
                config_gui.afficher_interface_choix(self.root, volume=current_volume)
            except TypeError:
                config_gui.afficher_interface_choix(self.root)
        btn_retour = tk.Button(left_frame, image=self.icon_retour, command=retour_config, bg="#f0f0f0", bd=0, relief="flat", cursor="hand2", activebackground="#f0f0f0", highlightthickness=0)
        btn_retour.image = icon_retour
        btn_retour.pack(side="top", expand=True, anchor="center", pady=0)
        # Zone centrale
        self.tour_label = tk.Label(main_frame, text="", font=("Helvetica", 13, "bold"), bg="#f0f0f0", fg="#003366")
        self.tour_label.place(relx=0.50, rely=0.08, anchor="center")
        self.timer_label = tk.Label(main_frame, text="00:00", font=("Helvetica", 13, "bold"), bg="#f0f0f0", fg="#003366")
        self.timer_label.place(relx=0.50, rely=0.15, anchor="center")
        self.canvas = tk.Canvas(main_frame, width=400, height=400, bg="#f0f0f0", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.55, anchor="center")
        self.load_and_pack_button("point-dinterrogation.png", "?", self.root, self.aide_popup, "bottom", pady=10)
        self.load_and_pack_button("fleche-pivotante-vers-la-gauche.png", "Rejouer", self.root, self.rejouer, "bottom", pady=10)
        self.update_info_joueur()
        self.afficher_plateau()
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.update_idletasks()
        self.root.update()

    def redraw_ui_only(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.update_info_joueur()
        self.afficher_plateau()

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
        from core.langues import traduire
        couleur = 'noir' if self.tour % 2 == 0 else 'blanc'
        self.tour_label.config(text=f"{traduire('tour_de')} ({traduire(couleur)})")

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
        # Vérifie que la case est déjà occupée par un pion
        if position in self.pions['X'] or position in self.pions['O']:
            from core.langues import traduire
            messagebox.showinfo(traduire("invalide"), traduire("case_occupee"))
            return
        # Vérifie que la case est vide et non "en prise"
        if self.plateau.cases[ligne][colonne] in ['X', 'O']:
            return
        from core.langues import traduire
        if not self.case_non_en_prise(position):
            messagebox.showinfo(traduire("invalide"), traduire("case_bloquee"))
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
        # Vérifie que la case est déjà occupée par un pion
        if position in self.pions['X'] or position in self.pions['O']:
            return  # Ignore le coup réseau invalide
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
        return generer_coups_possibles(depart, couleur, symbole, self.plateau, self.pions, capture=False)

    def position_valide(self, symbole, pos):
        x, y = self.positions[symbole]
        dx, dy = abs(pos[0] - x), abs(pos[1] - y)
        if (0 <= pos[0] < 8 and 0 <= pos[1] < 8 and
            self.plateau.cases[pos[0]][pos[1]] not in ['X', 'O'] and
            (dx <= 1 and dy <= 1) and (dx + dy) != 0):
            return True
        return False

    def verifier_victoire(self):
        def joueur_peut_jouer(symbole):
            for i in range(8):
                for j in range(8):
                    if self.plateau.cases[i][j] in ['X', 'O']:
                        continue
                    if (i, j) in self.pions['X'] or (i, j) in self.pions['O']:
                        continue
                    if self.case_non_en_prise((i, j)):
                        return True
            return False
        if not joueur_peut_jouer('X') and not joueur_peut_jouer('O'):
            self.pause_timer()
            joueur = self.joueurs[(self.tour) % 2]
            couleur = 'Blanc' if joueur.symbole == 'X' else 'Noir'
            from core.langues import traduire
            messagebox.showinfo(traduire("victoire"), f"{traduire('joueur')} ({traduire(couleur.lower())}) {traduire('a_gagne')} !")
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
        from core.langues import traduire
        self.pause_timer()
        aide = tk.Toplevel(self.root)
        aide.title(traduire("regles_du_jeu"))
        aide.geometry("400x400")
        aide.configure(bg="#f0f4f8")
        tk.Label(aide, text=traduire("regles_isolation"), font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)
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
        # Réinitialise uniquement les pions
        self.pions = {'X': set(), 'O': set()}
        self.tour = 0
        self.timer_seconds = 0
        self.selection = None if hasattr(self, 'selection') else None
        self.coups_possibles = set() if hasattr(self, 'coups_possibles') else set()
        self.redraw_ui_only()
        self.start_timer()

def lancer_jeu_reseau(root, is_host, player_name_blanc, player_name_noir, sock, plateau=None, pions=None, wait_win=None):
    import threading
    from core.joueur import Joueur
    from core.network.utils import plateau_to_str, pions_to_str, str_to_plateau, str_to_pions
    if is_host:
        sock.sendall(f"nom:{player_name_blanc}".encode())
        data = sock.recv(4096)
        player_name_noir = data.decode()[4:]
        if plateau is None:
            from plateau_builder import creer_plateau
            plateau = creer_plateau()
        # Initialisation des pions vides pour Isolation
        pions = {'X': set(), 'O': set()}
        plateau_str = plateau_to_str(plateau)
        pions_str = pions_to_str(pions)
        sock.sendall((plateau_str + '\nENDPLATEAU\n').encode())
        sock.sendall((pions_str + '\nENDPIONS\n').encode())
        joueurs = [Joueur(player_name_blanc, 'X'), Joueur(player_name_noir, 'O')]
        jeu = JeuIsolation(plateau, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=[player_name_blanc, player_name_noir], root=root)
        jeu.pions = pions
        jeu.afficher_plateau()
        jeu.jouer()
    else:
        def client_receive_and_start():
            data = sock.recv(4096)
            player_name_blanc_local = data.decode()[4:]
            sock.sendall(f"nom:{player_name_noir}".encode())
            def recv_until(sock, end_marker):
                data = b''
                while not data.decode(errors='ignore').endswith(end_marker):
                    part = sock.recv(1024)
                    if not part:
                        raise ConnectionError("Connexion interrompue lors de la réception des données réseau.")
                    data += part
                return data.decode().replace(end_marker, '').strip()
            plateau_str = recv_until(sock, '\nENDPLATEAU\n')
            pions_str = recv_until(sock, '\nENDPIONS\n')
            plateau_local = str_to_plateau(plateau_str)
            pions_local = str_to_pions(pions_str)
            def start_game():
                if wait_win is not None:
                    wait_win.destroy()
                joueurs = [Joueur(player_name_blanc_local, 'X'), Joueur(player_name_noir, 'O')]
                jeu = JeuIsolation(plateau_local, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=[player_name_blanc_local, player_name_noir], root=root)
                jeu.pions = pions_local
                jeu.afficher_plateau()
                jeu.jouer()
            root.after(0, start_game)
        threading.Thread(target=client_receive_and_start, daemon=True).start()
