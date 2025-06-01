import tkinter as tk
from PIL import Image, ImageTk
import os
import random
from core.langues import translate

from core.plateau import Board
from core.joueur import Player
from jeux.katarenga import GameKatarenga
from jeux.congress import GameCongress
from jeux.isolation import GameIsolation

try:
    from core.quadrants import charger_quadrants_personnalises as load_custom_quadrants
except ImportError:
    load_custom_quadrants = None

def create_board():
    color_choices = ['R', 'J', 'B', 'V']
    board = Board()
    board.cells = [[random.choice(color_choices) for _ in range(8)] for _ in range(8)]
    return board

def create_header(root_window, username, on_submenu_click):
    header_background = "#e0e0e0"
    header_frame = tk.Frame(root_window, bg=header_background, height=80)
    header_frame.pack(side="top", fill="x")
    welcome_label = tk.Label(header_frame, text=f"{translate('welcome')} {username if username else ''}", font=("Arial", 22, "bold"), bg=header_background, fg="#5b7fce")
    welcome_label.pack(side="left", padx=32, pady=18)
    icon_image_path = os.path.join("assets", "lyrique.png")
    icon_image_pil = Image.open(icon_image_path).convert("RGBA").resize((40, 40))
    icon_photo = ImageTk.PhotoImage(icon_image_pil)
    submenu_button = tk.Button(header_frame, image=icon_photo, bg=header_background, bd=0, relief="flat", cursor="hand2", activebackground=header_background, highlightthickness=0)
    submenu_button.image = icon_photo
    submenu_button.pack(side="right", padx=28, pady=12)
    submenu_button.bind("<Button-1>", on_submenu_click)
    return header_frame, submenu_button

def create_submenu(root_window):
    from tkinter import messagebox
    def show_logout_menu(event):
        menu = tk.Menu(root_window, tearoff=0)
        menu.add_command(label=translate("about"), command=lambda: messagebox.showinfo(translate("about"), translate("about_text")))
        menu.add_command(label=translate("credits"), command=lambda: messagebox.showinfo(translate("credits"), translate("credits_text")))
        menu.add_separator()
        def go_to_login():
            import login
            try:
                current_volume = root_window.volume_var.get()
            except AttributeError:
                try:
                    from core.musique import SoundBar
                    current_volume = SoundBar.last_volume
                except Exception:
                    current_volume = None
            for widget in root_window.winfo_children():
                widget.destroy()
            login.show_login(root_window, volume=current_volume)
        menu.add_command(label=translate("logout"), command=go_to_login)
        menu.add_command(label=translate("close"), command=root_window.quit)
        menu.tk_popup(event.x_root, event.y_root)
    return show_logout_menu

def setup_soundbar_and_language_selector(root_window, soundbar_callback=None, lang_callback=None):
    from core.musique import set_volume, SoundBar
    from core.parametres import LanguageSelector
    transmitted_volume = getattr(root_window, 'VOLUME', None)
    initial_volume = 50
    if hasattr(root_window, 'volume_var'):
        try:
            initial_volume = root_window.volume_var.get()
        except Exception:
            pass
    elif transmitted_volume is not None:
        initial_volume = transmitted_volume
    if hasattr(root_window, 'volume_var'):
        root_window.volume_var.set(initial_volume)
        soundbar = SoundBar(root_window, volume_var=root_window.volume_var)
    else:
        root_window.volume_var = tk.IntVar(value=initial_volume)
        soundbar = SoundBar(root_window, volume_var=root_window.volume_var)
    set_volume(root_window.volume_var.get())
    soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)
    lang_selector = None
    if lang_callback is not None:
        lang_selector = LanguageSelector(root_window, assets_dir="assets", callback=lang_callback)
        lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)
    if soundbar_callback:
        soundbar_callback(soundbar)
    return soundbar, lang_selector

def launch_board_builder(game_type, is_ai_mode=False, board_mode="auto", network_callback=None, root_window=None):
    if root_window is None:
        root_window = tk.Tk()
        owns_root = True
    else:
        owns_root = False
        for widget in root_window.winfo_children():
            widget.destroy()
    root_window.title("Board Preview")
    root_window.configure(bg="#f0f4f8")
    try:
        icon_image = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
        root_window.iconphoto(False, icon_image)
    except Exception:
        pass
    username = getattr(root_window, 'USERNAME', None)
    show_logout_menu = create_submenu(root_window)
    create_header(root_window, username, show_logout_menu)
    setup_soundbar_and_language_selector(root_window)

    if board_mode == "auto" or load_custom_quadrants is None:
        board = create_board()
    else:
        board = Board()
        quadrants = load_custom_quadrants(os.path.join("assets", "quadrants_custom"))
        quadrant_positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for quadrant_index, quadrant in enumerate(quadrants[:4]):
            if 'recto' in quadrant:
                block = quadrant['recto']
                for row_offset in range(4):
                    for col_offset in range(4):
                        board.cells[quadrant_positions[quadrant_index][0] + row_offset][quadrant_positions[quadrant_index][1] + col_offset] = block[row_offset][col_offset]
    def show_board_ui(root_window, game_type, board, is_ai_mode, board_mode, network_callback, volume, username):
        for widget in root_window.winfo_children():
            widget.destroy()
        show_logout_menu = create_submenu(root_window)
        create_header(root_window, username, show_logout_menu)
        def on_language_changed(selected_language):
            try:
                current_volume = root_window.volume_var.get()
            except Exception:
                current_volume = 50
            import importlib
            import core.langues
            importlib.reload(core.langues)
            show_board_ui(root_window, game_type, board, is_ai_mode, board_mode, network_callback, current_volume, username)
        setup_soundbar_and_language_selector(root_window, lang_callback=on_language_changed)
        main_frame = tk.Frame(root_window, bg="#f0f4f0")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        if hasattr(root_window, 'label_board_generated') and root_window.label_board_generated.winfo_exists():
            root_window.label_board_generated.destroy()
        root_window.label_board_generated = tk.Label(main_frame, text=translate("generated_board"), font=("Helvetica", 16, "bold"), bg="#f0f4f0")
        root_window.label_board_generated.pack(pady=10)
        canvas = tk.Canvas(main_frame, width=400, height=400, bg="#f0f4f0", highlightthickness=0)
        canvas.pack()
        cell_size = 50
        for row_index in range(8):
            for col_index in range(8):
                color_code = board.cells[row_index][col_index] if hasattr(board, 'cells') else board.get_cell(row_index, col_index)
                fill = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}.get(color_code, 'white')
                canvas.create_rectangle(col_index*cell_size, row_index*cell_size, (col_index+1)*cell_size, row_index*cell_size + cell_size, fill=fill, outline="black")
        def launch_game():
            for widget in root_window.winfo_children():
                widget.destroy()
            if network_callback:
                network_callback(board, None)
            else:
                players = [Player(0, 'X'), Player(1, 'O')]
                mode = "ia" if is_ai_mode else "1v1"
                if game_type == "katarenga":
                    GameKatarenga(board, players, mode=mode, root=root_window).play()
                elif game_type == "congress":
                    GameCongress(board, players, mode=mode, root=root_window).play()
                elif game_type == "isolation":
                    GameIsolation(board, players, mode=mode, root=root_window).play()
        buttons_frame = tk.Frame(main_frame, bg="#f0f4f0")
        buttons_frame.pack(pady=15)
        play_button = tk.Button(buttons_frame, text=translate("play"), command=launch_game, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), width=15, relief="flat")
        play_button.pack(side="left", padx=5)
        def back_to_config():
            import config_gui
            for widget in root_window.winfo_children():
                widget.destroy()
            username = getattr(root_window, 'USERNAME', None)
            config_gui.main(root_window, game_type, username=username, volume=volume)
        back_icon_image = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
        back_icon_photo = ImageTk.PhotoImage(back_icon_image)
        back_button = tk.Button(root_window, image=back_icon_photo, command=back_to_config, bg="#f0f4f8", bd=0, relief="flat", cursor="hand2", activebackground="#e0e0e0")
        back_button.image = back_icon_photo
        back_button.place(relx=0.0, rely=0.5, anchor="w", x=18)

    try:
        initial_volume = root_window.volume_var.get()
    except Exception:
        initial_volume = 50
    show_board_ui(root_window, game_type, board, is_ai_mode, board_mode, network_callback, initial_volume, username)
    if owns_root:
        root_window.mainloop()
