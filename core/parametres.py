import os
import tkinter as tk
from PIL import Image, ImageTk
import sys

"""Language management"""

def get_assets_dir():
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets")

def get_language_file_path(assets_dir):
    user_dir = os.path.expanduser('~')
    app_dir = os.path.join(user_dir, '.project_b1')
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, 'language.txt')

language_file = get_language_file_path("assets")
if os.path.exists(language_file):
    with open(language_file, "r", encoding="utf-8") as file:
        CURRENT_LANGUAGE = file.read().strip()
else:
    CURRENT_LANGUAGE = "fr"

def set_language(language):
    global CURRENT_LANGUAGE
    if language in ["fr", "en"]:
        CURRENT_LANGUAGE = language
class LanguageSelector(tk.Frame):
    def __init__(self, master, assets_dir, callback=None, **kwargs):
        super().__init__(master, bg="#f0f0f0", **kwargs)
        self.assets_dir = assets_dir
        self.callback = callback
        self.language_var = tk.StringVar(value=CURRENT_LANGUAGE)
        fr_img = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "france.png")).resize((32, 32)), master=master)
        en_img = ImageTk.PhotoImage(Image.open(os.path.join(assets_dir, "uk.png")).resize((32, 32)), master=master)
        self.images = {'fr': fr_img, 'en': en_img}
        for code in ("fr", "en"):
            btn = tk.Radiobutton(
                self, image=self.images[code], variable=self.language_var, value=code,
                indicatoron=0, borderwidth=0, width=40, height=40,
                selectcolor='#e0e0e0', bg='#f0f0f0', activebackground='#e0e0e0',
                relief='flat', highlightthickness=0, cursor='hand2',
                command=self.change_language)
            btn.image = self.images[code]
            btn.pack(side='top', pady=(0, 8) if code=='fr' else (0, 0))

    def change_language(self):
        new_lang = self.language_var.get()
        if new_lang not in ('fr', 'en'):
            return
        language_file = get_language_file_path(self.assets_dir)
        try:
            with open(language_file, 'w', encoding='utf-8') as file:
                file.write(new_lang)
        except Exception:
            pass
        try:
            with open(language_file, 'r', encoding='utf-8') as file:
                new_lang = file.read().strip()
        except Exception:
            pass
        global CURRENT_LANGUAGE
        CURRENT_LANGUAGE = new_lang
        if self.callback:
            self.callback(new_lang)
