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

network_mode = None
client_socket = None

jeu_demande = sys.argv[1] if len(sys.argv) > 1 else "katarenga"

def center_window(win, width, height):
    win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def show_help():
    messagebox.showinfo(traduire("aide"), 
        traduire("aide_texte")) 

def quit_app():
    root.destroy()
    subprocess.Popen([sys.executable, "menu_gui.py"])

def back_to_config():
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
    def on_client_connect(attente_win, client_socket, addr):
        attente_win.destroy()
        messagebox.showinfo(traduire("heberger"), traduire("client_connecte"))
        game_ready.set(True)
        update_go_button_state()
        # Lancer la partie réseau en tant qu'hôte, passer la socket réseau et le nom du joueur hôte
        start_network_game(is_host=True, player_name=player_name, sock=client_socket)
    def on_stop(attente_win):
        attente_win.destroy()
        messagebox.showinfo(traduire("heberger"), traduire("serveur_arrete"))
        game_ready.set(False)
        update_go_button_state()
    host_server(
        server_name=name,
        on_client_connect=on_client_connect,
        on_stop=on_stop,
        root=root,
        tk=tk,
        traduire=traduire,
        center_window=center_window
    )

def open_network_window():
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

def join_server_ui(server, fenetre):
    fenetre.destroy()
    # Demander le nom du joueur avant de rejoindre
    player_name = simpledialog.askstring(traduire("join_server"), traduire("entrer_nom_joueur"), parent=root)
    if not player_name:
        return  # Annulé
    ip = server['ip']
    port = server.get('port', 5555)
    sock = join_server(ip, port)
    if sock:
        game_ready.set(True)
        update_go_button_state()
        # Lancer la partie réseau en tant que client
        # On ne connaît pas le nom du joueur blanc (hôte) ici, il faudra l'échanger au début de la partie
        start_network_game(is_host=False, player_name_noir=player_name, sock=sock)
    else:
        messagebox.showerror(traduire("join_server"), f"{traduire('tentative_connexion')} {server['nom']} ({ip})\n{traduire('connection_failed')}")
        game_ready.set(False)
        update_go_button_state()

# Fonction pour lancer le jeu réseau (plateau, joueurs, etc.)
def start_network_game(is_host, player_name=None, player_name_noir=None, sock=None):
    for widget in root.winfo_children():
        widget.destroy()
    if is_host:
        player_name_blanc = player_name
        player_name_noir = None 
    else:
        player_name_blanc = None 
        player_name_noir = player_name_noir or player_name
    if jeu_demande == "katarenga":
        from jeux.katarenga import lancer_jeu_reseau
        lancer_jeu_reseau(root, is_host=is_host, player_name_blanc=player_name_blanc, player_name_noir=player_name_noir, sock=sock)
    elif jeu_demande == "isolation":
        from jeux.isolation import lancer_jeu_reseau
        lancer_jeu_reseau(root, is_host=is_host, player_name_blanc=player_name_blanc, player_name_noir=player_name_noir, sock=sock)
    elif jeu_demande == "congress":
        from jeux.congress import lancer_jeu_reseau
        lancer_jeu_reseau(root, is_host=is_host, player_name_blanc=player_name_blanc, player_name_noir=player_name_noir, sock=sock)
    else:
        tk.Label(root, text="Mode réseau non implémenté pour ce jeu.", font=("Helvetica", 15, "bold"), fg="#d32f2f", bg="#e6f2ff").pack(pady=60)

def open_mode_choice_window():
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("choisir_mode_jeu"))
    center_window(fenetre, 300, 180)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(bg="#e0f7fa")
    def set_local():
        network_mode.set("local")
        game_ready.set(True)
        update_go_button_state()
        fenetre.destroy()
    def set_reseau():
        network_mode.set("reseau")
        game_ready.set(False)
        update_go_button_state()
        fenetre.destroy()
        open_network_window()
    tk.Label(fenetre, text=traduire("choisir_mode_jeu"), font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=15)
    btn_solo = tk.Button(fenetre, text=traduire("mode_solo"), font=("Helvetica", 12), width=15, command=set_local)
    btn_solo.pack(pady=5)
    btn_reseau = tk.Button(fenetre, text=traduire("mode_reseau"), font=("Helvetica", 12), width=15, command=set_reseau)
    btn_reseau.pack(pady=5)

def afficher_interface_choix():
    frame_top = tk.Frame(root, bg="#e0f7fa")
    frame_top.pack(side="top", fill="x", pady=5, padx=5)

    try:
        retour_img = Image.open(os.path.join("assets", "en-arriere.png")).resize((24, 24))
        retour_icon = ImageTk.PhotoImage(retour_img)
        btn_retour = tk.Button(frame_top, image=retour_icon, command=fermer, bg="#e0f7fa", bd=0)
        btn_retour.image = retour_icon
        btn_retour.pack(side="left")
    except:
        tk.Button(frame_top, text="<", command=fermer, bg="#e0f7fa", bd=0).pack(side="left")

    try:
        help_img = Image.open(os.path.join("assets", "point-dinterrogation.png")).resize((24, 24))
        help_icon = ImageTk.PhotoImage(help_img)
        btn_help = tk.Button(frame_top, image=help_icon, command=show_help, bg="#e0f7fa", bd=0)
        btn_help.image = help_icon
        btn_help.pack(side="right")
    except:
        tk.Button(frame_top, text="?", command=show_help, bg="#e0f7fa", bd=0).pack(side="right")

    # === Titre ===
    tk.Label(root, text=traduire(jeu_demande).upper(), font=("Helvetica", 16, "bold"), fg="#004d40", bg="#fefbe9").pack(pady=10)

    # === Mode de jeu ===
    global mode, network_mode, game_ready
    mode = tk.StringVar(value="1v1")
    network_mode = tk.StringVar(value="local")  # 'local' or 'reseau'
    game_ready = tk.BooleanVar(value=False)
    frame_mode = tk.Frame(root, bg="#fefbe9")
    frame_mode.pack(pady=10)

    frame1 = tk.Frame(frame_mode, bg="#fefbe9")
    frame1.pack(pady=10)
    tk.Radiobutton(frame1, text=traduire("mode_1v1"), variable=mode, value="1v1", font=("Helvetica", 12), bg="#fefbe9", command=update_go_button_state).pack(side="left", padx=10)
    btn_mode_select = tk.Button(frame1, text=traduire("mode_jeu"), font=("Helvetica", 12, "bold"), bg="#e0f7fa", bd=0, command=open_mode_choice_window)
    btn_mode_select.pack(side="left", padx=5)

    frame2 = tk.Frame(frame_mode, bg="#fefbe9")
    frame2.pack(pady=10)
    tk.Radiobutton(frame2, text=traduire("mode_ia"), variable=mode, value="ia", font=("Helvetica", 12), bg="#fefbe9", command=update_go_button_state).pack(side="left", padx=10)

    # === Choix du plateau ===
    global plateau_mode
    plateau_mode = tk.StringVar(value="auto")
    frame_plateau = tk.Frame(root, bg="#fefbe9")
    frame_plateau.pack(pady=10)

    tk.Label(frame_plateau, text=traduire("plateau"), bg="#fefbe9", font=("Helvetica", 13)).pack()
    tk.Radiobutton(frame_plateau, text=traduire("plateau_auto"), variable=plateau_mode, value="auto", bg="#fefbe9", font=("Helvetica", 12)).pack(anchor="w", padx=20)
    tk.Radiobutton(frame_plateau, text=traduire("plateau_perso"), variable=plateau_mode, value="perso", bg="#fefbe9", font=("Helvetica", 12)).pack(anchor="w", padx=20)

    """Bouton Jouer"""
    global play_btn
    play_btn = tk.Button(root, text=traduire("play"), command=play, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=15, relief="flat", state="disabled")
    play_btn.pack(pady=20)
    update_go_button_state()

"""Si les conditions du mode de jeu sont remplies, le bouton GO est activé."""
def update_go_button_state():
    if mode.get() == "ia":
        play_btn.config(state="normal", bg="#4CAF50")
    elif mode.get() == "1v1":
        if network_mode.get() == "local":
            play_btn.config(state="normal", bg="#4CAF50")
        elif network_mode.get() == "reseau" and game_ready.get():
            play_btn.config(state="normal", bg="#4CAF50")
        else:
            play_btn.config(state="disabled", bg="#888888")
    else:
        play_btn.config(state="disabled", bg="#888888")

def play():
    if plateau_mode.get() == "auto":
        root.destroy()
        lancer_plateau_builder(jeu_demande, mode.get() == "ia", plateau_mode.get())
    elif plateau_mode.get() == "perso":
        for widget in root.winfo_children():
            widget.destroy()
        QuadrantEditorLive(root, retour_callback=retour_vers_configuration)

def retour_vers_configuration():
    for widget in root.winfo_children():
        widget.destroy()
    afficher_interface_choix()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def fermer():
    root.destroy()
    subprocess.Popen([sys.executable, "menu_gui.py"])

"""Initialisation de la fenêtre principale"""
root = tk.Tk()
root.title(traduire("titre"))
root.geometry("360x580")
root.configure(bg="#e6f2ff")

"""Charger l'icône de la fenêtre"""
try:
    icon_img = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
    root.iconphoto(False, icon_img)
except Exception as e:
    print("Erreur chargement icône :", e)

afficher_interface_choix()

"""Initialisation de la musique de fond"""
pygame.mixer.init()
pygame.mixer.music.load(os.path.join("assets", "musique.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

root.mainloop()

