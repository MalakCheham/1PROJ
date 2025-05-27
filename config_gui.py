import tkinter as tk
import sys
import subprocess
import pygame
import socket
import os

from plateau_builder import lancer_plateau_builder
from quadrant_editor_live import QuadrantEditorLive
from core.langues import traduire
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from core.network.game_network import host_server, join_server, start_discovery, stop_discovery
from core.musique import jouer_musique


"""Variables globales"""
dic_variables = {
    "jeu_demande": sys.argv[1] if len(sys.argv) > 1 else "katarenga",
    "network_mode": "local", 
    "client_socket": None,
    "mode": "1v1",
    "game_ready": False,
    "plateau_mode": "auto"
}

def center_window(win, width, height, root):
    win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def back_to_config(root):
    """Retourne à l'écran de choix principal."""
    for widget in root.winfo_children():
        widget.destroy()
    afficher_interface_choix(root)

def open_host_window(root):
    """Ouvre la fenêtre pour héberger une partie réseau"""
    name = simpledialog.askstring(traduire("heberger"), traduire("entrer_nom_serveur"), parent=root)
    if not name:
        return
    player_name = simpledialog.askstring(traduire("heberger"), traduire("entrer_nom_joueur"), parent=root)
    if not player_name:
        return
    dic_variables["host_name"] = name
    dic_variables["player_name"] = player_name
    dic_variables["is_host"] = True
    dic_variables["is_client"] = False
    dic_variables["network_mode"] = "reseau"
    dic_variables["game_ready"] = True
    update_go_button_state(root)

def open_network_window(root):
    """Ouvre la fenêtre pour choisir entre héberger ou rejoindre une partie réseau"""
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("choisir_mode_jeu"))
    center_window(fenetre, 300, 180, root)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(bg="#e0f7fa")
    tk.Label(fenetre, text=traduire("choisir_reseau"), font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=15)
    btn_host = tk.Button(fenetre, text=traduire("heberger"), font=("Helvetica", 12), width=15, command=lambda: [fenetre.destroy(), open_host_window(root)])
    btn_host.pack(pady=5)
    btn_join = tk.Button(fenetre, text=traduire("join_server"), font=("Helvetica", 12), width=15, command=lambda: [fenetre.destroy(), open_join_window(root)])
    btn_join.pack(pady=5)

def open_join_window(root):
    """Ouvre la fenêtre pour rejoindre une partie réseau existante"""
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("join_server"))
    center_window(fenetre, 350, 350, root)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(bg="#e0f7fa")
    tk.Label(fenetre, text=traduire("serveurs_disponibles"), font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=10)
    frame_list = tk.Frame(fenetre, bg="#e0f7fa")
    frame_list.pack(pady=5, fill="both", expand=True)
    serveurs = []
    btns = []
    def add_server(srv):
        serveurs.append(srv)
        btn = tk.Button(frame_list, text=f"{srv['nom']} ({srv['ip']}:{srv['port']})", font=("Helvetica", 12), width=30, anchor="w", command=lambda s=srv: join_server_ui(s, fenetre, root))
        btn.pack(pady=3)
        btns.append(btn)
    discovery = start_discovery(add_server)
    def on_close():
        stop_discovery()
        fenetre.destroy()
    fenetre.protocol("WM_DELETE_WINDOW", on_close)
    def refresh():
        for b in btns:
            b.destroy()
        btns.clear()
        serveurs.clear()
        if hasattr(discovery, 'found'):
            discovery.found.clear()
    tk.Button(fenetre, text=traduire("rafraichir"), command=refresh, bg="#b2ebf2").pack(pady=5)

def start_network_game(root, is_host, player_name=None, player_name_noir=None, sock=None, plateau=None, pions=None):
    """Lance la partie réseau avec les bons paramètres"""
    for widget in root.winfo_children():
        widget.destroy()
    if is_host:
        player_name_blanc = player_name
        player_name_noir = None
    else:
        player_name_blanc = None
        player_name_noir = player_name_noir or player_name
    if dic_variables["jeu_demande"] == "katarenga":
        from jeux.katarenga import lancer_jeu_reseau
        lancer_jeu_reseau(root, is_host=is_host, player_name_blanc=player_name_blanc, player_name_noir=player_name_noir, sock=sock, plateau=plateau, pions=pions)
    elif dic_variables["jeu_demande"] == "isolation":
        from jeux.isolation import lancer_jeu_reseau
        lancer_jeu_reseau(root, is_host=is_host, player_name_blanc=player_name_blanc, player_name_noir=player_name_noir, sock=sock, plateau=plateau, pions=pions)
    elif dic_variables["jeu_demande"] == "congress":
        from jeux.congress import lancer_jeu_reseau
        lancer_jeu_reseau(root, is_host=is_host, player_name_blanc=player_name_blanc, player_name_noir=player_name_noir, sock=sock, plateau=plateau, pions=pions)
    else:
        tk.Label(root, text="Mode réseau non implémenté pour ce jeu.", font=("Helvetica", 15, "bold"), fg="#d32f2f", bg="#e6f2ff").pack(pady=60)

def join_server_ui(server, fenetre, root):
    """Demande le nom du joueur puis tente de rejoindre le serveur sélectionné"""
    fenetre.destroy()
    player_name = simpledialog.askstring(traduire("join_server"), traduire("entrer_nom_joueur"), parent=root)
    if not player_name:
        return
    ip = server['ip']
    port = server.get('port', 5555)
    sock = join_server(ip, port)
    if sock:
        dic_variables["game_ready"] = True
        update_go_button_state(root)
        start_network_game(root, is_host=False, player_name=player_name, sock=sock)
    else:
        messagebox.showerror(traduire("join_server"), f"{traduire('tentative_connexion')} {server['nom']} ({ip})\n{traduire('connection_failed')}")
        dic_variables["game_ready"] = False
        update_go_button_state(root)

def update_go_button_state(root):
    """Active ou désactive le bouton 'Jouer' selon les choix de l'utilisateur"""
    btn = dic_variables.get("play_btn")
    if not btn:
        return
    if dic_variables["mode"] == "ia":
        btn.config(state="normal", bg="#4CAF50")
    elif dic_variables["mode"] == "1v1":
        if dic_variables["network_mode"] == "local":
            btn.config(state="normal", bg="#4CAF50")
        elif dic_variables["network_mode"] == "reseau":
            btn.config(state="normal", bg="#4CAF50")
        else:
            btn.config(state="disabled", bg="#888888")
    else:
        btn.config(state="disabled", bg="#888888")
    mode_label = dic_variables.get("mode_label")
    if not mode_label:
        mode_label = tk.Label(root, font=("Helvetica", 11, "italic"), bg="#e6f2ff", fg="#004d40")
        mode_label.pack()
        dic_variables["mode_label"] = mode_label
    if dic_variables["network_mode"] == "local":
        mode_label.config(text=traduire("mode_solo"))
    elif dic_variables["network_mode"] == "reseau":
        if dic_variables.get("is_host"):
            mode_label.config(text=traduire("mode_reseau_hote"))
        elif dic_variables.get("is_client"):
            mode_label.config(text=traduire("mode_reseau_client"))
        else:
            mode_label.config(text=traduire("mode_reseau"))
    else:
        mode_label.config(text="Mode : ?")

def play(root):
    """Lance la partie selon les choix de l'utilisateur"""
    if dic_variables["network_mode"] == "reseau" and dic_variables.get("is_host"):
        def lancer_partie_reseau(plateau=None, pions=None):
            from core.network.game_network import host_server
            def on_client_connect(attente_win, client_socket, addr):
                attente_win.destroy()
                root.after(0, lambda: start_network_game(root, is_host=True, player_name=dic_variables.get("host_name"), sock=client_socket, plateau=plateau, pions=pions))
            def on_stop(attente_win):
                attente_win.destroy()
                messagebox.showinfo(traduire("heberger"), traduire("serveur_arrete"))
                dic_variables["game_ready"] = False
                update_go_button_state(root)
            host_server(
                server_name=dic_variables.get("host_name","Serveur"),
                on_client_connect=on_client_connect,
                on_stop=on_stop,
                root=root,
                tk=tk,
                traduire=traduire,
                center_window=lambda win, w, h: center_window(win, w, h, root)
            )
        if dic_variables["plateau_mode"] == "auto":
            def on_lancer_partie(plateau, pions):
                lancer_partie_reseau(plateau, pions)
            lancer_plateau_builder(dic_variables["jeu_demande"], False, "auto", on_lancer_partie, root)
        else:
            QuadrantEditorLive(root, retour_callback=lambda: back_to_config(root), network_callback=lancer_partie_reseau)
    elif dic_variables["network_mode"] == "reseau" and dic_variables.get("is_client"):
        start_network_game(root, is_host=False, player_name=dic_variables.get("player_name"), sock=dic_variables.get("client_socket"))
    else:
        if dic_variables["plateau_mode"] == "auto":
            for widget in root.winfo_children():
                widget.destroy()
            lancer_plateau_builder(dic_variables["jeu_demande"], dic_variables["mode"] == "ia", dic_variables["plateau_mode"], None, root)
        elif dic_variables["plateau_mode"] == "perso":
            for widget in root.winfo_children():
                widget.destroy()
            QuadrantEditorLive(root, retour_callback=lambda: back_to_config(root))

def open_mode_choice_window(root):
    """Ouvre la fenêtre pour choisir entre solo et réseau"""
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("choisir_mode_jeu"))
    center_window(fenetre, 300, 180, root)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(bg="#e0f7fa")
    def set_local():
        dic_variables["network_mode"] = "local"
        dic_variables["is_host"] = False
        dic_variables["is_client"] = False
        dic_variables["game_ready"] = True
        update_go_button_state(root)
        fenetre.destroy()
    def set_reseau():
        dic_variables["network_mode"] = "reseau"
        dic_variables["is_host"] = False
        dic_variables["is_client"] = False
        dic_variables["game_ready"] = False
        update_go_button_state(root)
        fenetre.destroy()
        open_network_window(root)
    tk.Label(fenetre, text=traduire("choisir_mode_jeu"), font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=15)
    btn_solo = tk.Button(fenetre, text=traduire("mode_solo"), font=("Helvetica", 12), width=15, command=set_local)
    btn_solo.pack(pady=5)
    btn_reseau = tk.Button(fenetre, text=traduire("mode_reseau"), font=("Helvetica", 12), width=15, command=set_reseau)
    btn_reseau.pack(pady=5)

def afficher_interface_choix(root):
    """Affiche l'écran principal de choix du mode de jeu et du plateau."""
    for widget in root.winfo_children():
        widget.destroy()
    header_bg = "#e0e0e0"
    header = tk.Frame(root, bg=header_bg, height=80)
    header.pack(side="top", fill="x")
    from core.langues import traduire
    username = dic_variables.get('username') or getattr(root, 'USERNAME', None)
    bienvenue = tk.Label(header, text=f"{traduire('bienvenue')} {username if username else ''}", font=("Arial", 22, "bold"), bg=header_bg, fg="#5b7fce")
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
        menu.add_command(label=traduire("a_propos"), command=lambda: messagebox.showinfo(traduire("a_propos"), traduire("a_propos_texte")))
        menu.add_command(label=traduire("credits"), command=lambda: messagebox.showinfo(traduire("credits"), traduire("credits_texte")))
        menu.add_separator()
        # Se déconnecter : retour à la page login
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
        menu.add_command(label=traduire("se_deconnecter"), command=go_to_login)
        menu.add_command(label=traduire("fermer"), command=root.quit)
        menu.tk_popup(event.x_root, event.y_root)
    btn_icon.bind("<Button-1>", show_logout_menu)

    """Barre de son"""
    from core.musique import SoundBar, regler_volume
    from core.parametres import LanguageSelector
    volume_transmis = getattr(root, 'VOLUME', None)
    initial_volume = 50
    if dic_variables.get('volume') is not None:
        initial_volume = dic_variables['volume']
    elif volume_transmis is not None:
        initial_volume = volume_transmis
    elif hasattr(root, 'volume_var'):
        try:
            initial_volume = root.volume_var.get()
        except Exception:
            pass
    if hasattr(root, 'volume_var'):
        root.volume_var.set(initial_volume)
        soundbar = SoundBar(root, volume_var=root.volume_var)
    else:
        root.volume_var = tk.IntVar(value=initial_volume)
        soundbar = SoundBar(root, volume_var=root.volume_var)
    regler_volume(root.volume_var.get())
    soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

    """Langues"""
    def on_language_changed(new_lang):
        try:
            current_volume = soundbar.volume_var.get()
        except Exception:
            current_volume = dic_variables.get('volume')
        current_mode = dic_variables.get("mode", "1v1")
        current_network_mode = dic_variables.get("network_mode", "local")
        current_plateau_mode = dic_variables.get("plateau_mode", "auto")
        current_username = username
        import importlib
        import core.langues
        importlib.reload(core.langues)
        main(root, dic_variables["jeu_demande"], username=current_username, volume=current_volume, mode=current_mode, network_mode=current_network_mode, plateau_mode=current_plateau_mode)
    lang_selector = LanguageSelector(root, assets_dir="assets", callback=on_language_changed)
    lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

    main_frame = tk.Frame(root, bg="#f0f0f0")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(main_frame, text=traduire(dic_variables["jeu_demande"]).upper(), font=("Helvetica", 16, "bold"), fg="#004d40", bg="#f0f0f0").pack(pady=10)

    dic_variables["mode_var"] = tk.StringVar(value=dic_variables["mode"])
    dic_variables["plateau_mode_var"] = tk.StringVar(value=dic_variables["plateau_mode"])

    frame_mode = tk.Frame(main_frame, bg="#f0f0f0")
    frame_mode.pack(pady=10)

    frame1 = tk.Frame(frame_mode, bg="#f0f0f0")
    frame1.pack(pady=10)
    tk.Radiobutton(frame1, text=traduire("mode_1v1"), variable=dic_variables["mode_var"], value="1v1", font=("Helvetica", 12), bg="#f0f0f0", command=lambda: on_mode_change(root)).pack(side="left", padx=10)
    btn_mode_select = tk.Button(frame1, text=traduire("mode_jeu"), font=("Helvetica", 12, "bold"), bg="#e0f7fa", bd=0, command=lambda: open_mode_choice_window(root))
    btn_mode_select.pack(side="left", padx=5)

    frame2 = tk.Frame(frame_mode, bg="#f0f0f0")
    frame2.pack(pady=10)
    tk.Radiobutton(frame2, text=traduire("mode_ia"), variable=dic_variables["mode_var"], value="ia", font=("Helvetica", 12), bg="#f0f0f0", command=lambda: on_mode_change(root)).pack(side="left", padx=10)

    frame_plateau = tk.Frame(main_frame, bg="#f0f0f0")
    frame_plateau.pack(pady=10)

    tk.Label(frame_plateau, text=traduire("plateau"), bg="#f0f0f0", font=("Helvetica", 13)).pack()
    tk.Radiobutton(frame_plateau, text=traduire("plateau_auto"), variable=dic_variables["plateau_mode_var"], value="auto", bg="#f0f0f0", font=("Helvetica", 12), command=lambda: on_plateau_mode_change(root)).pack(anchor="w", padx=20)
    tk.Radiobutton(frame_plateau, text=traduire("plateau_perso"), variable=dic_variables["plateau_mode_var"], value="perso", bg="#f0f0f0", font=("Helvetica", 12), command=lambda: on_plateau_mode_change(root)).pack(anchor="w", padx=20)

    dic_variables["play_btn"] = tk.Button(main_frame, text=traduire("play"), command=lambda: play(root), font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=15, relief="flat", state="disabled")
    dic_variables["play_btn"].pack(pady=20)

    if dic_variables.get("mode_label"):
        dic_variables["mode_label"].destroy()
    dic_variables["mode_label"] = tk.Label(main_frame, font=("Helvetica", 11, "italic"), bg="#f0f0f0", fg="#004d40")
    dic_variables["mode_label"].pack(pady=(0, 10))
    update_go_button_state(root)

    """Bouton retour"""
    def retour_menu():
        import menu_gui
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
        menu_gui.show_menu(root, volume=current_volume)
    img_retour = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
    icon_retour = ImageTk.PhotoImage(img_retour)
    btn_retour = tk.Button(root, image=icon_retour, command=retour_menu, bg="#f0f0f0", bd=0, relief="flat", cursor="hand2", activebackground="#e0e0e0")
    btn_retour.image = icon_retour
    btn_retour.place(relx=0.0, rely=0.5, anchor="w", x=18)

def on_mode_change(root):
    """Met à jour le mode de jeu choisi dans le dictionnaire"""
    dic_variables["mode"] = dic_variables["mode_var"].get()
    update_go_button_state(root)

def on_plateau_mode_change(root):
    """Met à jour le mode de plateau choisi dans le dictionnaire"""
    dic_variables["plateau_mode"] = dic_variables["plateau_mode_var"].get()

def get_local_ip():
    """Renvoie l'adresse IP locale de la machine (pour le réseau)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def main(root, jeu_type, username=None, volume=None, mode=None, network_mode=None, plateau_mode=None):
    global dic_variables
    dic_variables = {
        "jeu_demande": jeu_type,
        "network_mode": network_mode if network_mode is not None else "local",
        "client_socket": None,
        "mode": mode if mode is not None else "1v1",
        "game_ready": False,
        "plateau_mode": plateau_mode if plateau_mode is not None else "auto",
        "username": username,
        "volume": volume
    }
    
    if username:
        setattr(root, 'USERNAME', username)
    afficher_interface_choix(root)