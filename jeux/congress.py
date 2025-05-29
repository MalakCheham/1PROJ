import tkinter as tk
import subprocess
import sys
import os
import threading
import random

from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles
from core.mouvement import generer_coups_possibles
from tkinter import messagebox
from PIL import Image, ImageTk
from core.musique import play_music

class JeuCongress:
    def __init__(self, plateau, joueurs, mode="1v1", sock=None, is_host=False, noms_joueurs=None, root=None):

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
        self.pions = {'X': set(), 'O': set()}
        self.pions['X'].update([(0,1), (0,4), (1,7), (3,0), (4,7), (6,0), (7,3), (7,6)])
        self.pions['O'].update([(0,3), (0,6), (1,0), (3,7), (4,0), (6,7), (7,1), (7,4)])
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.selection = None
        self.root = root if root else tk.Tk()
        self.root.title("Congress")
        self.root.configure(bg="#f0f4f0")
        self.setup_ui()
        self.update_info_joueur()
        self.start_timer()
        if self.reseau:
            self.lock_ui_if_needed()
            threading.Thread(target=self.network_listener, daemon=True).start()
        else:
            self.canvas.bind("<Button-1>", self.on_click)
        play_music()

    def setup_ui(self):
        from core.langues import translate
        header_bg = "#e0e0e0"
        header = tk.Frame(self.root, bg=header_bg, height=80)
        header.pack(side="top", fill="x")

        bienvenue = tk.Label(header, text="Congress", font=("Arial", 22, "bold"), bg=header_bg, fg="#5b7fce")
        bienvenue.pack(side="left", padx=32, pady=18)

        img = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
        icon = ImageTk.PhotoImage(img, master=self.root)
        self.icon = icon
        btn_icon = tk.Button(header, image=self.icon, bg=header_bg, bd=0, relief="flat", cursor="hand2", activebackground=header_bg, highlightthickness=0)
        btn_icon.image = self.icon
        btn_icon.pack(side="right", padx=28, pady=12)
        def show_logout_menu(event):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label=translate("about"), command=lambda: messagebox.showinfo(translate("about"), translate("about_text")))
            menu.add_command(label=translate("credits"), command=lambda: messagebox.showinfo(translate("credits"), translate("credits_text")))
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
            menu.add_command(label=translate("logout"), command=go_to_login)
            menu.add_command(label=translate("close"), command=self.root.quit)
            menu.tk_popup(event.x_root, event.y_root)
        btn_icon.bind("<Button-1>", show_logout_menu)
        # Barre de son
        from core.musique import SoundBar, set_volume
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
        set_volume(self.root.volume_var.get())
        soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

        def on_language_changed(new_lang):
            import importlib
            import core.langues
            importlib.reload(core.langues)
            self.redraw_ui_only()
        lang_selector = LanguageSelector(self.root, assets_dir="assets", callback=on_language_changed)
        lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

        # Zone centrale
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(pady=10, expand=True, fill="both")
        # Frame latéral pour centrer le bouton retour verticalement
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
            # Transmet le volume si la fonction l'accepte, sinon fallback
            try:
                config_gui.afficher_interface_choix(self.root, volume=current_volume)
            except TypeError:
                config_gui.afficher_interface_choix(self.root)
        btn_retour = tk.Button(left_frame, image=self.icon_retour, command=retour_config, bg="#f0f0f0", bd=0, relief="flat", cursor="hand2", activebackground="#f0f0f0", highlightthickness=0)
        btn_retour.image = icon_retour
        btn_retour.pack(side="top", expand=True, anchor="center", pady=0)

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
        from core.langues import translate
        if self.mode == "ia":
            if self.tour % 2 == 0:
                self.tour_label.config(text=f"{translate('tour_de')} ({translate('noir')})")
            else:
                self.tour_label.config(text=f"{translate('tour_de')} ({translate('blanc')})")
        else:
            couleur = 'noir' if self.tour % 2 == 0 else 'blanc'
            nom = self.noms_joueurs[self.tour % 2] if self.noms_joueurs else f"Joueur {translate(couleur)}"
            self.tour_label.config(text=f"{translate('tour_de')} ({translate(couleur)})")

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
        joueur = self.joueur_actuel()
        symbole = joueur.symbole
        positions = self.pions[symbole]
        if not positions:
            return
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
            from core.langues import translate
            messagebox.showinfo(translate("victoire"), f"{translate('joueur')} ({translate(couleur.lower())}) {translate('a_gagne')} !")
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
        from core.langues import translate
        self.pause_timer()
        aide = tk.Toplevel(self.root)
        aide.title(translate("game_rules"))
        aide.geometry("400x400")
        aide.configure(bg="#f0f4f8")

        tk.Label(aide, text=translate("congress_rules"), font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)
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
        for w in self.root.winfo_children():
            w.destroy()
        import config_gui
        config_gui.afficher_interface_choix(self.root)

    def rejouer(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        # Réinitialise uniquement les pions
        self.pions = {
            'X': set([(0,1), (0,4), (1,7), (3,0), (4,7), (6,0), (7,3), (7,6)]),
            'O': set([(0,3), (0,6), (1,0), (3,7), (4,0), (6,7), (7,1), (7,4)])
        }
        self.tour = 0
        self.timer_seconds = 0
        self.selection = None
        self.coups_possibles = set()
        self.redraw_ui_only()
        self.start_timer()

    def generer_coups_possibles(self, depart, couleur, symbole):
        return generer_coups_possibles(depart, couleur, symbole, self.plateau, self.pions, capture=False)

def plateau_to_str(plateau):
    return '\n'.join([''.join(row) for row in plateau.cases])

def pions_to_str(pions):
    # pions: dict {'X': set(), 'O': set()}
    return '|'.join([f"{symb}:{';'.join([f'{i},{j}' for (i,j) in positions])}" for symb, positions in pions.items()])

def str_to_plateau(s):
    from core.plateau import Plateau
    lines = s.strip().split('\n')
    plateau = Plateau()
    plateau.cases = [list(line) for line in lines]
    return plateau

def str_to_pions(s):
    pions = {'X': set(), 'O': set()}
    for part in s.split('|'):
        if not part: continue
        symb, positions = part.split(':')
        if positions:
            pions[symb] = set(tuple(map(int, pos.split(','))) for pos in positions.split(';') if pos)
    return pions

def lancer_jeu_reseau(root, is_host, player_name_blanc, player_name_noir, sock, plateau=None, pions=None, wait_win=None):
    import threading
    if is_host:
        sock.sendall(f"nom:{player_name_blanc}".encode())
        data = sock.recv(4096)
        player_name_noir = data.decode()[4:]
        if plateau is None or pions is None:
            from plateau_builder import creer_plateau
            plateau = creer_plateau()
            # Initialisation correcte des pions pour Congress
            pions = {'X': set(), 'O': set()}
            pions['X'].update([(0,1), (0,4), (1,7), (3,0), (4,7), (6,0), (7,3), (7,6)])
            pions['O'].update([(0,3), (0,6), (1,0), (3,7), (4,0), (6,7), (7,1), (7,4)])
        plateau_str = plateau_to_str(plateau)
        pions_str = pions_to_str(pions)
        sock.sendall((plateau_str + '\nENDPLATEAU\n').encode())
        sock.sendall((pions_str + '\nENDPIONS\n').encode())
        joueurs = [Joueur(player_name_blanc, 'X'), Joueur(player_name_noir, 'O')]
        jeu = JeuCongress(plateau, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=[player_name_blanc, player_name_noir], root=root)
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
                jeu = JeuCongress(plateau_local, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=[player_name_blanc_local, player_name_noir], root=root)
                jeu.pions = pions_local
                jeu.afficher_plateau()
                jeu.jouer()
            root.after(0, start_game)
        threading.Thread(target=client_receive_and_start, daemon=True).start()
