import tkinter as tk
from PIL import Image, ImageTk
import os
from functools import partial

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
USERNAME = None

def set_username(username):
    global USERNAME
    USERNAME = username

def show_menu(root=None, username=None, volume=None):
    if username:
        set_username(username)
    root = root or tk.Tk()
    root.geometry("900x800")
    root.configure(bg="#f0f0f0")
    for w in root.winfo_children():
        w.destroy()

    header_bg = "#e0e0e0" 
    header = tk.Frame(root, bg=header_bg, height=80)
    header.pack(side="top", fill="x")

    from core.langues import traduire
    bienvenue = tk.Label(header, text=f"{traduire('bienvenue')} {USERNAME}", font=("Arial", 22, "bold"), bg=header_bg, fg="#5b7fce")
    bienvenue.pack(side="left", padx=32, pady=18)

    """Icone sous menu"""
    img = Image.open(os.path.join(ASSETS_DIR, "lyrique.png")).convert("RGBA").resize((40, 40))
    icon = ImageTk.PhotoImage(img)
    btn_icon = tk.Button(header, image=icon, bg=header_bg, bd=0, relief="flat", cursor="hand2", activebackground=header_bg, highlightthickness=0)
    btn_icon.image = icon
    btn_icon.pack(side="right", padx=28, pady=12)

    from tkinter import messagebox
    def import_login_and_show(root):
        import login
        try:
            current_volume = root.volume_var.get()
        except AttributeError:
            try:
                from core.musique import SoundBar
                current_volume = SoundBar.last_volume
            except Exception:
                current_volume = None
        for w in root.winfo_children():
            w.destroy()
        login.show_login(root, volume=current_volume)

    """Sous menu"""
    def show_logout_menu(event):
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label=traduire("a_propos"), command=lambda: messagebox.showinfo(traduire("a_propos"), traduire("a_propos_texte")))
        menu.add_command(label=traduire("credits"), command=lambda: messagebox.showinfo(traduire("credits"), traduire("credits_texte")))
        menu.add_separator()
        menu.add_command(label=traduire("se_deconnecter"), command=lambda: import_login_and_show(root))
        menu.add_command(label=traduire("fermer"), command=root.quit)
        menu.tk_popup(event.x_root, event.y_root)
    btn_icon.bind("<Button-1>", show_logout_menu)

    body = tk.Frame(root, bg="#f0f0f0")
    body.pack(expand=True, fill="both")
    body.grid_rowconfigure(0, weight=1)
    body.grid_columnconfigure((0,1,2), weight=1)

    center_frame = tk.Frame(body, bg="#f0f0f0")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    """Choix des modes de jeu"""
    modes = [
        ("Kataranga", "#e0e0e0", traduire("desc_katarenga"), "katarenga.png"),
        ("Congress", "#e0e0e0", traduire("desc_congress"), "congress.png"),
        ("Isolation", "#e0e0e0", traduire("desc_isolation"), "isolation.png")
    ]
    frames = []
    for i, (mode, color, desc, img_file) in enumerate(modes):
        frame = tk.Frame(center_frame, bg=color, bd=0, relief="ridge", height=330, width=260)
        frame.grid(row=0, column=i, padx=24, pady=0, sticky="nsew")
        frames.append(frame)
        label = tk.Label(frame, text=mode, font=("Arial", 16, "bold"), bg=color, fg="#5b7fce", anchor="center")
        label.pack(pady=(8, 0), fill="x")

        img_path = os.path.join(ASSETS_DIR, img_file)
        game_img = Image.open(img_path).convert("RGBA").resize((150, 150))
        game_icon = ImageTk.PhotoImage(game_img)
        img_lbl = tk.Label(frame, image=game_icon, bg=color)
        img_lbl.image = game_icon
        img_lbl.pack(pady=(2, 0))
        
        desc_lbl = tk.Label(frame, text=desc, font=("Arial", 10), bg=color, fg="#444", wraplength=180, anchor="center")
        desc_lbl.pack(pady=(2, 0), fill="x")
        
        spacer = tk.Label(frame, bg=color)
        spacer.pack(expand=True, fill="both")
        
        def jouer_depuis_menu(mode):
            from config_gui import main as config_main
            jeu_demande = mode.lower()
            for w in root.winfo_children():
                w.destroy()
            config_main(root, jeu_demande, username=USERNAME, volume=volume)
        
        play_btn = tk.Button(frame, text=traduire("jouer"), font=("Arial", 11, "bold"), bg="#219150", fg="white",
                             relief="flat", cursor="hand2", bd=0,
                             highlightthickness=1, highlightbackground="#19713c",
                             activebackground="#19713c", activeforeground="white",
                             command=lambda m=mode: jouer_depuis_menu(m))
        play_btn.pack(pady=(6, 12), fill="x", side="bottom")
        frame.pack_propagate(False)

    center_frame.grid_rowconfigure(0, weight=1)
    for i in range(len(modes)):
        center_frame.grid_columnconfigure(i, weight=1)

    """Barre de son"""
    from core.musique import SoundBar, regler_volume
    from core.parametres import LanguageSelector
    if hasattr(root, 'volume_var'):
        root.volume_var.set(volume if volume is not None else root.volume_var.get())
        soundbar = SoundBar(root, volume_var=root.volume_var)
    else:
        root.volume_var = tk.IntVar(value=volume if volume is not None else 50)
        soundbar = SoundBar(root, volume_var=root.volume_var)
    regler_volume(root.volume_var.get())
    soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

    """Langues"""
    def on_language_changed(new_lang):
        try:
            current_volume = soundbar.volume_var.get()
        except Exception:
            current_volume = volume
        import importlib
        import core.langues
        importlib.reload(core.langues)
        show_menu(root, username=USERNAME, volume=current_volume)
    lang_selector = LanguageSelector(root, assets_dir=ASSETS_DIR, callback=on_language_changed)
    lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

    root.title(traduire("titre"))
    if not getattr(root, 'initialized', False):
        root.initialized = True
        root.mainloop()

def logout(root):
    import login
    from core.musique import regler_volume
    try:
        current_volume = root.volume_var.get()
    except AttributeError:
        try:
            from core.musique import SoundBar
            current_volume = SoundBar.last_volume
        except Exception:
            current_volume = None
    for w in root.winfo_children():
        w.destroy()
    login.show_login(root, volume=current_volume)
