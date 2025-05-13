import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import subprocess

from plateau_builder import lancer_plateau_builder

# === Jeu demandé depuis le menu principal ===
jeu_demande = sys.argv[1] if len(sys.argv) > 1 else "katarenga"

# === Actions ===
def afficher_aide():
    messagebox.showinfo("Aide", "Choisissez un mode :\n- 1 VS 1 : deux joueurs humains\n- IA : vous contre un adversaire aléatoire")

def fermer():
    root.destroy()
    subprocess.Popen([sys.executable, "menu_gui.py"])

def go():
    root.destroy()
    lancer_plateau_builder(jeu_demande, mode.get() == "ia")

# === Fenêtre principale ===
root = tk.Tk()
root.title("KATARENGA&CO.")
root.geometry("340x460")
root.configure(bg="#e6f2ff")

# === Icône dans la barre de titre ===
try:
    icon_img = ImageTk.PhotoImage(file="assets/logo.png")
    root.iconphoto(False, icon_img)
except Exception as e:
    print(f"Erreur chargement icône : {e}")


# === En-tête avec retour et aide ===
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

# === Titre du jeu ===
tk.Label(root, text=jeu_demande.upper(), font=("Helvetica", 16, "bold"), fg="#004d40", bg="#fefbe9").pack(pady=10)

# === Choix du mode de jeu ===
frame_mode = tk.Frame(root, bg="#fefbe9")
frame_mode.pack(pady=10)

mode = tk.StringVar(value="1v1")

# 1v1
frame1 = tk.Frame(frame_mode, bg="#fefbe9")
frame1.pack(pady=10)
tk.Radiobutton(frame1, text="1 VS 1", variable=mode, value="1v1", font=("Helvetica", 12),
               bg="#fefbe9", fg="#004d40", selectcolor="#fefbe9", activebackground="#fefbe9").pack(side="left", padx=10)
try:
    user_img = Image.open("assets/utilisateur.png").resize((24, 24))
    user_icon = ImageTk.PhotoImage(user_img)
    tk.Label(frame1, image=user_icon, bg="#fefbe9").pack(side="left")
except:
    pass

# IA
frame2 = tk.Frame(frame_mode, bg="#fefbe9")
frame2.pack(pady=10)
tk.Radiobutton(frame2, text="IA", variable=mode, value="ia", font=("Helvetica", 12),
               bg="#fefbe9", fg="#004d40", selectcolor="#fefbe9", activebackground="#fefbe9").pack(side="left", padx=10)
try:
    ia_img = Image.open("assets/ia.png").resize((24, 24))
    ia_icon = ImageTk.PhotoImage(ia_img)
    tk.Label(frame2, image=ia_icon, bg="#fefbe9").pack(side="left")
except:
    pass

# === Bouton GO ===
tk.Button(root, text="GO !", command=go, font=("Helvetica", 12, "bold"),
          bg="#4CAF50", fg="white", width=15, relief="flat").pack(pady=20)

root.mainloop()
