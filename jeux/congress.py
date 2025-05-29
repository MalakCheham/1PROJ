import tkinter as tk
import subprocess
import sys
import os
import threading
import random

from core.plateau import Board
from core.joueur import Player
from core.aide import get_rules
from core.mouvement import generate_possible_moves
from tkinter import messagebox
from PIL import Image, ImageTk
from core.musique import play_music

class GameCongress:
    def __init__(self, board, players, mode="1v1", sock=None, is_host=False, player_names=None, root=None):

        if root:
            for widget in root.winfo_children():
                widget.destroy()
        self.board = board
        self.players = players
        self.mode = mode
        self.sock = sock
        self.is_host = is_host
        self.player_names = player_names or ["White Player", "Black Player"]
        self.network = sock is not None
        self.pieces = {'X': set(), 'O': set()}
        self.pieces['X'].update([(0,1), (0,4), (1,7), (3,0), (4,7), (6,0), (7,3), (7,6)])
        self.pieces['O'].update([(0,3), (0,6), (1,0), (3,7), (4,0), (6,7), (7,1), (7,4)])
        self.turn = 0
        self.timer_seconds = 0
        self.timer_running = True
        self.selection = None
        self.root = root if root else tk.Tk()
        self.root.title("Congress")
        self.root.configure(bg="#f0f4f0")
        self.setup_ui()
        self.update_player_info()
        self.start_timer()
        if self.network:
            self.lock_ui_if_needed()
            threading.Thread(target=self.network_listener, daemon=True).start()
        else:
            self.canvas.bind("<Button-1>", self.on_click)
        play_music()

    def setup_ui(self):
        from core.langues import translate
        header_background = "#e0e0e0"
        header_frame = tk.Frame(self.root, bg=header_background, height=80)
        header_frame.pack(side="top", fill="x")
        title_label = tk.Label(header_frame, text="Congress", font=("Arial", 22, "bold"), bg=header_background, fg="#5b7fce")
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
        self.update_player_info()
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
        self.turn_label = tk.Label(self.main_frame, text="", font=("Helvetica", 13, "bold"), bg="#f0f0f0", fg="#003366")
        self.turn_label.place(relx=0.50, rely=0.08, anchor="center")
        self.timer_label = tk.Label(self.main_frame, text="00:00", font=("Helvetica", 13, "bold"), bg="#f0f0f0", fg="#003366")
        self.timer_label.place(relx=0.50, rely=0.15, anchor="center")
        self.canvas = tk.Canvas(self.main_frame, width=400, height=400, bg="#f0f0f0", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.55, anchor="center")
        self.update_player_info()
        self.display_board()
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.update_idletasks()
        self.root.update()

    def redraw_ui_only(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_ui()
        self.update_player_info()
        self.display_board()

    def lock_ui_if_needed(self):
        if not self.network:
            return
        my_symbol = 'X' if self.is_host else 'O'
        if (self.turn % 2 == 0 and my_symbol != 'X') or (self.turn % 2 == 1 and my_symbol != 'O'):
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

    def play(self):
        if self.mode == "ia" and self.turn % 2 == 1:
            self.root.after(500, self.play_ai_move)
        self.root.mainloop()

    def play_ai_move(self):
        symbol = self.players[self.turn % 2].symbol
        possible_pawns = []
        for pawn in self.pieces[symbol]:
            color = self.board.cells[pawn[0]][pawn[1]]
            moves = self.generate_possible_moves(pawn, color, symbol)
            if moves:
                possible_pawns.append((pawn, list(moves)))
        if not possible_pawns:
            return
        pawn, moves = random.choice(possible_pawns)
        destination = random.choice(moves)
        self.pieces[symbol].remove(pawn)
        self.pieces[symbol].add(destination)
        self.selection = None
        self.possible_moves = set()
        self.turn += 1
        self.update_player_info()
        self.display_board()
        self.check_victory()
        if self.mode == "ia" and self.turn % 2 == 1:
            self.root.after(500, self.play_ai_move)

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
        return self.players[self.turn % 2]

    def update_player_info(self):
        from core.langues import translate
        color = 'black' if self.turn % 2 == 0 else 'white'
        name = self.player_names[self.turn % 2] if self.player_names else f"Player {translate(color)}"
        self.turn_label.config(text=f"{translate('turn_of')} ({translate(color)})")

    def display_board(self):
        self.canvas.delete("all")
        size = 50
        colors = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}
        for row_index in range(8):
            for col_index in range(8):
                color = self.board.cells[row_index][col_index]
                fill = colors.get(color, 'white')
                self.canvas.create_rectangle(col_index*size, row_index*size, (col_index+1)*size, (row_index+1)*size, fill=fill)
                if self.selection == (row_index, col_index):
                    self.canvas.create_rectangle(col_index*size, row_index*size, (col_index+1)*size, (row_index+1)*size, outline='blue', width=3)
                if hasattr(self, 'possible_moves') and (row_index, col_index) in getattr(self, 'possible_moves', set()):
                    self.canvas.create_oval(col_index*size+20, row_index*size+20, (col_index+1)*size-20, (row_index+1)*size-20, fill='lightgreen')
        for symbol, color in [('X', 'black'), ('O', 'white')]:
            for (row_index, col_index) in self.pieces[symbol]:
                self.canvas.create_oval(col_index*size+10, row_index*size+10, (col_index+1)*size-10, (row_index+1)*size-10, fill=color)

    def on_click(self, event):
        if self.mode == "ia" and self.turn % 2 == 1:
            return
        row_index, col_index = event.y // 50, event.x // 50
        player, symbol = self.get_current_player(), self.get_current_player().symbol
        position = (row_index, col_index)
        if self.selection is None:
            if position in self.pieces[symbol]:
                self.selection = position
                start_color = self.board.cells[self.selection[0]][self.selection[1]]
                self.possible_moves = self.generate_possible_moves(self.selection, start_color, symbol)
                self.display_board()
        else:
            if position in getattr(self, 'possible_moves', set()):
                from_pos = self.selection
                self.pieces[symbol].remove(self.selection)
                self.pieces[symbol].add(position)
                self.selection = None
                self.possible_moves = set()
                self.turn += 1
                self.update_player_info()
                self.display_board()
                self.check_victory()
                if self.network:
                    self.send_move(from_pos, position)
                    self.lock_ui_if_needed()
            else:
                self.selection = None
                self.possible_moves = set()
                self.display_board()

    def apply_network_move(self, from_pos, to_pos):
        player, symbol = self.get_current_player(), self.get_current_player().symbol
        self.pieces[symbol].remove(from_pos)
        self.pieces[symbol].add(to_pos)
        self.selection = None
        self.possible_moves = set()
        self.turn += 1
        self.update_player_info()
        self.display_board()
        self.check_victory()
        if self.network:
            self.lock_ui_if_needed()

    def check_victory(self):
        player = self.get_current_player()
        symbol = player.symbol
        positions = self.pieces[symbol]
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
                neighbor = (pos[0]+dx, pos[1]+dy)
                if neighbor in positions and neighbor not in visited:
                    queue.append(neighbor)
        if len(visited) == len(positions):
            self.pause_timer()
            color = 'White' if player.symbol == 'X' else 'Black'
            from core.langues import translate
            messagebox.showinfo(translate("victory"), f"{translate('player')} {translate(color.lower())} {translate('won')}")
            self.pause_timer()
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
        help_window = tk.Toplevel(self.root)
        help_window.title(translate("game_rules"))
        help_window.geometry("400x400")
        help_window.configure(bg="#f0f4f8")

        tk.Label(help_window, text=translate("congress_rules"), font=("Helvetica", 14, "bold"), bg="#f4f4f8", fg="#003366").pack(pady=10)
        text_widget = tk.Text(help_window, wrap="word", bg="#f0f4f8", fg="#000000", font=("Helvetica", 10), bd=0)
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", get_rules("congress"))
        text_widget.configure(state="disabled")

        def on_close():
            self.pause_timer()
            help_window.destroy()

        help_window.protocol("WM_DELETE_WINDOW", on_close)

    def return_to_menu(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass
        for w in self.root.winfo_children():
            w.destroy()
        import config_gui
        config_gui.afficher_interface_choix(self.root)

    def restart_game(self):
        self.timer_running = False
        if hasattr(self, "timer_id"):
            try:
                self.root.after_cancel(self.timer_id)
            except Exception:
                pass

        self.pieces = {
            'X': set([(0,1), (0,4), (1,7), (3,0), (4,7), (6,0), (7,3), (7,6)]),
            'O': set([(0,3), (0,6), (1,0), (3,7), (4,0), (6,7), (7,1), (7,4)])
        }
        self.turn = 0
        self.timer_seconds = 0
        self.selection = None
        self.possible_moves = set()
        self.redraw_ui_only()
        self.start_timer()

    def generate_possible_moves(self, start, color, symbol):
        return generate_possible_moves(start, color, symbol, self.board, self.pieces, capture=False)

def plateau_to_str(plateau):
    return '\n'.join([''.join(row) for row in plateau.cells])

def pions_to_str(pions):
    return '|'.join([f"{symb}:{';'.join([f'{i},{j}' for (i,j) in positions])}" for symb, positions in pions.items()])

def str_to_plateau(board_str):
    from core.plateau import Board
    lines = board_str.strip().split('\n')
    board = Board()
    board.cells = [list(line) for line in lines]
    return board

def str_to_pions(pieces_str):
    pions = {'X': set(), 'O': set()}
    for part in pieces_str.split('|'):
        if not part: continue
        symb, positions = part.split(':')
        if positions:
            pions[symb] = set(tuple(map(int, pos.split(','))) for pos in positions.split(';') if pos)
    return pions

def launch_network_game(root, is_host, player_name_white, player_name_black, sock, board=None, pieces=None, wait_win=None):
    import threading
    if is_host:
        sock.sendall(f"name:{player_name_white}".encode())
        data = sock.recv(4096)
        player_name_black = data.decode()[4:]
        if board is None or pieces is None:
            from plateau_builder import create_board
            board = create_board()
            pieces = {'X': set(), 'O': set()}
            pieces['X'].update([(0,1), (0,4), (1,7), (3,0), (4,7), (6,0), (7,3), (7,6)])
            pieces['O'].update([(0,3), (0,6), (1,0), (3,7), (4,0), (6,7), (7,1), (7,4)])
        board_str = plateau_to_str(board)
        pieces_str = pions_to_str(pieces)
        sock.sendall((board_str + '\nENDPLATEAU\n').encode())
        sock.sendall((pieces_str + '\nENDPIONS\n').encode())
        players = [Player(player_name_white, 'X'), Player(player_name_black, 'O')]
        game = GameCongress(board, players, mode="network", sock=sock, is_host=is_host, player_names=[player_name_white, player_name_black], root=root)
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
                game = GameCongress(board_local, players, mode="network", sock=sock, is_host=is_host, player_names=[player_name_white_local, player_name_black], root=root)
                game.pieces = pieces_local
                game.display_board()
                game.play()
            root.after(0, start_game)
        threading.Thread(target=client_receive_and_start, daemon=True).start()
