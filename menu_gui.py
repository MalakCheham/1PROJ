import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import sys
import os

from core.langues import traduire
from core import parametres
from core.musique import jouer_musique, regler_volume, pause, reprendre

# === Lancer musique une seule fois ===
jouer_musique()

def open_settings():
    fen = tk.Toplevel()
    fen.title(traduire("parametres"))
    fen.geometry("360x420")
    fen.configure(bg="#f0f4f8")

    try:
        icon_img = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
        fen.iconphoto(False, icon_img)
        fen.icon_img = icon_img
    except Exception as e:
        print("Erreur chargement icône : ", e)

    frame_effets = tk.Frame(fen, bg="#f0f4f8")
    frame_effets.pack(pady=10, padx=15, fill="x")
    tk.Label(frame_effets, text="🔊", bg="#f0f4f8").pack(side="left")
    tk.Label(frame_effets, text=traduire("volume_effets"), bg="#f0f4f8", font=("Helvetica", 11)).pack(side="left", padx=10)
    tk.Scale(frame_effets, from_=0, to=100, orient="horizontal", bg="#f0f4f8", length=120).pack(side="right")

    frame_musique = tk.Frame(fen, bg="#f0f4f8")
    frame_musique.pack(pady=10, padx=15, fill="x")
    tk.Label(frame_musique, text="🎵", bg="#f0f4f8").pack(side="left")
    tk.Label(frame_musique, text=traduire("volume_musique"), bg="#f0f4f8", font=("Helvetica", 11)).pack(side="left", padx=10)
    scale = tk.Scale(frame_musique, from_=0, to=100, orient="horizontal", bg="#f0f4f8", length=120, command=regler_volume)
    scale.set(50)
    scale.pack(side="right")

    frame_ctrl = tk.Frame(fen, bg="#f0f4f8")
    frame_ctrl.pack(pady=10)
    tk.Button(frame_ctrl, text="⏸ Pause", command=pause).pack(side="left", padx=10)
    tk.Button(frame_ctrl, text="▶ Reprendre", command=reprendre).pack(side="left", padx=10)

    frame_langue = tk.Frame(fen, bg="#f0f4f8")
    frame_langue.pack(pady=15, padx=15, fill="x")
    tk.Label(frame_langue, text="🌐", bg="#f0f4f8").pack(side="left")
    tk.Label(frame_langue, text=traduire("langue"), bg="#f0f4f8", font=("Helvetica", 11)).pack(side="left", padx=10)
    tk.Button(frame_langue, text="FR", width=5, command=lambda: change_language("fr", fen)).pack(side="right", padx=5)
    tk.Button(frame_langue, text="EN", width=5, command=lambda: change_language("en", fen)).pack(side="right", padx=5)

    frame_retour = tk.Frame(fen, bg="#f0f4f8")
    frame_retour.pack(pady=15)
    try:
        retour_img = Image.open(os.path.join("assets", "en-arriere.png")).resize((32, 32))
        retour_icon = ImageTk.PhotoImage(retour_img)
        tk.Button(frame_retour, image=retour_icon, command=fen.destroy, bg="#f0f4f8", bd=0).pack()
        frame_retour.image = retour_icon
    except:
        tk.Button(frame_retour, text="Retour", command=fen.destroy).pack()

def build_interface(root=None):
    if root is None:
        from tkinter import _default_root
        root = _default_root
    for widget in root.winfo_children():
        widget.destroy()
    frame_top = tk.Frame(root, bg="#e6f2ff")
    frame_top.pack(side="top", fill="x", pady=10, padx=10)
    tk.Label(frame_top, text=traduire("titre"), font=("Helvetica", 16, "bold"), fg="#004d99", bg="#e6f2ff").pack(side="left")
    try:
        icone_image = Image.open(os.path.join("assets", "lyrique.png")).resize((24, 24))
        icone = ImageTk.PhotoImage(icone_image)
        def show_lyrique_menu(event=None):
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="À propos", command=lambda: messagebox.showinfo("À propos", "Katarenga & Co.\nProjet B1"))
            menu.add_command(label="Crédits", command=lambda: messagebox.showinfo("Crédits", "Développé par:\n Ibtihel BOUGUERN\n Malak CHEHAM\n Yassmine"))
            menu.add_separator()
            menu.add_command(label="Se déconnecter", command=lambda: (import_login_and_show(root)))
            menu.add_command(label="Fermer", command=root.quit)
            menu.tk_popup(event.x_root, event.y_root) if event else menu.post(0, 0)
        def import_login_and_show(root):
            import login
            login.show_login(root)
        bouton_options = tk.Button(frame_top, image=icone, bg="#e6f2ff", bd=0)
        bouton_options.image = icone
        bouton_options.pack(side="right")
        bouton_options.bind("<Button-1>", show_lyrique_menu)
    except:
        tk.Button(frame_top, text="⚙", command=open_settings).pack(side="right")
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
    tk.Button(frame, text=traduire("jouer_katarenga"), command=lambda: launch_game("katarenga", root), **style_btn).pack(pady=10)
    tk.Button(frame, text=traduire("jouer_congress"), command=lambda: launch_game("congress", root), **style_btn).pack(pady=10)
    tk.Button(frame, text=traduire("jouer_isolation"), command=lambda: launch_game("isolation", root), **style_btn).pack(pady=10)

def launch_game(jeu_type, root):
    try:
        for widget in root.winfo_children():
            widget.destroy()
        import menu_gui2
        menu_gui2.main(root, jeu_type)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lancer le jeu : {e}")

def change_language(code, root=None):
    chemin_langue = os.path.join("assets", "langue.txt")
    with open(chemin_langue, "w", encoding="utf-8") as f:
        f.write(code)
    parametres.LANGUE_ACTUELLE = code
    build_interface(root)

def main(root):
    root.title("KATARENGA&CO.")
    root.geometry("600x800")
    root.configure(bg="#e6f2ff")
    try:
        icon_img = ImageTk.PhotoImage(file=os.path.join("assets", "logo.png"))
        root.iconphoto(False, icon_img)
    except:
        pass
    build_interface(root)

# Appel direct uniquement si exécuté comme script principal
if __name__ == "__main__":
    main(tk.Tk())
