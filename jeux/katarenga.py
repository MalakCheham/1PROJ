import os
import subprocess
import sys
import threading
import tkinter as tk

from PIL import Image, ImageTk
from core.plateau import Plateau
from core.joueur import Joueur
from core.aide import get_regles
from core.musique import jouer_musique
from tkinter import messagebox
from core.mouvement import generer_coups_possibles, peut_entrer_camp
from core.network.utils import plateau_to_str, pions_to_str, str_to_plateau, str_to_pions
jouer_musique()

CAMPS_X = [(0,0), (0,9)]
CAMPS_O = [(9,0), (9,9)]

class JeuKatarenga:
    def __init__(self, plateau, joueurs, mode="1v1", root=None, sock=None, is_host=False, noms_joueurs=None):
        if root:
            for widget in root.winfo_children():
                widget.destroy()

        self.plateau = Plateau()
        self.plateau.cases = [['#' for _ in range(10)] for _ in range(10)]
        for i in range(8):
            for j in range(8):
                self.plateau.cases[i+1][j+1] = plateau.cases[i][j]
        for (i, j) in CAMPS_X + CAMPS_O:
            self.plateau.cases[i][j] = 'CAMP'
        """ Masquer le tour du tableau sauf les camps """
        for i in [0,9]:
            for j in range(10):
                if (i,j) not in CAMPS_X + CAMPS_O:
                    self.plateau.cases[i][j] = '#'
        for j in [0,9]:
            for i in range(10):
                if (i,j) not in CAMPS_X + CAMPS_O:
                    self.plateau.cases[i][j] = '#'

        self.joueurs = joueurs
        self.mode = mode
        self.sock = sock
        self.is_host = is_host
        self.noms_joueurs = noms_joueurs or ["Joueur Blanc", "Joueur Noir"]
        self.root = root if root else tk.Tk()

        self.pions = {
            'X': {(1, j) for j in range(1, 9)},
            'O': {(8, j) for j in range(1, 9)}
        }
        
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.selection = None
        self.coups_possibles = set()

        self.root.title("Katarenga")
        self.root.configure(bg="#f0f4f8") 

        self.setup_ui()
        self.start_timer()

        if self.sock:
            self.setup_network()

    def setup_ui(self):
        header_bg = "#e0e0e0"
        header = tk.Frame(self.root, bg=header_bg, height=80)
        header.pack(side="top", fill="x")
        from core.langues import traduire
        username = getattr(self.root, 'USERNAME', None)

        bienvenue = tk.Label(header, text="Katarenga", font=("Arial", 22, "bold"), bg=header_bg, fg="#5b7fce")
        bienvenue.pack(side="left", padx=32, pady=18)

        img = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
        if hasattr(self.root, 'tk'):
            icon = ImageTk.PhotoImage(img, master=self.root)
        else:
            icon = ImageTk.PhotoImage(img)
        self.icon = icon 
        btn_icon = tk.Button(header, image=self.icon, bg=header_bg, bd=0, relief="flat", cursor="hand2", activebackground=header_bg, highlightthickness=0)
        btn_icon.image = self.icon
        btn_icon.pack(side="right", padx=28, pady=12)

        def show_logout_menu(event):
            from tkinter import messagebox
            menu = tk.Menu(self.root, tearoff=0)
            from core.langues import traduire
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

        from core.musique import SoundBar, regler_volume
        from core.parametres import LanguageSelector
        volume_transmis = getattr(self.root, 'VOLUME', None)
        initial_volume = 50
        if hasattr(self.root, 'volume_var'):
            try:
                initial_volume = self.root.volume_var.get()
            except Exception:
                pass
        elif volume_transmis is not None:
            initial_volume = volume_transmis
        if hasattr(self.root, 'volume_var'):
            self.root.volume_var.set(initial_volume)
            soundbar = SoundBar(self.root, volume_var=self.root.volume_var)
        else:
            self.root.volume_var = tk.IntVar(value=initial_volume)
            soundbar = SoundBar(self.root, volume_var=self.root.volume_var)
        regler_volume(self.root.volume_var.get())
        soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

        def on_language_changed(new_lang):
            try:
                current_volume = soundbar.volume_var.get()
            except Exception:
                current_volume = getattr(self.root, 'volume_var', tk.IntVar(value=50)).get()
            import importlib
            import core.langues
            importlib.reload(core.langues)
            
            self.redraw_ui_only()
        lang_selector = LanguageSelector(self.root, assets_dir="assets", callback=on_language_changed)
        lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

        main_frame = tk.Frame(self.root, bg="#f0f4f0")
        main_frame.pack(pady=10, expand=True, fill="both")

        self.tour_label = tk.Label(main_frame, text="", font=("Helvetica", 13, "bold"), bg="#f0f4f0", fg="#003366")
        self.tour_label.pack(pady=(0,2))
        self.pions_restants_label = tk.Label(main_frame, text="", font=("Helvetica", 11), bg="#f0f4f0", fg="#003366")
        self.pions_restants_label.pack(pady=(0,2))
        self.timer_label = tk.Label(main_frame, text="00:00", font=("Helvetica", 13, "bold"), bg="#f0f4f0", fg="#003366")
        self.timer_label.pack(pady=(0,2))

        self.TAILLE_CASE = 52
        self.PLATEAU_DIM = 10
        canvas_size = self.TAILLE_CASE * self.PLATEAU_DIM
        self.canvas = tk.Canvas(main_frame, width=canvas_size, height=canvas_size, bg="#f0f4f0", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.55, anchor="center")

        def retour_config():
            import config_gui
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
            username = getattr(self.root, 'USERNAME', None)
            config_gui.main(self.root, "katarenga", username=username, volume=current_volume)
        img_retour = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
        if hasattr(self.root, 'tk'):
            icon_retour = ImageTk.PhotoImage(img_retour, master=self.root)
        else:
            icon_retour = ImageTk.PhotoImage(img_retour)
        self.icon_retour = icon_retour
        btn_retour = tk.Button(self.root, image=self.icon_retour, command=retour_config, bg="#f0f4f0", bd=0, relief="flat", cursor="hand2", activebackground="#e0e0e0")
        btn_retour.image = icon_retour  # Correction : on assigne bien l'attribut image, pas icon_retour
        btn_retour.place(relx=0.0, rely=0.5, anchor="w", x=18)

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

    def setup_network(self):
        threading.Thread(target=self.network_listener, daemon=True).start()
        self.lock_ui_if_needed()

    def network_listener(self):
        while True:
            try:
                if not self.sock:
                    break

                data = self.sock.recv(1024)
                if not data:
                    break

                msg = data.decode()
                if msg.startswith('move:'):
                    coords = msg[5:].split('->')
                    depart = tuple(map(int, coords[0].split(',')))
                    arrivee = tuple(map(int, coords[1].split(',')))

                    self.root.after(0, lambda: self.apply_network_move(depart, arrivee))
            except Exception as e:
                print(f"Network error: {e}")
                break

    def lock_ui_if_needed(self):
        if not self.sock:
            return
        mon_symbole = 'X' if self.is_host else 'O'
        if (self.tour % 2 == 0 and mon_symbole != 'X') or (self.tour % 2 == 1 and mon_symbole != 'O'):
            self.canvas.unbind("<Button-1>")
        else:
            self.canvas.bind("<Button-1>", self.on_click)

    def send_move(self, depart, arrivee):
        from core.langues import traduire
        if self.sock:
            try:
                msg = f"move:{depart[0]},{depart[1]}->{arrivee[0]},{arrivee[1]}".encode()
                self.sock.sendall(msg)
            except Exception as e:
                print(f"Error sending move: {e}")
                messagebox.showerror(traduire("erreur"), traduire("erreur_envoi_coup"))

    def apply_network_move(self, depart, arrivee):
        joueur = self.joueur_actuel()
        symbole = joueur.symbole

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

        if self.tour % 2 == 0:
            couleur = 'noir'
        else:
            couleur = 'blanc'
        
        nom = self.noms_joueurs[self.tour % 2] if self.noms_joueurs else f"Joueur {traduire(couleur)}"

        self.tour_label.config(text=f"{traduire('tour_de')} ({traduire(couleur)})")
        pions_x_restants = len(self.pions['X'])
        pions_o_restants = len(self.pions['O'])
        self.pions_restants_label.config(text=f"{traduire('pions_restants')} - {traduire('blanc')}: {pions_x_restants}, {traduire('noir')}: {pions_o_restants}")

    def afficher_plateau(self):
        self.canvas.delete("all")
        taille = self.TAILLE_CASE
        dim = self.PLATEAU_DIM
        canvas_size = taille * dim

        w = int(self.canvas.winfo_width())
        h = int(self.canvas.winfo_height())
        offset_x = (w - canvas_size) // 2 if w > canvas_size else 0
        offset_y = (h - canvas_size) // 2 if h > canvas_size else 0

        colors = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}
        camps = CAMPS_X + CAMPS_O
        for i in range(dim):
            for j in range(dim):
                if (i in [0,9] or j in [0,9]) and (i,j) not in camps:
                    continue
                x1 = offset_x + j * taille
                y1 = offset_y + i * taille
                x2 = x1 + taille
                y2 = y1 + taille
                fill = colors.get(self.plateau.cases[i][j], 'white')
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)
                for symbol, color in [('X', 'black'), ('O', 'white')]:
                    if (i, j) in self.pions[symbol]:
                        self.canvas.create_oval(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill=color)
                if self.selection == (i, j):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline='blue', width=3)
                if hasattr(self, 'coups_possibles') and (i, j) in getattr(self, 'coups_possibles', set()):
                    self.canvas.create_oval(x1 + 16, y1 + 16, x2 - 16, y2 - 16, fill='lightgreen')
        for (i, j) in camps:
            self.canvas.create_rectangle(j * taille, i * taille, (j + 1) * taille, (i + 1) * taille, outline='black', width=3)

    def generer_coups_possibles(self, depart, couleur, symbole):
        if depart in CAMPS_X + CAMPS_O:
            return set()
        coups = generer_coups_possibles(depart, couleur, symbole, self.plateau, self.pions, capture=True)
        coups_filtrés = set()

        if symbole == 'X' and depart[0] == 7:
            for coin in CAMPS_O:
                if coin not in self.pions['X'] and coin not in self.pions['O']:
                    coups_filtrés.add(coin)
        if symbole == 'O' and depart[0] == 1:
            for coin in CAMPS_X:
                if coin not in self.pions['X'] and coin not in self.pions['O']:
                    coups_filtrés.add(coin)

        for arrivee in coups:
            if arrivee in CAMPS_O and symbole == 'X' and depart[0] == 7:
                continue
            if arrivee in CAMPS_X and symbole == 'O' and depart[0] == 1:
                continue
            if arrivee not in CAMPS_X + CAMPS_O:
                if self.plateau.cases[arrivee[0]][arrivee[1]] != '#':
                    coups_filtrés.add(arrivee)
        return coups_filtrés

    def verifier_victoire(self):
        from core.langues import traduire
        x_in_camps = [p for p in self.pions['X'] if p in CAMPS_O]
        o_in_camps = [p for p in self.pions['O'] if p in CAMPS_X]
        if len(set(x_in_camps)) == 2:
            self.pause_timer()
            nom = getattr(self.joueurs[0], 'nom', str(self.joueurs[0]))
            messagebox.showinfo(traduire("victoire"), traduire("victoire_2_coins").format(nom=nom))
            self.retour_login()
        elif len(set(o_in_camps)) == 2:
            self.pause_timer()
            nom = getattr(self.joueurs[1], 'nom', str(self.joueurs[1]))
            messagebox.showinfo(traduire("victoire"), traduire("victoire_2_coins").format(nom=nom))
            self.retour_login()
        elif len(self.pions['X']) < 2:
            self.pause_timer()
            nom = getattr(self.joueurs[1], 'nom', str(self.joueurs[1]))
            messagebox.showinfo(traduire("victoire"), traduire("victoire_blanc_plus_pions").format(nom=nom))
            self.retour_login()
        elif len(self.pions['O']) < 2:
            self.pause_timer()
            nom = getattr(self.joueurs[0], 'nom', str(self.joueurs[0]))
            messagebox.showinfo(traduire("victoire"), traduire("victoire_noir_plus_pions").format(nom=nom))
            self.retour_login()

    def retour_login(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        for w in self.root.winfo_children():
            w.destroy()
        import login
        try:
            current_volume = self.root.volume_var.get()
        except AttributeError:
            try:
                from core.musique import SoundBar
                current_volume = SoundBar.last_volume
            except Exception:
                current_volume = None
        login.show_login(self.root, volume=current_volume)

    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running or not self.root.winfo_exists():
            return
        try:
            minutes, seconds = divmod(self.timer_seconds, 60)
            if self.timer_label.winfo_exists():
                self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.timer_seconds += 1
            self.timer_id = self.root.after(1000, self.update_timer)
        except tk.TclError:
            self.timer_running = False
            return

    def pause_timer(self):
        self.timer_running = False

    def reprendre_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def retour_menu(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        self.root.destroy()
        subprocess.Popen([sys.executable, "menu_gui.py"])

    def aide_popup(self):
        from core.langues import traduire
        self.pause_timer()
        aide = tk.Toplevel(self.root)
        aide.title(traduire("regles_du_jeu"))
        aide.geometry("400x400")
        aide.configure(bg="#f0f4f8")

        tk.Label(aide, text=traduire("regles_katarenga"), font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)
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
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        self.pions = {'X': {(1, j) for j in range(1, 9)}, 'O': {(8, j) for j in range(1, 9)}}
        self.tour = 0
        self.timer_seconds = 0
        self.selection = None
        self.coups_possibles = set()
        self.redraw_ui_only()
        self.start_timer()

    def jouer(self):
        self.root.mainloop()

    def on_click(self, event):
        ligne = event.y // self.TAILLE_CASE
        colonne = event.x // self.TAILLE_CASE
        joueur, symbole = self.joueur_actuel(), self.joueur_actuel().symbole
        position_cliquee = (ligne, colonne)
        if self.selection is None:
            if position_cliquee in self.pions[symbole] and position_cliquee not in CAMPS_X + CAMPS_O:
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
                if position_cliquee in self.pions[symbole] and position_cliquee not in CAMPS_X + CAMPS_O:
                    self.selection = position_cliquee
                    couleur_depart = self.plateau.cases[self.selection[0]][self.selection[1]]
                    self.coups_possibles = self.generer_coups_possibles(self.selection, couleur_depart, symbole)
                    self.afficher_plateau()

def lancer_jeu_reseau(root, is_host, player_name_blanc, player_name_noir, sock, plateau=None, pions=None, wait_win=None):
    import threading
    if is_host:
        sock.sendall(f"nom:{player_name_blanc}".encode())
        data = sock.recv(4096)
        player_name_noir = data.decode()[4:]
        if plateau is None:
            from plateau_builder import creer_plateau
            plateau = creer_plateau()
        if pions is None:
            pions = {
                'X': {(1, j) for j in range(1, 9)},
                'O': {(8, j) for j in range(1, 9)}
            }
        plateau_str = plateau_to_str(plateau)
        pions_x_str = pions_to_str({'X': pions['X']})
        pions_o_str = pions_to_str({'O': pions['O']})
        sock.sendall((plateau_str + '\nENDPLATEAU\n').encode())
        sock.sendall((pions_x_str + '\nENDPIONSX\n').encode())
        sock.sendall((pions_o_str + '\nENDPIONSO\n').encode())
        joueurs = [Joueur(player_name_blanc, 'X'), Joueur(player_name_noir, 'O')]
        jeu = JeuKatarenga(plateau, joueurs, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=[player_name_blanc, player_name_noir], root=root)
        jeu.pions = pions
        jeu.afficher_plateau()
        jeu.jouer()
    else:
        def client_receive_and_start():
            try:
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
                pions_x_str = recv_until(sock, '\nENDPIONSX\n')
                pions_o_str = recv_until(sock, '\nENDPIONSO\n')
                plateau_local = str_to_plateau(plateau_str)
                pions_local = {
                    'X': str_to_pions(pions_x_str),
                    'O': str_to_pions(pions_o_str)
                }
                def start_game():
                    if wait_win is not None:
                        wait_win.destroy()
                    joueurs = [Joueur(player_name_blanc_local, 'X'), Joueur(player_name_noir, 'O')]
                    jeu = JeuKatarenga(plateau_local, joueurs, pions=pions_local, mode="reseau", sock=sock, is_host=is_host, noms_joueurs=[player_name_blanc_local, player_name_noir], root=root)
                    jeu.afficher_plateau()
                    jeu.jouer()
                root.after(0, start_game)
            except Exception as e:
                import traceback
                print("[ERREUR réseau client]", e)
                traceback.print_exc()
                from tkinter import messagebox
                messagebox.showerror("Erreur réseau", f"Erreur lors de la connexion réseau côté client :\n{e}")
        threading.Thread(target=client_receive_and_start, daemon=True).start()

if __name__ == '__main__':
    plateau = Plateau()
    joueurs = [Joueur("Joueur 1", 'O'), Joueur("Joueur 2", 'X')]
    jeu = JeuKatarenga(plateau, joueurs)
    jeu.jouer()