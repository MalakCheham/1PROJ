import tkinter as tk
import threading
import sys
import subprocess

from plateau_builder import lancer_plateau_builder
from quadrant_editor_live import QuadrantEditorLive
from core.network.network_selector import network_selector
from core.network.server import start_server
from core.network.client import start_client, send_move, receive_move
from core.langues import traduire
from tkinter import messagebox
from PIL import Image, ImageTk

network_mode = None
client_socket = None

jeu_demande = sys.argv[1] if len(sys.argv) > 1 else "katarenga"

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

def on_network_choice(result):
    global network_mode, client_socket
    network_mode = result
    if result == "host":
        threading.Thread(target=start_server, daemon=True).start()
        messagebox.showinfo(traduire("host"), traduire("server_started_waiting"))
    elif result == "join":
        ip = tk.simpledialog.askstring(traduire("join"), traduire("enter_server_ip"), initialvalue="127.0.0.1")
        client_socket = start_client(ip)
        if client_socket:
            messagebox.showinfo(traduire("join"), traduire("connected_to_server"))
        else:
            messagebox.showerror(traduire("join"), traduire("connection_failed"))

def choose_mode():
    network_selector(root, on_network_choice)

def go():
    if plateau_mode.get() == "auto":
        root.destroy()
        lancer_plateau_builder(jeu_demande, mode.get() == "ia", plateau_mode.get())
    elif plateau_mode.get() == "perso":
        for widget in root.winfo_children():
            widget.destroy()
        QuadrantEditorLive(root, retour_callback=retour_vers_configuration)

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
    tk.Radiobutton(frame1, text=traduire("mode_1v1"), variable=mode, value="1v1", font=("Helvetica", 12), bg="#fefbe9", command=choose_mode).pack(side="left", padx=10)

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
root.mainloop()
