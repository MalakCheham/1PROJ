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

"""Variables globales"""
dic_variables = {
    "jeu_demande": sys.argv[1] if len(sys.argv) > 1 else "katarenga",
    "network_mode": "local", 
    "client_socket": None,
    "mode": "1v1",
    "game_ready": False,
    "plateau_mode": "auto"
}

def center_window(win, width, height):
    """Centre une fenêtre par rapport à la fenêtre principale (root)"""
    win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def show_help():
    """Affiche la fenêtre d'aide avec les explications du jeu"""
    messagebox.showinfo(traduire("aide"), traduire("aide_texte"))

def quit_app():
    """Ferme la fenêtre principale et relance le menu"""
    root.destroy()
    subprocess.Popen([sys.executable, "menu_gui.py"])

def back_to_config():
    """Retourne à l'écran de choix principal."""
    for widget in root.winfo_children():
        widget.destroy()
    afficher_interface_choix()

def open_host_window():
    name = simpledialog.askstring(traduire("heberger"), traduire("entrer_nom_serveur"), parent=root)
    if not name:
        return
    player_name = simpledialog.askstring(traduire("heberger"), traduire("entrer_nom_joueur"), parent=root)
    if not player_name:
        return
    # On revient sur la fenêtre principale, l'utilisateur choisit le plateau
    for widget in root.winfo_children():
        widget.destroy()
    def attente_client_et_lancer_jeu(plateau, pions):
        # Affiche la fenêtre d'attente d'un joueur
        attente_win = tk.Toplevel(root)
        attente_win.title(traduire("heberger"))
        center_window(attente_win, 350, 180)
        attente_win.transient(root)
        attente_win.grab_set()
        attente_win.configure(bg="#e0f7fa")
        label = tk.Label(attente_win, text=traduire("attente_joueur"), font=("Helvetica", 13, "bold"), bg="#e0f7fa")
        label.pack(pady=30)
        # Quand un client se connecte, on lance le jeu dans le thread principal
        def on_client_connect(attente_win, client_socket, addr):
            attente_win.destroy()
            root.after(0, lambda: start_network_game(is_host=True, player_name=player_name, sock=client_socket, plateau=plateau, pions=pions))
        def on_stop(attente_win):
            attente_win.destroy()
            messagebox.showinfo(traduire("heberger"), traduire("serveur_arrete"))
            dic_variables["game_ready"] = False
            update_go_button_state()
        # Lancer le serveur d'attente
        from core.network.game_network import host_server
        host_server(
            server_name=name,
            on_client_connect=on_client_connect,
            on_stop=on_stop,
            root=root,
            tk=tk,
            traduire=traduire,
            center_window=center_window
        )
    # Choix du mode de plateau
    if dic_variables["plateau_mode"] == "auto":
        def on_lancer_partie(plateau, pions):
            attente_client_et_lancer_jeu(plateau, pions)
        lancer_plateau_builder(dic_variables["jeu_demande"], False, "auto", on_lancer_partie)
    else:
        QuadrantEditorLive(root, retour_callback=back_to_config, network_callback=attente_client_et_lancer_jeu)

def open_network_window():
    """Ouvre la fenêtre pour choisir entre héberger ou rejoindre une partie réseau"""
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("choisir_mode_jeu"))
    center_window(fenetre, 300, 180)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(bg="#e0f7fa")
    tk.Label(fenetre, text=traduire("choisir_reseau"), font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=15)
    btn_host = tk.Button(fenetre, text=traduire("heberger"), font=("Helvetica", 12), width=15, command=lambda: [fenetre.destroy(), open_host_window()])
    btn_host.pack(pady=5)
    btn_join = tk.Button(fenetre, text=traduire("join_server"), font=("Helvetica", 12), width=15, command=lambda: [fenetre.destroy(), open_join_window()])
    btn_join.pack(pady=5)

def open_join_window():
    """Ouvre la fenêtre pour rejoindre une partie réseau existante"""
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("join_server"))
    center_window(fenetre, 350, 350)
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
        btn = tk.Button(frame_list, text=f"{srv['nom']} ({srv['ip']}:{srv['port']})", font=("Helvetica", 12), width=30, anchor="w", command=lambda s=srv: join_server_ui(s, fenetre))
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

def start_network_game(is_host, player_name=None, player_name_noir=None, sock=None, plateau=None, pions=None):
    """Lance la partie réseau avec les bons paramètres"""
    for widget in root.winfo_children():
        widget.destroy()
    if is_host:
        player_name_blanc = player_name
        player_name_noir = None
    else:
        player_name_blanc = None
        player_name_noir = player_name_noir or player_name
    # Correction : toujours transmettre plateau et pions (ou positions) reçus du serveur au client
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

def join_server_ui(server, fenetre):
    fenetre.destroy()
    player_name = simpledialog.askstring(traduire("join_server"), traduire("entrer_nom_joueur"), parent=root)
    if not player_name:
        return
    ip = server['ip']
    port = server.get('port', 5555)
    sock = join_server(ip, port)
    if sock:
        dic_variables["game_ready"] = True
        update_go_button_state()
        # Affiche une fenêtre d'attente côté client
        for widget in root.winfo_children():
            widget.destroy()
        wait_win = tk.Toplevel(root)
        wait_win.title(traduire("join_server"))
        center_window(wait_win, 350, 120)
        wait_win.transient(root)
        wait_win.grab_set()
        wait_win.configure(bg="#e0f7fa")
        tk.Label(wait_win, text="En attente que l'hôte lance la partie...", font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=30)
        # Thread d'attente de la config du plateau
        import threading
        def attendre_lancement():
            # Quand la config arrive, on lance le jeu dans le thread principal
            root.after(0, lambda: start_network_game(is_host=False, player_name=player_name, sock=sock))
            wait_win.destroy()
        threading.Thread(target=attendre_lancement, daemon=True).start()
    else:
        messagebox.showerror(traduire("join_server"), f"{traduire('tentative_connexion')} {server['nom']} ({ip})\n{traduire('connection_failed')}")
        dic_variables["game_ready"] = False
        update_go_button_state()

def update_go_button_state():
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

def play():
    """Lance la partie selon les choix de l'utilisateur"""
    if dic_variables["network_mode"] == "reseau" and dic_variables.get("is_host"):
        # Si l'utilisateur est l'hôte, on affiche d'abord l'aperçu ou l'éditeur, puis la fenêtre d'attente APRÈS le clic sur "Lancer la partie"
        def lancer_partie_reseau(plateau=None, pions=None):
            from core.network.game_network import host_server
            def on_client_connect(attente_win, client_socket, addr):
                attente_win.destroy()
                start_network_game(is_host=True, player_name=dic_variables.get("host_name"), sock=client_socket, plateau=plateau, pions=pions)
            def on_stop(attente_win):
                attente_win.destroy()
                messagebox.showinfo(traduire("heberger"), traduire("serveur_arrete"))
                dic_variables["game_ready"] = False
                update_go_button_state()
            attente_win = tk.Toplevel(root)
            attente_win.title(traduire("heberger"))
            center_window(attente_win, 300, 120)
            attente_win.transient(root)
            attente_win.grab_set()
            attente_win.configure(bg="#e0f7fa")
            label = tk.Label(attente_win, text=f"Serveur créé : {dic_variables.get('host_name','')}\n{get_local_ip()}:5555", font=("Helvetica", 13, "bold"), bg="#e0f7fa")
            label.pack(pady=20)
            tk.Button(attente_win, text="OK", command=attente_win.destroy, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white").pack(pady=10)
            host_server(
                server_name=dic_variables.get("host_name","Serveur"),
                on_client_connect=on_client_connect,
                on_stop=on_stop,
                root=root,
                tk=tk,
                traduire=traduire,
                center_window=center_window
            )
        if dic_variables["plateau_mode"] == "auto":
            # Afficher l'aperçu du plateau, puis lancer la partie réseau APRÈS clic sur "Lancer la Partie"
            def on_lancer_partie(plateau, pions):
                # Après validation de l'aperçu, afficher la fenêtre d'attente
                lancer_partie_reseau(plateau, pions)
            lancer_plateau_builder(dic_variables["jeu_demande"], False, "auto", on_lancer_partie)
        else:
            # Quadrants personnalisés : l'éditeur appelle le callback réseau après clic sur "Jouer avec ces quadrants"
            QuadrantEditorLive(root, retour_callback=back_to_config, network_callback=lancer_partie_reseau)
    elif dic_variables["network_mode"] == "reseau" and dic_variables.get("is_client"):
        # Côté client, on lance la partie réseau immédiatement
        start_network_game(is_host=False, player_name=dic_variables.get("player_name"), sock=dic_variables.get("client_socket"))
    else:
        # Solo ou IA : comportement inchangé
        if dic_variables["plateau_mode"] == "auto":
            root.destroy()
            lancer_plateau_builder(dic_variables["jeu_demande"], dic_variables["mode"] == "ia", dic_variables["plateau_mode"])
        elif dic_variables["plateau_mode"] == "perso":
            for widget in root.winfo_children():
                widget.destroy()
            QuadrantEditorLive(root, retour_callback=back_to_config)

def open_mode_choice_window():
    """Ouvre la fenêtre pour choisir entre solo et réseau"""
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("choisir_mode_jeu"))
    center_window(fenetre, 300, 180)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(bg="#e0f7fa")
    def set_local():
        dic_variables["network_mode"] = "local"
        dic_variables["is_host"] = False
        dic_variables["is_client"] = False
        dic_variables["game_ready"] = True
        update_go_button_state()
        fenetre.destroy()
    def set_reseau():
        dic_variables["network_mode"] = "reseau"
        dic_variables["is_host"] = False
        dic_variables["is_client"] = False
        dic_variables["game_ready"] = False
        update_go_button_state()
        fenetre.destroy()
        open_network_window()
    tk.Label(fenetre, text=traduire("choisir_mode_jeu"), font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=15)
    btn_solo = tk.Button(fenetre, text=traduire("mode_solo"), font=("Helvetica", 12), width=15, command=set_local)
    btn_solo.pack(pady=5)
    btn_reseau = tk.Button(fenetre, text=traduire("mode_reseau"), font=("Helvetica", 12), width=15, command=set_reseau)
    btn_reseau.pack(pady=5)

def afficher_interface_choix():
    """Affiche l'écran principal de choix du mode de jeu et du plateau."""
    frame_top = tk.Frame(root, bg="#e0f7fa")
    frame_top.pack(side="top", fill="x", pady=5, padx=5)

    # Bouton retour
    try:
        retour_img = Image.open(os.path.join("assets", "en-arriere.png")).resize((24, 24))
        retour_icon = ImageTk.PhotoImage(retour_img)
        btn_retour = tk.Button(frame_top, image=retour_icon, command=quit_app, bg="#e0f7fa", bd=0)
        btn_retour.image = retour_icon
        btn_retour.pack(side="left")
    except:
        tk.Button(frame_top, text="<", command=quit_app, bg="#e0f7fa", bd=0).pack(side="left")

    # Bouton aide
    try:
        help_img = Image.open(os.path.join("assets", "point-dinterrogation.png")).resize((24, 24))
        help_icon = ImageTk.PhotoImage(help_img)
        btn_help = tk.Button(frame_top, image=help_icon, command=show_help, bg="#e0f7fa", bd=0)
        btn_help.image = help_icon
        btn_help.pack(side="right")
    except:
        tk.Button(frame_top, text="?", command=show_help, bg="#e0f7fa", bd=0).pack(side="right")

    # Titre du jeu
    tk.Label(root, text=traduire(dic_variables["jeu_demande"]).upper(), font=("Helvetica", 16, "bold"), fg="#004d40", bg="#fefbe9").pack(pady=10)

    # Variables Tkinter pour l'UI, stockées dans le dictionnaire
    dic_variables["mode_var"] = tk.StringVar(value=dic_variables["mode"])
    dic_variables["plateau_mode_var"] = tk.StringVar(value=dic_variables["plateau_mode"])

    # Choix du mode de jeu
    frame_mode = tk.Frame(root, bg="#fefbe9")
    frame_mode.pack(pady=10)

    frame1 = tk.Frame(frame_mode, bg="#fefbe9")
    frame1.pack(pady=10)
    tk.Radiobutton(frame1, text=traduire("mode_1v1"), variable=dic_variables["mode_var"], value="1v1", font=("Helvetica", 12), bg="#fefbe9", command=on_mode_change).pack(side="left", padx=10)
    btn_mode_select = tk.Button(frame1, text=traduire("mode_jeu"), font=("Helvetica", 12, "bold"), bg="#e0f7fa", bd=0, command=open_mode_choice_window)
    btn_mode_select.pack(side="left", padx=5)

    frame2 = tk.Frame(frame_mode, bg="#fefbe9")
    frame2.pack(pady=10)
    tk.Radiobutton(frame2, text=traduire("mode_ia"), variable=dic_variables["mode_var"], value="ia", font=("Helvetica", 12), bg="#fefbe9", command=on_mode_change).pack(side="left", padx=10)

    # Choix du plateau
    frame_plateau = tk.Frame(root, bg="#fefbe9")
    frame_plateau.pack(pady=10)

    tk.Label(frame_plateau, text=traduire("plateau"), bg="#fefbe9", font=("Helvetica", 13)).pack()
    tk.Radiobutton(frame_plateau, text=traduire("plateau_auto"), variable=dic_variables["plateau_mode_var"], value="auto", bg="#fefbe9", font=("Helvetica", 12), command=on_plateau_mode_change).pack(anchor="w", padx=20)
    tk.Radiobutton(frame_plateau, text=traduire("plateau_perso"), variable=dic_variables["plateau_mode_var"], value="perso", bg="#fefbe9", font=("Helvetica", 12), command=on_plateau_mode_change).pack(anchor="w", padx=20)

    # Bouton pour jouer, stocké dans le dictionnaire
    dic_variables["play_btn"] = tk.Button(root, text=traduire("play"), command=play, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=15, relief="flat", state="disabled")
    dic_variables["play_btn"].pack(pady=20)
    update_go_button_state()

def on_mode_change():
    """Met à jour le mode de jeu choisi dans le dictionnaire"""
    dic_variables["mode"] = dic_variables["mode_var"].get()
    update_go_button_state()

def on_plateau_mode_change():
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

# Tkinter : crée la fenetre principale
root = tk.Tk()
root.title(traduire("titre"))
root.geometry("360x580")
root.configure(bg="#e6f2ff")

# Tkinter : charger l'icone
icon_img = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
root.iconphoto(False, icon_img)

# On gènere la fenêtre principale
afficher_interface_choix()

# Lancer la musique 
pygame.mixer.init()
pygame.mixer.music.load(os.path.join("assets", "musique.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

root.mainloop()