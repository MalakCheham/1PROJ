import tkinter as tk
import random
from PIL import Image, ImageTk
import os

from core.plateau import Plateau
from core.joueur import Joueur
from jeux.katarenga import JeuKatarenga
from jeux.congress import JeuCongress
from jeux.isolation import JeuIsolation

try:
    from core.quadrants import charger_quadrants_personnalises
except ImportError:
    charger_quadrants_personnalises = None

def creer_plateau():
    couleurs = ['R', 'J', 'B', 'V']
    plateau = Plateau()
    plateau.cases = [[random.choice(couleurs) for _ in range(8)] for _ in range(8)]
    return plateau

def lancer_plateau_builder(type_jeu, mode_ia=False, plateau_mode="auto", network_callback=None, root=None):
    if root is None:
        root = tk.Tk()
        own_root = True
    else:
        own_root = False
        for widget in root.winfo_children():
            widget.destroy()
    root.title("Aperçu du Plateau")
    root.configure(bg="#f0f4f8")

    try:
        icon_img = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
        root.iconphoto(False, icon_img)
    except:
        pass

    """entête"""
    header_bg = "#e0e0e0"
    header = tk.Frame(root, bg=header_bg, height=80)
    header.pack(side="top", fill="x")
    from core.langues import translate
    username = getattr(root, 'USERNAME', None)
    bienvenue = tk.Label(header, text=f"{translate('welcome')} {username if username else ''}", font=("Arial", 22, "bold"), bg=header_bg, fg="#5b7fce")
    bienvenue.pack(side="left", padx=32, pady=18)
    img = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
    icon = ImageTk.PhotoImage(img)
    btn_icon = tk.Button(header, image=icon, bg=header_bg, bd=0, relief="flat", cursor="hand2", activebackground=header_bg, highlightthickness=0)
    btn_icon.image = icon
    btn_icon.pack(side="right", padx=28, pady=12)

    """Sous menu"""
    from tkinter import messagebox
    def show_logout_menu(event):
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label=translate("about"), command=lambda: messagebox.showinfo(translate("about"), translate("about_text")))
        menu.add_command(label=translate("credits"), command=lambda: messagebox.showinfo(translate("credits"), translate("credits_texte")))
        menu.add_separator()
        def go_to_login():
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
        menu.add_command(label=translate("logout"), command=go_to_login)
        menu.add_command(label=translate("close"), command=root.quit)
        menu.tk_popup(event.x_root, event.y_root)
    btn_icon.bind("<Button-1>", show_logout_menu)

    """Gestion son + langues"""
    from core.musique import set_volume, SoundBar
    from core.parametres import LanguageSelector
    volume_transmis = getattr(root, 'VOLUME', None)
    initial_volume = 50
    if hasattr(root, 'volume_var'):
        try:
            initial_volume = root.volume_var.get()
        except Exception:
            pass
    elif volume_transmis is not None:
        initial_volume = volume_transmis
    if hasattr(root, 'volume_var'):
        root.volume_var.set(initial_volume)
        soundbar = SoundBar(root, volume_var=root.volume_var)
    else:
        root.volume_var = tk.IntVar(value=initial_volume)
        soundbar = SoundBar(root, volume_var=root.volume_var)
    set_volume(root.volume_var.get())
    soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

    """Show UI sans génération de plateau"""
    def afficher_plateau_ui(root, type_jeu, plateau, mode_ia, plateau_mode, network_callback, volume, username):
        
        for widget in root.winfo_children():
            widget.destroy()
        """En-tête"""
        header_bg = "#e0e0e0"
        header = tk.Frame(root, bg=header_bg, height=80)
        header.pack(side="top", fill="x")
        from core.langues import translate
        bienvenue = tk.Label(header, text=f"{translate('welcome')} {username if username else ''}", font=("Arial", 22, "bold"), bg=header_bg, fg="#5b7fce")
        bienvenue.pack(side="left", padx=32, pady=18)
        img = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
        icon = ImageTk.PhotoImage(img)
        btn_icon = tk.Button(header, image=icon, bg=header_bg, bd=0, relief="flat", cursor="hand2", activebackground=header_bg, highlightthickness=0)
        btn_icon.image = icon
        btn_icon.pack(side="right", padx=28, pady=12)

        """Sous menu"""
        from tkinter import messagebox
        def show_logout_menu(event):
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label=translate("about"), command=lambda: messagebox.showinfo(translate("about"), translate("about_text")))
            menu.add_command(label=translate("credits"), command=lambda: messagebox.showinfo(translate("credits"), translate("credits_texte")))
            menu.add_separator()
            def go_to_login():
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
            menu.add_command(label=translate("logout"), command=go_to_login)
            menu.add_command(label=translate("close"), command=root.quit)
            menu.tk_popup(event.x_root, event.y_root)
        btn_icon.bind("<Button-1>", show_logout_menu)

        """Barre de son"""
        from core.musique import SoundBar, set_volume
        from core.parametres import LanguageSelector
        if hasattr(root, 'volume_var'):
            soundbar = SoundBar(root, volume_var=root.volume_var)
        else:
            root.volume_var = tk.IntVar(value=50)
            soundbar = SoundBar(root, volume_var=root.volume_var)
        set_volume(root.volume_var.get())
        soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

        def on_language_changed(selected_language):
            try:
                current_volume = soundbar.volume_var.get()
            except Exception:
                current_volume = getattr(root, 'volume_var', tk.IntVar(value=50)).get()
            import importlib
            import core.langues
            importlib.reload(core.langues)
            afficher_plateau_ui(root, type_jeu, plateau, mode_ia, plateau_mode, network_callback, current_volume, username)

        lang_selector = LanguageSelector(root, assets_dir="assets", callback=on_language_changed)
        lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

        main_frame = tk.Frame(root, bg="#f0f4f0")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        if hasattr(root, 'label_plateau_genere') and root.label_plateau_genere.winfo_exists():
            root.label_plateau_genere.destroy()
        root.label_plateau_genere = tk.Label(main_frame, text=translate("generated_board"), font=("Helvetica", 16, "bold"), bg="#f0f4f0")
        root.label_plateau_genere.pack(pady=10)

        canvas = tk.Canvas(main_frame, width=400, height=400, bg="#f0f4f0", highlightthickness=0)
        canvas.pack()

        taille = 50
        for i in range(8):
            for j in range(8):
                couleur = plateau.cases[i][j] if hasattr(plateau, 'cases') else plateau.lire(i, j)
                fill = {'R': '#ff9999', 'J': '#ffffb3', 'B': '#99ccff', 'V': '#b3ffb3'}.get(couleur, 'white')
                canvas.create_rectangle(j*taille, i*taille, (j+1)*taille, i*taille + taille, fill=fill, outline="black")

        def lancer_partie():
            for widget in root.winfo_children():
                widget.destroy()
            if network_callback:
                network_callback(plateau, None)
            else:
                joueurs = [Joueur(0, 'X'), Joueur(1, 'O')]
                if type_jeu == "katarenga":
                    JeuKatarenga(plateau, joueurs, root=root).jouer()
                elif type_jeu == "congress":
                    JeuCongress(plateau, joueurs, root=root).jouer()
                elif type_jeu == "isolation":
                    JeuIsolation(plateau, joueurs, root=root).jouer()

        btns_frame = tk.Frame(main_frame, bg="#f0f4f0")
        btns_frame.pack(pady=15)
        btn = tk.Button(btns_frame, text=translate("play"), command=lancer_partie, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), width=15, relief="flat")
        btn.pack(side="left", padx=5)

        """Bouton retour"""
        def retour_config():
            import config_gui
            for w in root.winfo_children():
                w.destroy()
            username = getattr(root, 'USERNAME', None)
            config_gui.main(root, type_jeu, username=username, volume=volume)
        img_retour = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
        icon_retour = ImageTk.PhotoImage(img_retour)
        btn_retour = tk.Button(root, image=icon_retour, command=retour_config, bg="#f0f4f8", bd=0, relief="flat", cursor="hand2", activebackground="#e0e0e0")
        btn_retour.image = icon_retour
        btn_retour.place(relx=0.0, rely=0.5, anchor="w", x=18)

    """Génération du plateau"""
    if plateau_mode == "auto" or charger_quadrants_personnalises is None:
        plateau = creer_plateau()
    else:
        plateau = Plateau()
        quadrants = charger_quadrants_personnalises(os.path.join("assets", "quadrants_custom"))
        positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for i, q in enumerate(quadrants[:4]):
            if 'recto' in q:
                bloc = q['recto']
                for dx in range(4):
                    for dy in range(4):
                        plateau.cases[positions[i][0] + dx][positions[i][1] + dy] = bloc[dx][dy]
    

    afficher_plateau_ui(root, type_jeu, plateau, mode_ia, plateau_mode, network_callback, initial_volume, username)
    
    if own_root:
        root.mainloop()
