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
jouer_musique()


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
    """Centre une fenêtre par rapport à la fenêtre principale (root)"""
    win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def show_help():
    """Affiche la fenêtre d'aide avec les explications du jeu"""
    messagebox.showinfo(traduire("aide"), traduire("aide_texte"))

def quit_app(root):
    """Ferme la fenêtre principale et relance le menu"""
    root.destroy()
    subprocess.Popen([sys.executable, "menu_gui.py"])

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
    # Affichage du mode courant
    mode_label = dic_variables.get("mode_label")
    if not mode_label:
        mode_label = tk.Label(root, font=("Helvetica", 11, "italic"), bg="#e6f2ff", fg="#004d40")
        mode_label.pack()
        dic_variables["mode_label"] = mode_label
    if dic_variables["network_mode"] == "local":
        mode_label.config(text="Mode : Solo")
    elif dic_variables["network_mode"] == "reseau":
        if dic_variables.get("is_host"):
            mode_label.config(text="Mode : Réseau (hôte)")
        elif dic_variables.get("is_client"):
            mode_label.config(text="Mode : Réseau (client)")
        else:
            mode_label.config(text="Mode : Réseau")
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
    # Nettoyer la fenêtre
    for widget in root.winfo_children():
        widget.destroy()

    # --- Entête importée depuis menu_gui.py ---
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

    # --- Ajout barre de son et sélecteur de langue en bas ---
    from core.musique import SoundBar, regler_volume
    from core.parametres import LanguageSelector
    # Barre de son en bas à gauche
    soundbar = SoundBar(root)
    volume = getattr(root, 'VOLUME', None)
    if volume is not None:
        soundbar.volume_var.set(volume)
        regler_volume(volume)
    else:
        regler_volume(soundbar.volume_var.get())
    soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

    # Sélecteur de langue en bas à droite
    def on_language_changed(new_lang):
        # Préserver le volume actuel
        try:
            current_volume = soundbar.volume_var.get()
        except Exception:
            current_volume = volume
        import importlib
        import core.langues
        importlib.reload(core.langues)
        main(root, dic_variables["jeu_demande"], username=username, volume=current_volume)
    lang_selector = LanguageSelector(root, assets_dir="assets", callback=on_language_changed)
    lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

    # Titre du jeu
    tk.Label(root, text=traduire(dic_variables["jeu_demande"]).upper(), font=("Helvetica", 16, "bold"), fg="#004d40", bg="#f0f0f0").pack(pady=10)

    # Variables Tkinter pour l'UI, stockées dans le dictionnaire
    dic_variables["mode_var"] = tk.StringVar(value=dic_variables["mode"])
    dic_variables["plateau_mode_var"] = tk.StringVar(value=dic_variables["plateau_mode"])

    # Choix du mode de jeu
    frame_mode = tk.Frame(root, bg="#f0f0f0")
    frame_mode.pack(pady=10)

    frame1 = tk.Frame(frame_mode, bg="#f0f0f0")
    frame1.pack(pady=10)
    tk.Radiobutton(frame1, text=traduire("mode_1v1"), variable=dic_variables["mode_var"], value="1v1", font=("Helvetica", 12), bg="#f0f0f0", command=lambda: on_mode_change(root)).pack(side="left", padx=10)
    btn_mode_select = tk.Button(frame1, text=traduire("mode_jeu"), font=("Helvetica", 12, "bold"), bg="#e0f7fa", bd=0, command=lambda: open_mode_choice_window(root))
    btn_mode_select.pack(side="left", padx=5)

    frame2 = tk.Frame(frame_mode, bg="#f0f0f0")
    frame2.pack(pady=10)
    tk.Radiobutton(frame2, text=traduire("mode_ia"), variable=dic_variables["mode_var"], value="ia", font=("Helvetica", 12), bg="#f0f0f0", command=lambda: on_mode_change(root)).pack(side="left", padx=10)

    # Choix du plateau
    frame_plateau = tk.Frame(root, bg="#f0f0f0")
    frame_plateau.pack(pady=10)

    tk.Label(frame_plateau, text=traduire("plateau"), bg="#f0f0f0", font=("Helvetica", 13)).pack()
    tk.Radiobutton(frame_plateau, text=traduire("plateau_auto"), variable=dic_variables["plateau_mode_var"], value="auto", bg="#f0f0f0", font=("Helvetica", 12), command=lambda: on_plateau_mode_change(root)).pack(anchor="w", padx=20)
    tk.Radiobutton(frame_plateau, text=traduire("plateau_perso"), variable=dic_variables["plateau_mode_var"], value="perso", bg="#f0f0f0", font=("Helvetica", 12), command=lambda: on_plateau_mode_change(root)).pack(anchor="w", padx=20)

    # Bouton pour jouer, stocké dans le dictionnaire
    dic_variables["play_btn"] = tk.Button(root, text=traduire("play"), command=lambda: play(root), font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=15, relief="flat", state="disabled")
    dic_variables["play_btn"].pack(pady=20)
    update_go_button_state(root)

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

def fermer():
    """Ferme la fenêtre principale et relance le menu"""
    root.destroy()
    subprocess.Popen([sys.executable, "menu_gui.py"])

def main(root, jeu_type, username=None, volume=None):
    global dic_variables
    dic_variables = {
        "jeu_demande": jeu_type,
        "network_mode": "local",
        "client_socket": None,
        "mode": "1v1",
        "game_ready": False,
        "plateau_mode": "auto",
        "username": username,
        "volume": volume
    }
    # Stocker l'utilisateur sur root pour l'entête
    if username:
        setattr(root, 'USERNAME', username)
    afficher_interface_choix(root)