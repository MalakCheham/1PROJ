import tkinter as tk
import threading
import os
import subprocess
import sys
from core.mouvement import generate_possible_moves
from core.joueur import Player
from core.aide import get_rules
from tkinter import messagebox
from PIL import Image, ImageTk
from core.musique import play_music
play_music()

class GameIsolation:
    def __init__(self, board, players, mode="1v1", sock=None, is_host=False, player_names=None, root=None):
        if root:
            for widget in root.winfo_children():
                widget.destroy()
        self.board = board
        self.players = players
        self.mode = mode
        self.tour = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.pieces = {'X': set(), 'O': set()}
        self.sock = sock
        self.is_host = is_host
        self.player_names = player_names or ["Player White", "Player Black"]
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
        from core.langues import translate
        header_background = "#e0e0e0"
        self.root.configure(bg="#f0f0f0")
        header_frame = tk.Frame(self.root, bg=header_background, height=80)
        header_frame.pack(side="top", fill="x")
        title_label = tk.Label(header_frame, text="Isolation", font=("Arial", 22, "bold"), bg=header_background, fg="#5b7fce")
        title_label.pack(side="left", padx=32, pady=18)
        icon_image = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
        icon_photo = ImageTk.PhotoImage(icon_image, master=self.root)
        
        self.header_icon = icon_photo
        
        icon_button = tk.Button(header_frame, image=self.header_icon, bg=header_background, bd=0, relief="flat", cursor="hand2", activebackground=header_background, highlightthickness=0)
        icon_button.image = self.header_icon
        icon_button.pack(side="right", padx=28, pady=12)
        icon_button.bind("<Button-1>", self.show_submenu)
        
        self.setup_soundbar_and_language_selector()
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(pady=10, expand=True, fill="both")
        
        left_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        left_frame.pack(side="left", fill="y", padx=(18, 0), pady=0)
        
        self.create_back_button(left_frame)
        self.turn_label = tk.Label(self.main_frame, text="", font=("Helvetica", 13, "bold"), bg="#f0f0f0", fg="#003366")
        self.turn_label.place(relx=0.50, rely=0.08, anchor="center")
        self.timer_label = tk.Label(self.main_frame, text="00:00", font=("Helvetica", 13, "bold"), bg="#f0f0f0", fg="#003366")
        self.timer_label.place(relx=0.50, rely=0.15, anchor="center")
        self.canvas = tk.Canvas(self.main_frame, width=400, height=400, bg="#f0f0f0", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.55, anchor="center")
        self.load_and_pack_button("point-dinterrogation.png", "?", self.root, self.help_popup, "bottom", pady=10)
        self.load_and_pack_button("fleche-pivotante-vers-la-gauche.png", "Replay", self.root, self.restart_game, "bottom", pady=10)
        self.update_info_joueur()
        self.display_board()
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.update_idletasks()
        self.root.update()

    def show_submenu(self, event):
        from core.langues import translate
        submenu = tk.Menu(self.root, tearoff=0)
        submenu.add_command(label=translate("about"), command=lambda: messagebox.showinfo(translate("about"), translate("about_text")))
        submenu.add_command(label=translate("credits"), command=lambda: messagebox.showinfo(translate("credits"), translate("credits_text")))
        submenu.add_separator()
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
            for widget in self.root.winfo_children():
                widget.destroy()
            login.show_login(self.root, volume=current_volume)
        submenu.add_command(label=translate("logout"), command=go_to_login)
        submenu.add_command(label=translate("close"), command=self.root.quit)
        submenu.tk_popup(event.x_root, event.y_root)

    def setup_soundbar_and_language_selector(self):
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
        def on_language_changed(new_language):
            import importlib
            import core.langues
            importlib.reload(core.langues)
            self.redraw_ui_only()
        lang_selector = LanguageSelector(self.root, assets_dir="assets", callback=on_language_changed)
        lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

    def create_back_button(self, parent_frame):
        def return_to_config():
            import config_gui
            try:
                current_volume = self.root.volume_var.get()
            except Exception:
                current_volume = None
            for widget in self.root.winfo_children():
                widget.destroy()
            try:
                config_gui.afficher_interface_choix(self.root, volume=current_volume)
            except TypeError:
                config_gui.afficher_interface_choix(self.root)
        back_image = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
        back_icon = ImageTk.PhotoImage(back_image, master=self.root)
        self.back_icon = back_icon
        back_button = tk.Button(parent_frame, image=self.back_icon, command=return_to_config, bg="#f0f0f0", bd=0, relief="flat", cursor="hand2", activebackground="#f0f0f0", highlightthickness=0)
        back_button.image = self.back_icon
        back_button.pack(side="top", expand=True, anchor="center", pady=0)

    def redraw_ui_only(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.update_info_joueur()
        self.display_board()

    def lock_ui_if_needed(self):
        if not self.reseau:
            return
        my_symbol = 'X' if self.is_host else 'O'
        if (self.tour % 2 == 0 and my_symbol != 'X') or (self.tour % 2 == 1 and my_symbol != 'O'):
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

    def play(self):
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

    def get_current_player(self):
        return self.players[self.tour % 2]

    def update_info_joueur(self):
        from core.langues import translate
        color = translate('white') if self.get_current_player().symbol == 'O' else translate('black')
        self.turn_label.config(text=f"{translate('turn_of')} ({translate(color)})")

    def get_blocked_cells(self):
        blocked = set()
        for symbol in ['X', 'O']:
            for pawn in self.pieces[symbol]:
                color = self.board.cells[pawn[0]][pawn[1]]
                moves = self.generate_possible_moves_custom(pawn, color, symbol)
                blocked.update(moves)
        return blocked

    def display_board(self):
        self.canvas.delete("all")
        size = 50
        colors = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}
        for i in range(8):
            for j in range(8):
                color = self.board.cells[i][j]
                fill = colors.get(color, 'white')
                self.canvas.create_rectangle(j*size, i*size, (j+1)*size, (i+1)*size, fill=fill)
                if self.board.cells[i][j] not in ['X', 'O'] and not self.is_square_safe((i, j)):
                    y = i*size + size//2
                    self.canvas.create_line(j*size+10, y, (j+1)*size-10, y, fill='black', width=3)
        for symbol in ['X', 'O']:
            for (x, y) in self.pieces[symbol]:
                color = "black" if symbol == "X" else "white"
                self.canvas.create_oval(y*size+10, x*size+10, (y+1)*size-10, (x+1)*size-10, fill=color)

    def on_click(self, event):
        ligne, colonne = event.y // 50, event.x // 50
        if not (0 <= ligne < 8 and 0 <= colonne < 8):
            return
        joueur = self.get_current_player()
        symbol = joueur.symbol
        position = (ligne, colonne)
        
        if position in self.pieces['X'] or position in self.pieces['O']:
            from core.langues import translate
            messagebox.showinfo(translate("invalid"), translate("square_already_occupied"))
            return
        
        if self.board.cells[ligne][colonne] in ['X', 'O']:
            return
        from core.langues import translate
        if not self.is_square_safe(position):
            messagebox.showinfo(translate("invalid"), translate("square_blocked"))
            return
        self.pieces[symbol].add(position)
        self.tour += 1
        self.display_board()
        self.update_info_joueur()
        self.check_victory()
        if self.reseau:
            self.send_move(position)
            self.lock_ui_if_needed()

    def apply_network_move(self, position):
        joueur = self.get_current_player()
        symbol = joueur.symbol
        
        if position in self.pieces['X'] or position in self.pieces['O']:
            return
        
        self.pieces[symbol].add(position)
        self.tour += 1
        self.display_board()
        self.update_info_joueur()
        self.check_victory()
        if self.reseau:
            self.lock_ui_if_needed()

    def is_square_safe(self, pos):
        for symbol in ['X', 'O']:
            for pawn in self.pieces[symbol]:
                color = self.board.cells[pawn[0]][pawn[1]]
                moves = self.generate_possible_moves_custom(pawn, color, symbol)
                if pos in moves:
                    return False
        return True

    def generate_possible_moves_custom(self, start, color, symbol):
        return generate_possible_moves(start, color, symbol, self.board, self.pieces, capture=False)

    def is_valid_position(self, symbol, pos):
        x, y = self.positions[symbol]
        dx, dy = abs(pos[0] - x), abs(pos[1] - y)
        if (0 <= pos[0] < 8 and 0 <= pos[1] < 8 and
            self.board.cells[pos[0]][pos[1]] not in ['X', 'O'] and
            (dx <= 1 and dy <= 1) and (dx + dy) != 0):
            return True
        return False

    def player_can_play(self):
        for i in range(8):
            for j in range(8):
                if self.board.cells[i][j] in ['X', 'O']:
                    continue
                if (i, j) in self.pieces['X'] or (i, j) in self.pieces['O']:
                    continue
                if self.is_square_safe((i, j)):
                    return True
        return False

    def check_victory(self):
        def player_can_play_inner(symbol):
            for i in range(8):
                for j in range(8):
                    if self.board.cells[i][j] in ['X', 'O']:
                        continue
                    if (i, j) in self.pieces['X'] or (i, j) in self.pieces['O']:
                        continue
                    if self.is_square_safe((i, j)):
                        return True
            return False
        if not player_can_play_inner('X') and not player_can_play_inner('O'):
            self.pause_timer()
            player = self.players[(self.tour) % 2]
            color = 'White' if player.symbol == 'X' else 'Black'
            from core.langues import translate
            messagebox.showinfo(translate("victory"), f"{translate('player')} ({translate(color.lower())}) {translate('won')} !")
            self.resume_timer()
            self.restart_game()

    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running or not self.root.winfo_exists():
            return
        try:
            if self.timer_label.winfo_exists():
                minutes, seconds = divmod(self.timer_seconds, 60)
                self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        except tk.TclError:
            return
        self.timer_seconds += 1
        self.timer_id = self.root.after(1000, self.update_timer)

    def pause_timer(self):
        self.timer_running = False

    def resume_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def help_popup(self):
        from core.langues import translate
        self.pause_timer()
        aide = tk.Toplevel(self.root)
        aide.title(translate("game_rules"))
        aide.geometry("400x400")
        aide.configure(bg="#f0f4f8")
        tk.Label(aide, text=translate("isolation_rules"), font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)
        text_widget = tk.Text(aide, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", get_rules("isolation"))
        text_widget.configure(state="disabled")
        def on_close():
            self.resume_timer()
            aide.destroy()
        aide.protocol("WM_DELETE_WINDOW", on_close)

    def return_to_menu(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass
        self.root.destroy()
        subprocess.Popen([sys.executable, "menu_gui.py"])

    def restart_game(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass
        self.pieces = {'X': set(), 'O': set()}
        self.tour = 0
        self.timer_seconds = 0
        self.selection = None if hasattr(self, 'selection') else None
        self.coups_possibles = set() if hasattr(self, 'coups_possibles') else set()
        self.redraw_ui_only()
        self.start_timer()

def launch_network_game(root, is_host, player_name_white, player_name_black, sock, board=None, pieces=None, wait_win=None):
    import threading
    from core.network.utils import plateau_to_str, pions_to_str, str_to_plateau, str_to_pions
    if is_host:
        sock.sendall(f"name:{player_name_white}".encode())
        data = sock.recv(4096)
        player_name_black = data.decode()[4:]
        if board is None:
            from plateau_builder import create_board
            board = create_board()
        pieces = {'X': set(), 'O': set()}
        board_str = plateau_to_str(board)
        pieces_str = pions_to_str(pieces)
        sock.sendall((board_str + '\nENDPLATEAU\n').encode())
        sock.sendall((pieces_str + '\nENDPIONS\n').encode())
        players = [Player(player_name_white, 'X'), Player(player_name_black, 'O')]
        game = GameIsolation(board, players, mode="network", sock=sock, is_host=is_host, player_names=[player_name_white, player_name_black], root=root)
        game.pieces = pieces
        game.display_board()
        game.play()
    else:
        def client_receive_and_start():
            data = sock.recv(4096)
            player_name_white_local = data.decode()[4:]
            sock.sendall(f"name:{player_name_black}".encode())
            def recv_until(sock, end_marker):
                data = b''
                while not data.decode(errors='ignore').endswith(end_marker):
                    part = sock.recv(1024)
                    if not part:
                        raise ConnectionError("Connection interrupted during network data reception.")
                    data += part
                return data.decode().replace(end_marker, '').strip()
            board_str = recv_until(sock, '\nENDPLATEAU\n')
            pieces_str = recv_until(sock, '\nENDPIONS\n')
            board_local = str_to_plateau(board_str)
            pieces_local = str_to_pions(pieces_str)
            def start_game():
                if wait_win is not None:
                    wait_win.destroy()
                players = [Player(player_name_white_local, 'X'), Player(player_name_black, 'O')]
                game = GameIsolation(board_local, players, mode="network", sock=sock, is_host=is_host, player_names=[player_name_white_local, player_name_black], root=root)
                game.pieces = pieces_local
                game.display_board()
                game.play()
            root.after(0, start_game)
        threading.Thread(target=client_receive_and_start, daemon=True).start()
