import os
import subprocess
import sys
import threading
import tkinter as tk
from PIL import Image, ImageTk
from core.plateau import Board
from core.joueur import Player
from core.aide import get_rules
from core.musique import play_music, SoundBar, set_volume
from tkinter import messagebox
from core.mouvement import generate_possible_moves, can_enter_camp
from core.network.utils import plateau_to_str, pions_to_str, str_to_plateau, str_to_pions
from core.langues import translate
from core.parametres import LanguageSelector
play_music()

CAMP_POSITIONS_X = [(0, 0), (0, 9)]
CAMP_POSITIONS_O = [(9, 0), (9, 9)]

class GameKatarenga:
    def __init__(self, board, players, mode="1v1", root=None, sock=None, is_host=False, player_names=None, pieces=None):
        if root:
            for widget in root.winfo_children():
                widget.destroy()
        self.board = Board()
        self.board.cells = [['#' for _ in range(10)] for _ in range(10)]
        for row_index in range(8):
            for col_index in range(8):
                self.board.cells[row_index+1][col_index+1] = board.cells[row_index][col_index]
        for (row, col) in CAMP_POSITIONS_X + CAMP_POSITIONS_O:
            self.board.cells[row][col] = 'CAMP'
        for row in [0, 9]:
            for col in range(10):
                if (row, col) not in CAMP_POSITIONS_X + CAMP_POSITIONS_O:
                    self.board.cells[row][col] = '#'
        for col in [0, 9]:
            for row in range(10):
                if (row, col) not in CAMP_POSITIONS_X + CAMP_POSITIONS_O:
                    self.board.cells[row][col] = '#'
        self.players = players
        self.mode = mode
        self.sock = sock
        self.is_host = is_host
        self.player_names = player_names or ["White Player", "Black Player"]
        self.root = root if root else tk.Tk()
        if pieces is not None:
            self.pieces = pieces
        else:
            self.pieces = {
                'X': {(1, col_index) for col_index in range(1, 9)},
                'O': {(8, col_index) for col_index in range(1, 9)}
            }
        self.turn = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.selected_piece = None
        self.possible_moves = set()
        self.root.title("Katarenga")
        self.root.configure(bg="#f0f4f8")
        self.setup_ui()
        self.start_timer()
        if self.sock:
            self.setup_network()

    def setup_ui(self):
        header_background = "#e0e0e0"
        header_frame = tk.Frame(self.root, bg=header_background, height=80)
        header_frame.pack(side="top", fill="x")
        username = getattr(self.root, 'USERNAME', None)
        title_label = tk.Label(header_frame, text="Katarenga", font=("Arial", 22, "bold"), bg=header_background, fg="#5b7fce")
        title_label.pack(side="left", padx=32, pady=18)
        icon_image = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
        icon_photo = ImageTk.PhotoImage(icon_image, master=self.root)
        self.header_icon = icon_photo
        icon_button = tk.Button(header_frame, image=self.header_icon, bg=header_background, bd=0, relief="flat", cursor="hand2", activebackground=header_background, highlightthickness=0)
        icon_button.image = self.header_icon
        icon_button.pack(side="right", padx=28, pady=12)
        icon_button.bind("<Button-1>", self.show_submenu)
        self.setup_soundbar_and_language_selector()
        main_frame = tk.Frame(self.root, bg="#f0f4f0")
        main_frame.pack(pady=10, expand=True, fill="both")
        self.turn_label = tk.Label(main_frame, text="", font=("Helvetica", 13, "bold"), bg="#f0f4f0", fg="#003366")
        self.turn_label.pack(pady=(0,2))
        self.remaining_pieces_label = tk.Label(main_frame, text="", font=("Helvetica", 11), bg="#f0f4f0", fg="#003366")
        self.remaining_pieces_label.pack(pady=(0,2))
        self.timer_label = tk.Label(main_frame, text="00:00", font=("Helvetica", 13, "bold"), bg="#f0f4f0", fg="#003366")
        self.timer_label.pack(pady=(0,2))
        self.TILE_SIZE = 52
        self.BOARD_DIM = 10
        canvas_size = self.TILE_SIZE * self.BOARD_DIM
        self.canvas = tk.Canvas(main_frame, width=canvas_size, height=canvas_size, bg="#f0f4f0", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.55, anchor="center")
        self.create_back_button()
        self.load_and_pack_button("point-dinterrogation.png", "?", self.root, self.show_help_popup, "bottom", pady=10)
        self.load_and_pack_button("fleche-pivotante-vers-la-gauche.png", "Replay", self.root, self.restart_game, "bottom", pady=10)
        self.update_player_info()
        self.display_board()
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.update_idletasks()
        self.root.update()

    def show_submenu(self, event):
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
        transmitted_volume = getattr(self.root, 'VOLUME', None)
        initial_volume = 50
        if hasattr(self.root, 'volume_var'):
            try:
                initial_volume = self.root.volume_var.get()
            except Exception:
                pass
            self.root.volume_var.set(initial_volume)
            soundbar = SoundBar(self.root, volume_var=self.root.volume_var)
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

    def create_back_button(self):
        def return_to_config():
            import config_gui
            try:
                current_volume = self.root.volume_var.get()
            except AttributeError:
                try:
                    current_volume = SoundBar.last_volume
                except Exception:
                    current_volume = None
            for widget in self.root.winfo_children():
                widget.destroy()
            username = getattr(self.root, 'USERNAME', None)
            config_gui.main(self.root, "katarenga", username=username, volume=current_volume)
        back_image = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
        back_icon = ImageTk.PhotoImage(back_image, master=self.root)
        self.back_icon = back_icon
        back_button = tk.Button(self.root, image=self.back_icon, command=return_to_config, bg="#f0f4f8", bd=0, relief="flat", cursor="hand2", activebackground="#e0e0e0")
        back_button.image = self.back_icon
        back_button.place(relx=0.0, rely=0.5, anchor="w", x=18)

    def redraw_ui_only(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.update_player_info()
        self.display_board()

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
            except Exception:
                break

    def lock_ui_if_needed(self):
        if not self.sock or not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
            return
        my_symbol = 'X' if self.is_host else 'O'
        if (self.turn % 2 == 0 and my_symbol != 'X') or (self.turn % 2 == 1 and my_symbol != 'O'):
            self.canvas.unbind("<Button-1>")
        else:
            self.canvas.bind("<Button-1>", self.on_click)

    def send_move(self, depart, arrivee):
        from core.langues import translate
        if self.sock:
            try:
                msg = f"move:{depart[0]},{depart[1]}->{arrivee[0]},{arrivee[1]}".encode()
                self.sock.sendall(msg)
            except Exception:
                messagebox.showerror(translate("erreur"), translate("erreur_envoi_coup"))

    def apply_network_move(self, depart, arrivee):
        player = self.current_player()
        symbol = player.symbol

        piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pieces[s]), None)

        if piece_arrivee and self.turn > 0:
            self.pieces[piece_arrivee].discard(arrivee)

        self.pieces[symbol].discard(depart)
        self.pieces[symbol].add(arrivee)

        self.turn += 1
        self.selected_piece = None
        self.possible_moves = set()

        self.display_board()
        self.update_player_info()
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

    def current_player(self):
        return self.players[self.turn % 2]

    def update_player_info(self):
        from core.langues import translate

        if self.turn % 2 == 0:
            color = 'black'
        else:
            color = 'white'
        name = self.player_names[self.turn % 2] if self.player_names else f"Player {translate(color)}"
        self.turn_label.config(text=f"{translate('turn_of')} ({translate(color)})")
        remaining_x = len(self.pieces['X'])
        remaining_o = len(self.pieces['O'])
        self.remaining_pieces_label.config(text=f"{translate('remaining_pawns')} - {translate('blanc')}: {remaining_x}, {translate('noir')}: {remaining_o}")

    def display_board(self):
        self.canvas.delete("all")
        size = self.TILE_SIZE
        dim = self.BOARD_DIM
        canvas_size = size * dim

        w = int(self.canvas.winfo_width())
        h = int(self.canvas.winfo_height())
        offset_x = (w - canvas_size) // 2 if w > canvas_size else 0
        offset_y = (h - canvas_size) // 2 if h > canvas_size else 0

        colors = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}
        camps = CAMP_POSITIONS_X + CAMP_POSITIONS_O
        for i in range(dim):
            for j in range(dim):
                if (i in [0,9] or j in [0,9]) and (i,j) not in camps:
                    continue
                x1 = offset_x + j * size
                y1 = offset_y + i * size
                x2 = x1 + size
                y2 = y1 + size
                fill = colors.get(self.board.cells[i][j], 'white')
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)
                for symbol, color in [('X', 'black'), ('O', 'white')]:
                    if (i, j) in self.pieces[symbol]:
                        self.canvas.create_oval(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill=color)
                if self.selected_piece == (i, j):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline='blue', width=3)
                if hasattr(self, 'possible_moves') and (i, j) in getattr(self, 'possible_moves', set()):
                    self.canvas.create_oval(x1 + 16, y1 + 16, x2 - 16, y2 - 16, fill='lightgreen')
        for (i, j) in camps:
            self.canvas.create_rectangle(j * size, i * size, (j + 1) * size, (i + 1) * size, outline='black', width=3)

    def generate_possible_moves_custom(self, start, color, symbol):
        moves = generate_possible_moves(start, color, symbol, self.board, self.pieces, capture=True)
        filtered_moves = set()

        if symbol == 'X' and start[0] == 8:
            for camp in CAMP_POSITIONS_O:
                if camp not in self.pieces['X'] and camp not in self.pieces['O']:
                    filtered_moves.add(camp)
        if symbol == 'O' and start[0] == 1:
            for camp in CAMP_POSITIONS_X:
                if camp not in self.pieces['X'] and camp not in self.pieces['O']:
                    filtered_moves.add(camp)

        for end in moves:
            if end in CAMP_POSITIONS_O and symbol == 'X' and start[0] == 8:
                continue
            if end in CAMP_POSITIONS_X and symbol == 'O' and start[0] == 1:
                continue
            if end not in CAMP_POSITIONS_X + CAMP_POSITIONS_O:
                if self.board.cells[end[0]][end[1]] != '#':
                    filtered_moves.add(end)
        return filtered_moves

    def verifier_victoire(self):
        from core.langues import translate
        x_in_camps = [p for p in self.pieces['X'] if p in CAMP_POSITIONS_O]
        o_in_camps = [p for p in self.pieces['O'] if p in CAMP_POSITIONS_X]
        if len(set(x_in_camps)) == 2:
            self.pause_timer()
            name = getattr(self.players[0], 'name', str(self.players[0]))
            messagebox.showinfo(translate("victory"), translate("victory_2_pawns_in_corners").format(name=name))
            self.return_to_login()
        elif len(set(o_in_camps)) == 2:
            self.pause_timer()
            name = getattr(self.players[1], 'name', str(self.players[1]))
            messagebox.showinfo(translate("victory"), translate("victory_2_pawns_in_corners").format(name=name))
            self.return_to_login()
        elif len(self.pieces['X']) < 2:
            self.pause_timer()
            name = getattr(self.players[1], 'name', str(self.players[1]))
            messagebox.showinfo(translate("victory"), translate("victory_black_not_enough_pawns").format(name=name))
            self.return_to_login()
        elif len(self.pieces['O']) < 2:
            self.pause_timer()
            name = getattr(self.players[0], 'name', str(self.players[0]))
            messagebox.showinfo(translate("victory"), translate("victory_white_not_enough_pawns").format(name=name))
            self.return_to_login()

    def return_to_login(self):
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

    def resume_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def return_to_menu(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        self.root.destroy()
        subprocess.Popen([sys.executable, "menu_gui.py"])

    def show_help_popup(self):
        from core.langues import translate
        self.pause_timer()
        help_window = tk.Toplevel(self.root)
        help_window.title(translate("regles_du_jeu"))
        help_window.geometry("400x400")
        help_window.configure(bg="#f0f4f8")
        tk.Label(help_window, text=translate("regles_katarenga"), font=("Helvetica", 14, "bold"), bg="#f0f4f8", fg="#003366").pack(pady=10)
        text_widget = tk.Text(help_window, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", get_rules("katarenga"))
        text_widget.configure(state="disabled")
        def on_close():
            self.resume_timer()
            help_window.destroy()
        help_window.protocol("WM_DELETE_WINDOW", on_close)

    def restart_game(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            self.root.after_cancel(self.timer_id)
        self.pieces = {'X': {(1, j) for j in range(1, 9)}, 'O': {(8, j) for j in range(1, 9)}}
        self.turn = 0
        self.timer_seconds = 0
        self.selected_piece = None
        self.possible_moves = set()
        self.redraw_ui_only()
        self.start_timer()

    def play(self):
        self.root.mainloop()

    def on_click(self, event):
        row = event.y // self.TILE_SIZE
        col = event.x // self.TILE_SIZE
        player, symbol = self.current_player(), self.current_player().symbol
        clicked_position = (row, col)
        if self.selected_piece is None:
            if clicked_position in self.pieces[symbol] and clicked_position not in CAMP_POSITIONS_X + CAMP_POSITIONS_O:
                self.selected_piece = clicked_position
                start_color = self.board.cells[self.selected_piece[0]][self.selected_piece[1]]
                self.possible_moves = self.generate_possible_moves_custom(self.selected_piece, start_color, symbol)
                self.display_board()
        else:
            depart, arrivee = self.selected_piece, clicked_position
            start_color = self.board.cells[depart[0]][depart[1]]
            piece_arrivee = next((s for s in ['X', 'O'] if arrivee in self.pieces[s]), None)
            if arrivee in self.possible_moves:
                if piece_arrivee and self.turn > 0:
                    self.pieces[piece_arrivee].discard(arrivee)
                elif piece_arrivee:
                    messagebox.showinfo("Invalid", "Captures are not allowed on the first turn.")
                    return
                self.pieces[symbol].discard(depart)
                self.pieces[symbol].add(arrivee)
                self.turn += 1
                self.selected_piece = None
                self.possible_moves = set()
                self.display_board()
                self.update_player_info()
                self.verifier_victoire()
                if self.sock:
                    self.send_move(depart, arrivee)
                self.lock_ui_if_needed()
            else:
                self.selected_piece = None
                self.possible_moves = set()
                if clicked_position in self.pieces[symbol] and clicked_position not in CAMP_POSITIONS_X + CAMP_POSITIONS_O:
                    self.selected_piece = clicked_position
                    start_color = self.board.cells[self.selected_piece[0]][self.selected_piece[1]]
                    self.possible_moves = self.generate_possible_moves_custom(self.selected_piece, start_color, symbol)
                    self.display_board()

def launch_network_game(root, is_host, player_name_white, player_name_black, sock, board=None, pieces=None, wait_win=None):
    import threading
    if is_host:
        sock.sendall(f"nom:{player_name_white}".encode())
        data = sock.recv(4096)
        player_name_black = data.decode()[4:]
        if board is None:
            from plateau_builder import creer_plateau
            board = creer_plateau()
        if pieces is None:
            pieces = {
                'X': {(1, j) for j in range(1, 9)},
                'O': {(8, j) for j in range(1, 9)}
            }
        board_str = plateau_to_str(board)
        pieces_str = pions_to_str(pieces)
        sock.sendall((board_str + '\nENDPLATEAU\n').encode())
        sock.sendall((pieces_str + '\nENDPIONS\n').encode())
        players = [Player(player_name_white, 'X'), Player(player_name_black, 'O')]
        jeu = GameKatarenga(board, players, mode="network", sock=sock, is_host=is_host, player_names=[player_name_white, player_name_black], root=root)
        jeu.pieces = pieces
        jeu.display_board()
        jeu.play()
    else:
        def client_receive_and_start():
            try:
                data = sock.recv(4096)
                player_name_white_local = data.decode()[4:]
                sock.sendall(f"nom:{player_name_black}".encode())
                def recv_until(sock, end_marker, leftover=b''):
                    data = leftover
                    while end_marker.encode() not in data:
                        part = sock.recv(1024)
                        if not part:
                            raise ConnectionError("Connexion interrompue lors de la réception des données réseau.")
                        data += part
                    idx = data.index(end_marker.encode()) + len(end_marker)
                    return data[:idx - len(end_marker)].decode().strip(), data[idx:]
                board_str, leftover = recv_until(sock, '\nENDPLATEAU\n')
                pieces_str, leftover = recv_until(sock, '\nENDPIONS\n', leftover)
                board_local = str_to_plateau(board_str)
                pieces_local = str_to_pions(pieces_str.strip())
                def start_game():
                    if wait_win is not None:
                        wait_win.destroy()
                    players = [Player(player_name_white_local, 'X'), Player(player_name_black, 'O')]
                    jeu = GameKatarenga(board_local, players, pieces=pieces_local, mode="network", sock=sock, is_host=is_host, player_names=[player_name_white_local, player_name_black], root=root)
                    jeu.display_board()
                    jeu.update_player_info()
                    jeu.play()
                root.after(0, start_game)
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Erreur réseau", f"Erreur lors de la connexion réseau côté client :\n{e}")
        threading.Thread(target=client_receive_and_start, daemon=True).start()
