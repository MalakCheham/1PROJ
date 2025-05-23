import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import os
import pygame

from core.langues import traduire
from core import parametres

# === Fenêtre Paramètres ===
def open_settings():
    fen = tk.Toplevel()
    fen.title(traduire("parametres"))
    fen.geometry("360x420")

    try:    
        icon_img = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
        fen.iconphoto(False, icon_img)
        fen.icon_img = icon_img
    except Exception as e:
        print("Erreur chargement icône : ", e)

    frame_effets = tk.Frame(fen, bg="#f0f4f8")
    frame_effets.pack(pady=10, padx=15, fill="x")
    try:
        icone_effet = Image.open(os.path.join("assets", "volume-reduit.png")).resize((24, 24))
        icone_effet_img = ImageTk.PhotoImage(icone_effet)
        tk.Label(frame_effets, image=icone_effet_img, bg="#f0f4f8").pack(side="left", padx=5)
        frame_effets.image = icone_effet_img
    except:
        tk.Label(frame_effets, text="🔊", bg="#f0f4f8").pack(side="left")

    tk.Label(frame_effets, text=traduire("volume_effets"), bg="#f0f4f8", font=("Helvetica", 11)).pack(side="left", padx=10)
    tk.Scale(frame_effets, from_=0, to=100, orient="horizontal", bg="#f0f4f8", length=120).pack(side="right")

    frame_musique = tk.Frame(fen, bg="#f0f4f8")
    frame_musique.pack(pady=10, padx=15, fill="x")
    try:
        icone_musique = Image.open(os.path.join("assets", "note-de-musique.png")).resize((24, 24))
        icone_musique_img = ImageTk.PhotoImage(icone_musique)
        tk.Label(frame_musique, image=icone_musique_img, bg="#f0f4f8").pack(side="left", padx=5)
        frame_musique.image = icone_musique_img
    except:
        tk.Label(frame_musique, text="🎵", bg="#f0f4f8").pack(side="left")

    tk.Label(frame_musique, text=traduire("volume_musique"), bg="#f0f4f8", font=("Helvetica", 11)).pack(side="left", padx=10)
    tk.Scale(frame_musique, from_=0, to=100, orient="horizontal", bg="#f0f4f8", length=120).pack(side="right")

    frame_langue = tk.Frame(fen, bg="#f0f4f8")
    frame_langue.pack(pady=15, padx=15, fill="x")
    try:
        lang_img = Image.open(os.path.join("assets", "utilisateur.png")).resize((24, 24))
        lang_icon = ImageTk.PhotoImage(lang_img)
        tk.Label(frame_langue, image=lang_icon, bg="#f0f4f8").pack(side="left", padx=5)
        frame_langue.image = lang_icon
    except:
        tk.Label(frame_langue, text="🌐", bg="#f0f4f8").pack(side="left")

    tk.Label(frame_langue, text=traduire("langue"), bg="#f0f4f8", font=("Helvetica", 11)).pack(side="left", padx=10)
    tk.Button(frame_langue, text=traduire("langue_fr"), width=5, command=lambda: change_language("fr")).pack(side="right", padx=5)
    tk.Button(frame_langue, text=traduire("langue_en"), width=5, command=lambda: change_language("en")).pack(side="right", padx=5)

    frame_retour = tk.Frame(fen, bg="#f0f4f8")
    frame_retour.pack(pady=15)
    try:
        retour_img = Image.open(os.path.join("assets", "en-arriere.png")).resize((32, 32))
        retour_icon = ImageTk.PhotoImage(retour_img)
        tk.Button(frame_retour, image=retour_icon, command=fen.destroy, bg="#f0f4f8", bd=0).pack()
        frame_retour.image = retour_icon
    except:
        tk.Button(frame_retour, text=traduire("retour"), command=fen.destroy).pack()

# === Changer langue ===
def change_language(code):
    chemin_langue = os.path.join("assets", "langue.txt")

    with open(chemin_langue, "w", encoding="utf-8") as f:
        f.write(code)
    with open(chemin_langue, "r", encoding="utf-8") as f:
        parametres.LANGUE_ACTUELLE = f.read().strip()

    for widget in root.winfo_children():
        widget.destroy()

    build_interface()

# === Lancer jeu ===
def launch_game(jeu_type):
    try:
        subprocess.Popen([sys.executable, "menu_gui2.py", jeu_type])
        root.destroy()
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lancer le jeu : {e}")

# === Construction de l'interface principale ===
def build_interface():
    # === En-tête ===
    frame_top = tk.Frame(root, bg="#e6f2ff")
    frame_top.pack(side="top", fill="x", pady=10, padx=10)
    tk.Label(frame_top, text=traduire("titre"), font=("Helvetica", 16, "bold"), fg="#004d99", bg="#e6f2ff").pack(side="left")

    try:
        icone_image = Image.open(os.path.join("assets", "lyrique.png")).resize((24, 24))
        icone = ImageTk.PhotoImage(icone_image)
        bouton_options = tk.Button(frame_top, image=icone, bg="#e6f2ff", bd=0, command=open_settings)
        bouton_options.image = icone
        bouton_options.pack(side="right")
    except:
        tk.Button(frame_top, text="⚙", command=open_settings).pack(side="right")

    # === Boutons de jeux ===
    frame = tk.Frame(root, bg="#e6f2ff")
    frame.pack(expand=True)

    style_btn = {
        "font": ("Helvetica", 12, "bold"),
        "bg": "#cce6ff",
        "fg": "#003366",
        "activebackground": "#b3d9ff",
        "activeforeground": "#003366",
        "width": 20,
        "height": 2,
        "bd": 2,
        "relief": "ridge",
        "highlightthickness": 0,
        "cursor": "hand2"
    }

    tk.Button(frame, text=traduire("jouer_katarenga"), command=lambda: launch_game("katarenga"), **style_btn).pack(pady=10)
    tk.Button(frame, text=traduire("jouer_congress"), command=lambda: launch_game("congress"), **style_btn).pack(pady=10)
    tk.Button(frame, text=traduire("jouer_isolation"), command=lambda: launch_game("isolation"), **style_btn).pack(pady=10)

    # === MUSIQUE DE FOND ===
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join("assets", "musique.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# === Fenêtre principale ===
root = tk.Tk()
root.title("KATARENGA&CO.")
root.geometry("340x460")
root.configure(bg="#e6f2ff")

# === Icône dans la barre de titre ===
try:
    icon_img = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
    root.iconphoto(False, icon_img)
except Exception as e:
    print(f"Erreur chargement icône : {e}")

# === Construction initiale de l'interface ===
build_interface()

root.mainloop()
