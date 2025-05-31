import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
from functools import partial
from core.langues import translate
from core.parametres import get_assets_dir

ASSETS_DIR = get_assets_dir()
CURRENT_USERNAME = None

def set_username(username):
    global CURRENT_USERNAME
    CURRENT_USERNAME = username

def show_menu(root_window=None, username=None, volume=None):
    if username:
        set_username(username)
    root_window = root_window or tk.Tk()
    root_window.geometry("900x800")
    root_window.configure(bg="#f0f0f0")
    for widget in root_window.winfo_children():
        widget.destroy()

    header_background = "#e0e0e0"
    header_frame = tk.Frame(root_window, bg=header_background, height=80)
    header_frame.pack(side="top", fill="x")

    welcome_label = tk.Label(header_frame, text=f"{translate('welcome')} {CURRENT_USERNAME}", font=("Arial", 22, "bold"), bg=header_background, fg="#5b7fce")
    welcome_label.pack(side="left", padx=32, pady=18)

    icon_image = Image.open(os.path.join(ASSETS_DIR, "lyrique.png")).convert("RGBA").resize((40, 40))
    icon_photo = ImageTk.PhotoImage(icon_image)
    
    submenu_button = tk.Button(header_frame, image=icon_photo, bg=header_background, bd=0, relief="flat", cursor="hand2", activebackground=header_background, highlightthickness=0)
    submenu_button.image = icon_photo
    submenu_button.pack(side="right", padx=28, pady=12)

    from tkinter import messagebox
    def import_login_and_show(root_window):
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

    def show_logout_menu(event):
        menu = tk.Menu(root_window, tearoff=0)
        menu.add_command(label=translate("about"), command=lambda: messagebox.showinfo(translate("about"), translate("about_text")))
        menu.add_command(label=translate("credits"), command=lambda: messagebox.showinfo(translate("credits"), translate("credits_text")))
        menu.add_separator()
        menu.add_command(label=translate("logout"), command=lambda: import_login_and_show(root_window))
        menu.add_command(label=translate("close"), command=root_window.quit)
        menu.tk_popup(event.x_root, event.y_root)
    
    submenu_button.bind("<Button-1>", show_logout_menu)

    body_frame = tk.Frame(root_window, bg="#f0f0f0")
    body_frame.pack(expand=True, fill="both")
    body_frame.grid_rowconfigure(0, weight=1)
    body_frame.grid_columnconfigure((0,1,2), weight=1)

    center_frame = tk.Frame(body_frame, bg="#f0f0f0")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    game_modes = [
        ("Katarenga", "#e0e0e0", translate("katarenga_description"), "katarenga.png"),
        ("Congress", "#e0e0e0", translate("congress_description"), "congress.png"),
        ("Isolation", "#e0e0e0", translate("isolation_description"), "isolation.png")
    ]

    mode_frames = []
    
    for mode_index, (mode_name, background_color, description, image_filename) in enumerate(game_modes):
        mode_frame = tk.Frame(center_frame, bg=background_color, bd=0, relief="ridge", height=330, width=260)
        mode_frame.grid(row=0, column=mode_index, padx=24, pady=0, sticky="nsew")
        mode_frames.append(mode_frame)
        mode_label = tk.Label(mode_frame, text=mode_name, font=("Arial", 16, "bold"), bg=background_color, fg="#5b7fce", anchor="center")
        mode_label.pack(pady=(8, 0), fill="x")

        image_path = os.path.join(ASSETS_DIR, image_filename)
        
        game_image = Image.open(image_path).convert("RGBA").resize((150, 150))
        game_icon = ImageTk.PhotoImage(game_image)
        
        image_label = tk.Label(mode_frame, image=game_icon, bg=background_color)
        image_label.image = game_icon
        image_label.pack(pady=(2, 0))
        
        description_label = tk.Label(mode_frame, text=description, font=("Arial", 10), bg=background_color, fg="#444", wraplength=180, anchor="center")
        description_label.pack(pady=(2, 0), fill="x")
        
        spacer_label = tk.Label(mode_frame, bg=background_color)
        spacer_label.pack(expand=True, fill="both")
        
        def play_from_menu(selected_mode):
            from config_gui import main as config_main
            requested_game = selected_mode.lower()
            for widget in root_window.winfo_children():
                widget.destroy()
            config_main(root_window, requested_game, username=CURRENT_USERNAME, volume=root_window.volume_var.get())
        
        play_button = tk.Button(mode_frame, text=translate("play"), font=("Arial", 11, "bold"), bg="#219150", fg="white",
                             relief="flat", cursor="hand2", bd=0,
                             highlightthickness=1, highlightbackground="#19713c",
                             activebackground="#19713c", activeforeground="white",
                             command=lambda m=mode_name: play_from_menu(m))
        play_button.pack(pady=(6, 12), fill="x", side="bottom")
        mode_frame.pack_propagate(False)

    center_frame.grid_rowconfigure(0, weight=1)
    for mode_index in range(len(game_modes)):
        center_frame.grid_columnconfigure(mode_index, weight=1)

    """Sound bar"""
    from core.musique import set_volume, SoundBar
    from core.parametres import LanguageSelector
    if hasattr(root_window, 'volume_var'):
        root_window.volume_var.set(volume if volume is not None else root_window.volume_var.get())
        soundbar = SoundBar(root_window, volume_var=root_window.volume_var)
    else:
        root_window.volume_var = tk.IntVar(value=volume if volume is not None else 50)
        soundbar = SoundBar(root_window, volume_var=root_window.volume_var)
    set_volume(root_window.volume_var.get())
    soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

    """Language"""
    def on_language_changed(new_language):
        try:
            current_volume = soundbar.volume_var.get()
        except Exception:
            current_volume = volume
        import importlib
        import core.langues
        importlib.reload(core.langues)
        show_menu(root_window, username=CURRENT_USERNAME, volume=current_volume)
    lang_selector = LanguageSelector(root_window, assets_dir=ASSETS_DIR, callback=on_language_changed)
    lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

    root_window.title(translate("title"))
    if not getattr(root_window, 'initialized', False):
        root_window.initialized = True
        root_window.mainloop()

def logout(root_window):
    import login
    from core.musique import SoundBar, set_volume
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
