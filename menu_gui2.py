import tkinter as tk
import threading
import sys
import subprocess
import pygame
import socket


from plateau_builder import lancer_plateau_builder
from quadrant_editor_live import QuadrantEditorLive
from core.network.server import wait_for_first_client
from core.network.client import start_client, send_move, receive_move
from core.langues import traduire
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from core.network.discovery import ServerBroadcaster, ServerDiscovery

network_mode = None
client_socket = None
broadcaster = None
discovery = None

jeu_demande = sys.argv[1] if len(sys.argv) > 1 else "katarenga"

def center_window(win, width, height):
    win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def afficher_aide():
    messagebox.showinfo(traduire("aide"), 
        traduire("aide_texte")) 

def fermer():
    root.destroy()
    subprocess.Popen([sys.executable, "menu_gui.py"])

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

def creer_serveur(nom_serveur):
    ip = get_local_ip()
    port = 5000
    global broadcaster
    broadcaster = ServerBroadcaster(nom_serveur, port)
    broadcaster.start()
    attente_win = tk.Toplevel(root)
    attente_win.title(traduire("heberger"))
    center_window(attente_win, 300, 120)
    attente_win.transient(root)
    attente_win.grab_set()
    attente_win.configure(bg="#e0f7fa")
    label = tk.Label(attente_win, text=traduire("attente_joueur"), font=("Helvetica", 13, "bold"), bg="#e0f7fa")
    label.pack(pady=30)
    def server_thread():
        wait_for_first_client()
        if broadcaster:
            broadcaster.stop()
        root.after(0, lambda: [attente_win.destroy(), messagebox.showinfo(traduire("heberger"), traduire("client_connecte"))])
    threading.Thread(target=server_thread, daemon=True).start()
    messagebox.showinfo(traduire("heberger"), f"{traduire('serveur_cree')}\n{traduire('ip')}: {ip}\n{traduire('nom_serveur')}: {nom_serveur}")

def ouvrir_fenetre_host():
    nom = simpledialog.askstring(traduire("heberger"), traduire("entrer_nom_serveur"), initialvalue="Para Serveur", parent=root)
    if nom:
        creer_serveur(nom)


def ouvrir_fenetre_reseau():
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("reseau"))
    center_window(fenetre, 300, 180)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(bg="#e0f7fa")

    tk.Label(fenetre, text=traduire("choisir_reseau"), font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=15)
    btn_host = tk.Button(fenetre, text=traduire("heberger"), font=("Helvetica", 12), width=15, command=lambda: [fenetre.destroy(), ouvrir_fenetre_host()])
    btn_host.pack(pady=5)
    btn_join = tk.Button(fenetre, text=traduire("rejoindre"), font=("Helvetica", 12), width=15, command=lambda: [fenetre.destroy(), ouvrir_fenetre_join()])
    btn_join.pack(pady=5)


def ouvrir_fenetre_join():
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("rejoindre"))
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
        btn = tk.Button(frame_list, text=f"{srv['nom']} ({srv['ip']}:{srv['port']})", font=("Helvetica", 12), width=30, anchor="w", command=lambda s=srv: rejoindre_serveur(s, fenetre))
        btn.pack(pady=3)
        btns.append(btn)

    discovery = ServerDiscovery(add_server)
    discovery.start()

    def on_close():
        discovery.stop()
        fenetre.destroy()
    fenetre.protocol("WM_DELETE_WINDOW", on_close)

    # Ajout d'un bouton pour rafraîchir la liste (optionnel)
    def refresh():
        for b in btns:
            b.destroy()
        btns.clear()
        serveurs.clear()
        discovery.found.clear()
    tk.Button(fenetre, text=traduire("rafraichir"), command=refresh, bg="#b2ebf2").pack(pady=5)


def rejoindre_serveur(serveur, fenetre):
    # Connexion réseau réelle ici
    fenetre.destroy()
    ip = serveur['ip']
    port = serveur.get('port', 5000)
    sock = start_client(ip, port)
    if sock:
        messagebox.showinfo(traduire("rejoindre"), f"{traduire('tentative_connexion')} {serveur['nom']} ({ip})\n{traduire('connexion_reussie')}")
        # TODO: Passer à l'écran de jeu réseau si connexion OK
    else:
        messagebox.showerror(traduire("rejoindre"), f"{traduire('tentative_connexion')} {serveur['nom']} ({ip})\n{traduire('connection_failed')}")

def ouvrir_fenetre_choix_mode():
    fenetre = tk.Toplevel(root)
    fenetre.title(traduire("choix_mode"))
    center_window(fenetre, 300, 180)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(bg="#e0f7fa")
    tk.Label(fenetre, text=traduire("choisir_mode_jeu"), font=("Helvetica", 13, "bold"), bg="#e0f7fa").pack(pady=15)
    btn_solo = tk.Button(fenetre, text=traduire("mode_solo"), font=("Helvetica", 12), width=15, command=fenetre.destroy)
    btn_solo.pack(pady=5)
    btn_reseau = tk.Button(fenetre, text=traduire("mode_reseau"), font=("Helvetica", 12), width=15, command=lambda: [fenetre.destroy(), ouvrir_fenetre_reseau()])
    btn_reseau.pack(pady=5)

def afficher_interface_choix():
    # === En-tête ===
    frame_top = tk.Frame(root, bg="#e0f7fa")
    frame_top.pack(side="top", fill="x", pady=5, padx=5)

    try:
        retour_img = Image.open("assets/en-arriere.png").resize((24, 24))
        retour_icon = ImageTk.PhotoImage(retour_img)
        btn_retour = tk.Button(frame_top, image=retour_icon, command=fermer, bg="#e0f7fa", bd=0)
        btn_retour.image = retour_icon
        btn_retour.pack(side="left")
    except:
        tk.Button(frame_top, text="<", command=fermer, bg="#e0f7fa", bd=0).pack(side="left")

    try:
        help_img = Image.open("assets/point-dinterrogation.png").resize((24, 24))
        help_icon = ImageTk.PhotoImage(help_img)
        btn_help = tk.Button(frame_top, image=help_icon, command=afficher_aide, bg="#e0f7fa", bd=0)
        btn_help.image = help_icon
        btn_help.pack(side="right")
    except:
        tk.Button(frame_top, text="?", command=afficher_aide, bg="#e0f7fa", bd=0).pack(side="right")

    # === Titre ===
    tk.Label(root, text=traduire(jeu_demande).upper(), font=("Helvetica", 16, "bold"), fg="#004d40", bg="#fefbe9").pack(pady=10)

    # === Mode de jeu ===
    global mode
    mode = tk.StringVar(value="1v1")
    frame_mode = tk.Frame(root, bg="#fefbe9")
    frame_mode.pack(pady=10)

    frame1 = tk.Frame(frame_mode, bg="#fefbe9")
    frame1.pack(pady=10)
    tk.Radiobutton(frame1, text=traduire("mode_1v1"), variable=mode, value="1v1", font=("Helvetica", 12), bg="#fefbe9", command=None).pack(side="left", padx=10)
    # === Nouveau bouton pour ouvrir la sélection de mode (solo/réseau) ===
    btn_mode_select = tk.Button(frame1, text="⋮", font=("Helvetica", 12, "bold"), bg="#e0f7fa", bd=0, command=ouvrir_fenetre_choix_mode)
    btn_mode_select.pack(side="left", padx=5)

    frame2 = tk.Frame(frame_mode, bg="#fefbe9")
    frame2.pack(pady=10)
    tk.Radiobutton(frame2, text=traduire("mode_ia"), variable=mode, value="ia", font=("Helvetica", 12), bg="#fefbe9").pack(side="left", padx=10)

    # === Choix du plateau ===
    global plateau_mode
    plateau_mode = tk.StringVar(value="auto")
    frame_plateau = tk.Frame(root, bg="#fefbe9")
    frame_plateau.pack(pady=10)

    tk.Label(frame_plateau, text=traduire("plateau"), bg="#fefbe9", font=("Helvetica", 13)).pack()
    tk.Radiobutton(frame_plateau, text=traduire("plateau_auto"), variable=plateau_mode, value="auto", bg="#fefbe9", font=("Helvetica", 12)).pack(anchor="w", padx=20)
    tk.Radiobutton(frame_plateau, text=traduire("plateau_perso"), variable=plateau_mode, value="perso", bg="#fefbe9", font=("Helvetica", 12)).pack(anchor="w", padx=20)

    # === Bouton GO ===
    tk.Button(root, text=traduire("go"), command=go, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white", width=15, relief="flat").pack(pady=20)

def go():
    if plateau_mode.get() == "auto":
        root.destroy()
        lancer_plateau_builder(jeu_demande, mode.get() == "ia", plateau_mode.get())
    elif plateau_mode.get() == "perso":
        for widget in root.winfo_children():
            widget.destroy()
        QuadrantEditorLive(root, retour_callback=retour_vers_configuration)

# === Fenêtre principale ===
root = tk.Tk()
root.title(traduire("titre"))
root.geometry("360x580")
root.configure(bg="#e6f2ff")

# === Icône ===
try:
    icon_img = ImageTk.PhotoImage(file="assets/logo.png")
    root.iconphoto(False, icon_img)
except Exception as e:
    print("Erreur chargement icône :", e)

afficher_interface_choix()
# === MUSIQUE DE FOND ===
pygame.mixer.init()
pygame.mixer.music.load("assets/musique.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

root.mainloop()

