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
from core.mouvement import generer_coups_possibles
jouer_musique()

class JeuKatarenga:
    def __init__(self, plateau, joueurs, mode="1v1", root=None, sock=None, is_host=False, noms_joueurs=None):
        if root:
            for widget in root.winfo_children():
                widget.destroy()

        self.plateau = plateau
        self.joueurs = joueurs
        self.mode = mode
        self.sock = sock
        self.is_host = is_host
        self.noms_joueurs = noms_joueurs or ["Joueur Blanc", "Joueur Noir"]
        self.root = root if root else tk.Tk()
        self.pions = {'X': {(0, j) for j in range(8)}, 'O': {(7, j) for j in range(8)}}
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

        from tkinter import messagebox
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
        main_frame.pack(pady=10)

        self.tour_label = tk.Label(main_frame, text="", font=("Helvetica", 13, "bold"), bg="#f0f4f0", fg="#003366")
        self.tour_label.pack(pady=(0,2))
        self.pions_restants_label = tk.Label(main_frame, text="", font=("Helvetica", 11), bg="#f0f4f0", fg="#003366")
        self.pions_restants_label.pack(pady=(0,2))
        self.timer_label = tk.Label(main_frame, text="00:00", font=("Helvetica", 13, "bold"), bg="#f0f4f0", fg="#003366")
        self.timer_label.pack(pady=(0,2))

        self.canvas = tk.Canvas(main_frame, width=400, height=400, bg="#f0f4f0", highlightthickness=0)
        self.canvas.pack()

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
        btn_retour.image = self.icon_retour
        btn_retour.place(relx=0.0, rely=0.5, anchor="w", x=18)

        
        self.load_and_pack_button("point-dinterrogation.png", "?", self.root, self.aide_popup, "bottom", pady=10)
        self.load_and_pack_button("fleche-pivotante-vers-la-gauche.png", "Rejouer", self.root, self.rejouer, "bottom", pady=10)

        self.update_info_joueur()
        self.afficher_plateau()
        self.canvas.bind("<Button-1>", self.on_click)
        # Force update Tkinter pour éviter la page blanche
        self.root.update_idletasks()
        self.root.update()

    def redraw_ui_only(self):
        # Détruit et réaffiche l'UI sans toucher à l'état du jeu
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
        if self.sock:
            try:
                msg = f"move:{depart[0]},{depart[1]}->{arrivee[0]},{arrivee[1]}".encode()
                self.sock.sendall(msg)
            except Exception as e:
                print(f"Error sending move: {e}")
                messagebox.showerror("Error", "Failed to send move to other player")

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

    def generer_coups_possibles(self, depart, couleur, symbole):
        return generer_coups_possibles(depart, couleur, symbole, self.plateau, self.pions, capture=True)

    def verifier_victoire(self):
        joueur = self.joueur_actuel()
        ligne_victoire = 7 if joueur.symbole == 'X' else 0
        if any(p[0] == ligne_victoire for p in self.pions[joueur.symbole]):
            self.pause_timer()
            couleur = 'Blanc' if joueur.symbole == 'X' else 'Noir'
            nom = getattr(joueur, 'nom', str(joueur))
            messagebox.showinfo("Victoire!", f"{nom} ({'Blanc' if joueur.symbole == 'X' else 'Noir'}) a atteint la ligne adverse et a gagné!")
            self.retour_login()
        elif not self.pions['O' if joueur.symbole == 'X' else 'X']:
            self.pause_timer()
            nom = getattr(joueur, 'nom', str(joueur))
            messagebox.showinfo("Victoire!", f"Joueur {nom} ({'Blanc' if joueur.symbole == 'X' else 'Noir'}) a gagné par capture!")
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
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        self.pions = {'X': {(0, j) for j in range(8)}, 'O': {(7, j) for j in range(8)}}
        self.tour = 0
        self.timer_seconds = 0
        self.selection = None
        self.coups_possibles = set()
        self.redraw_ui_only()
        self.start_timer()

    def jouer(self):
        self.root.mainloop()

def plateau_to_str(plateau):
    return '\n'.join(''.join(row) for row in plateau.cases)
def pions_to_str(pions):
    return ';'.join(f"{i},{j}" for (i,j) in pions)
def str_to_plateau(s):
    lines = s.strip().split('\n')
    cases = [list(line) for line in lines]
    from core.plateau import Plateau
    plateau = Plateau()
    plateau.cases = cases
    return plateau
def str_to_pions(s):
    if not s:
        return set()
    return set(tuple(map(int, pos.split(','))) for pos in s.split(';'))

def lancer_jeu_reseau(root, is_host, player_name_blanc, player_name_noir, sock, plateau=None, pions=None, wait_win=None):
    import threading
    if is_host:
        sock.sendall(f"nom:{player_name_blanc}".encode())
        data = sock.recv(4096)
        player_name_noir = data.decode()[4:]
        if plateau is None or pions is None:
            from plateau_builder import creer_plateau
            plateau, pions = creer_plateau()
        plateau_str = plateau_to_str(plateau)
        pions_x_str = pions_to_str(pions['X'])
        pions_o_str = pions_to_str(pions['O'])
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