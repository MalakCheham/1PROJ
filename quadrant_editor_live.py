import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from core.langues import translate
from core.musique import set_volume, SoundBar
from core.parametres import LanguageSelector

COLOR_CODES = ["R", "J", "B", "V"]
COLOR_HEX_CODES = {
    "R": "#ff9999", "J": "#ffffb3", "B": "#99ccff", "V": "#b3ffb3"
}

class QuadrantEditorLive:
    def __init__(self, root_window, on_back, on_network=None, requested_game=None, mode=None):
        self.root_window = root_window
        self.on_back = on_back
        self.on_network = on_network
        self.current_color = "R"
        self.quadrant_list = []
        self.grid_colors = [[None for _ in range(4)] for _ in range(4)]
        self.requested_game = requested_game if requested_game is not None else getattr(root_window, 'jeu_demande', None)
        self.mode = mode if mode is not None else getattr(root_window, 'mode', None) or "1v1"

        for widget in root_window.winfo_children():
            widget.destroy()
        root_window.configure(bg="#f0f4f8")

        self._create_header()
        self._setup_soundbar_and_language_selector()
        self._create_main_ui()
        self._create_back_button()

    def _create_header(self):
        header_background = "#e0e0e0"
        header_frame = tk.Frame(self.root_window, bg=header_background, height=80)
        header_frame.pack(side="top", fill="x")
        username = getattr(self.root_window, 'USERNAME', None)
        title_label = tk.Label(header_frame, text=translate("create_4x4_quadrant"), font=("Arial", 22, "bold"), bg=header_background, fg="#5b7fce")
        title_label.pack(side="left", padx=32, pady=18)
        icon_image = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
        icon_photo = ImageTk.PhotoImage(icon_image, master=self.root_window)
        self.header_icon = icon_photo
        icon_button = tk.Button(header_frame, image=self.header_icon, bg=header_background, bd=0, relief="flat", cursor="hand2", activebackground=header_background, highlightthickness=0)
        icon_button.image = self.header_icon
        icon_button.pack(side="right", padx=28, pady=12)
        icon_button.bind("<Button-1>", self._show_submenu)

    def _show_submenu(self, event):
        submenu = tk.Menu(self.root_window, tearoff=0)
        submenu.add_command(label=translate("about"), command=lambda: messagebox.showinfo(translate("about"), translate("about_text")))
        submenu.add_command(label=translate("credits"), command=lambda: messagebox.showinfo(translate("credits"), translate("credits_text")))
        submenu.add_separator()
        def go_to_login():
            import login
            try:
                current_volume = self.root_window.volume_var.get()
            except AttributeError:
                try:
                    current_volume = SoundBar.last_volume
                except Exception:
                    current_volume = None
            for widget in self.root_window.winfo_children():
                widget.destroy()
            login.show_login(self.root_window, volume=current_volume)
        submenu.add_command(label=translate("logout"), command=go_to_login)
        submenu.add_command(label=translate("close"), command=self.root_window.quit)
        submenu.tk_popup(event.x_root, event.y_root)

    def _setup_soundbar_and_language_selector(self):
        transmitted_volume = getattr(self.root_window, 'VOLUME', None)
        initial_volume = 50
        if hasattr(self.root_window, 'volume_var'):
            try:
                initial_volume = self.root_window.volume_var.get()
            except Exception:
                pass
            self.root_window.volume_var.set(initial_volume)
            soundbar = SoundBar(self.root_window, volume_var=self.root_window.volume_var)
        else:
            self.root_window.volume_var = tk.IntVar(value=initial_volume)
            soundbar = SoundBar(self.root_window, volume_var=self.root_window.volume_var)
        set_volume(self.root_window.volume_var.get())
        soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)
        def on_language_changed(new_language):
            import importlib
            import core.langues
            importlib.reload(core.langues)
            self.reload_ui()
        lang_selector = LanguageSelector(self.root_window, assets_dir="assets", callback=on_language_changed)
        lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

    def _create_main_ui(self):
        main_frame = tk.Frame(self.root_window, bg="#f0f4f8")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.grid_frame = tk.Frame(main_frame, bg="#f0f4f8")
        self.grid_frame.pack(pady=5)
        self.cell_buttons = [[None for _ in range(4)] for _ in range(4)]
        for row_index in range(4):
            for col_index in range(4):
                cell_button = tk.Button(self.grid_frame, text="", width=4, height=2)
                cell_button.grid(row=row_index, column=col_index, padx=2, pady=2)
                cell_button.bind("<Button-1>", lambda event, x=row_index, y=col_index: self.paint_cell(x, y, event))
                cell_button.bind("<Button-3>", lambda event, x=row_index, y=col_index: self.paint_cell(x, y, event))
                self.cell_buttons[row_index][col_index] = cell_button
        self.color_choice_frame = tk.Frame(main_frame, bg="#f0f4f8")
        self.color_choice_frame.pack(pady=10)
        self.color_buttons = {}
        for color_code in COLOR_CODES:
            color_button = tk.Button(self.color_choice_frame, bg=COLOR_HEX_CODES[color_code], width=4, height=2, command=lambda col=color_code: self.select_color(col))
            color_button.pack(side="left", padx=10)
            self.color_buttons[color_code] = color_button
        self.update_color_highlight()
        self.controls_frame = tk.Frame(main_frame, bg="#f0f4f8")
        self.controls_frame.pack(pady=10)
        save_button = tk.Button(self.controls_frame, text=translate("save_quadrant"), command=self.validate_quadrant, font=("Helvetica", 10), bg="#4CAF50", fg="white", padx=10, pady=5)
        new_button = tk.Button(self.controls_frame, text=translate("new_quadrant"), command=self.reset_quadrant, font=("Helvetica", 10), padx=10, pady=5)
        save_button.pack(side="left", padx=8)
        new_button.pack(side="left", padx=8)
        self.info_label = tk.Label(main_frame, text=translate("quadrant_num", num=1), font=("Helvetica", 12), bg="#f0f4f8")
        self.info_label.pack(pady=5)
        self.play_button = tk.Button(main_frame, text=translate("play_with_these_quadrants"), command=self.build_board, font=("Helvetica", 12, "bold"), bg="#0066cc", fg="white")
        self.play_button.pack(pady=10)
        self.play_button.config(state="disabled")

    def _create_back_button(self):
        back_image = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
        back_icon = ImageTk.PhotoImage(back_image, master=self.root_window)
        self.back_icon = back_icon
        back_button = tk.Button(self.root_window, image=self.back_icon, command=self.on_back, bg="#f0f4f8", bd=0, relief="flat", cursor="hand2", activebackground="#e0e0e0")
        back_button.image = self.back_icon
        back_button.place(relx=0.0, rely=0.5, anchor="w", x=18)

    def select_color(self, color_code):
        self.current_color = color_code
        self.update_color_highlight()

    def update_color_highlight(self):
        for color_code, button in self.color_buttons.items():
            if color_code == self.current_color:
                button.config(relief="solid", bd=4, highlightbackground="#333", highlightcolor="#333")
            else:
                button.config(relief="flat", bd=2, highlightbackground="#f0f4f8", highlightcolor="#f0f4f8")

    def paint_cell(self, row_index, col_index, event=None):
        if event is not None and event.num == 3:
            for x in range(4):
                for y in range(4):
                    self.cell_buttons[x][y].config(bg=COLOR_HEX_CODES[self.current_color])
                    self.grid_colors[x][y] = self.current_color
        else:
            self.cell_buttons[row_index][col_index].config(bg=COLOR_HEX_CODES[self.current_color])
            self.grid_colors[row_index][col_index] = self.current_color

    def validate_quadrant(self):
        if any(None in row for row in self.grid_colors):
            messagebox.showwarning(translate("incomplete"), translate("all_squares_colored"))
            return
        self.quadrant_list.append({"recto": [row[:] for row in self.grid_colors]})
        if len(self.quadrant_list) == 4:
            messagebox.showinfo("OK", translate("four_quadrants_ready"))
            self.play_button.config(state="normal")
        else:
            self.reset_quadrant()
            if hasattr(self, 'info_label'):
                self.info_label.config(text=translate("quadrant_num", num=len(self.quadrant_list)+1))

    def reset_quadrant(self):
        self.grid_colors = [[None for _ in range(4)] for _ in range(4)]
        for row_index in range(4):
            for col_index in range(4):
                self.cell_buttons[row_index][col_index].config(bg="SystemButtonFace")
        if hasattr(self, 'info_label'):
            self.info_label.config(text=translate("quadrant_num", num=len(self.quadrant_list)+1))

    def build_board(self):
        if len(self.quadrant_list) != 4:
            messagebox.showerror("Error", "You need 4 quadrants to build the board.")
            return
        from core.plateau import Board
        from core.joueur import Player
        from jeux.katarenga import GameKatarenga
        from jeux.congress import GameCongress
        from jeux.isolation import GameIsolation
        board = Board()
        quadrant_positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for quadrant_index, quadrant in enumerate(self.quadrant_list):
            block = quadrant["recto"]
            for row_offset in range(4):
                for col_offset in range(4):
                    board.cells[quadrant_positions[quadrant_index][0] + row_offset][quadrant_positions[quadrant_index][1] + col_offset] = block[row_offset][col_offset]
        
        player_pieces = {}
        if hasattr(self, 'requested_game') and self.requested_game == 'katarenga':
            player_pieces = {
                'X': {(1, col) for col in range(1, 9)},
                'O': {(8, col) for col in range(1, 9)}
            }
        else: 
            player_pieces = None

        players = [Player(0, 'X'), Player(1, 'O')]
        
        mode = self.mode
        if self.on_network:
            self.on_network(board, player_pieces)
        else:
            for widget in self.root_window.winfo_children():
                widget.destroy()
            if hasattr(self, 'requested_game') and self.requested_game == 'congress':
                GameCongress(board, players, mode=mode, root=self.root_window).play()
            elif hasattr(self, 'requested_game') and self.requested_game == 'isolation':
                GameIsolation(board, players, mode=mode, root=self.root_window).play()
            else:
                GameKatarenga(board, players, mode=mode, root=self.root_window).play()

    def reload_ui(self):
        for widget in self.root_window.winfo_children():
            widget.destroy()
        self.__init__(self.root_window, self.on_back, self.on_network, self.requested_game)
