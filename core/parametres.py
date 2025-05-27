import os
import tkinter as tk
from PIL import Image, ImageTk

chemin_langue = os.path.join("assets", "langue.txt")
if os.path.exists(chemin_langue):
    with open(chemin_langue, "r", encoding="utf-8") as f:
        LANGUE_ACTUELLE = f.read().strip()
else:
    LANGUE_ACTUELLE = "fr"

def set_langue(langue):
    global LANGUE_ACTUELLE
    if langue in ["fr", "en"]:
        LANGUE_ACTUELLE = langue

class LanguageSelector(tk.Frame):
    def __init__(self, master, assets_dir, callback=None, **kwargs):
        super().__init__(master, bg="#f0f0f0", **kwargs)
        self.assets_dir = assets_dir
        self.callback = callback
        self.lang_var = tk.StringVar(value=LANGUE_ACTUELLE)
        fr_img = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "france.png")).resize((32, 32)))
        en_img = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "uk.png")).resize((32, 32)))
        self.images = {'fr': fr_img, 'en': en_img}
        for code in ("fr", "en"):
            btn = tk.Radiobutton(
                self, image=self.images[code], variable=self.lang_var, value=code,
                indicatoron=0, borderwidth=0, width=40, height=40,
                selectcolor='#e0e0e0', bg='#f0f0f0', activebackground='#e0e0e0',
                relief='flat', highlightthickness=0, cursor='hand2',
                command=self.change_language)
            btn.image = self.images[code]
            btn.pack(side='top', pady=(0, 8) if code=='fr' else (0, 0))

    def change_language(self):
        new = self.lang_var.get()
        if new not in ('fr', 'en'):
            return
        # Sauvegarde du choix
        chemin_langue = os.path.join(self.assets_dir, "langue.txt")
        try:
            with open(chemin_langue, 'w', encoding='utf-8') as f:
                f.write(new)
        except Exception:
            pass
        # Met à jour la variable globale
        global LANGUE_ACTUELLE
        LANGUE_ACTUELLE = new
        # Callback pour rafraîchir l'UI
        if self.callback:
            self.callback(new)
