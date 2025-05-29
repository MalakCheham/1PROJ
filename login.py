import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import importlib

import core.parametres as parameters
import core.langues as languages
from core.musique import set_volume, SoundBar
from core.parametres import LanguageSelector

"""Login screen"""

ASSETS_DIR = parameters.get_assets_dir()
class LoginScreen(tk.Frame):
    def __init__(self, master=None, initial_volume=None):
        from core.langues import translate

        root_window = master or tk.Tk()
        super().__init__(root_window, bg="#f0f0f0")
        self.master = root_window
        self.master.geometry("900x800")
        self.master.configure(bg="#f0f0f0")
        self.load_icon()
        self.pack(expand=True, fill="both")
        self.initial_volume = initial_volume 
        self.build_ui()
        
        if not getattr(self.master, 'initialized', False):
            self.master.initialized = True
            self.master.mainloop()

    def load_icon(self):
        icon_path = os.path.join(ASSETS_DIR, "logo.png")
        icon_image = ImageTk.PhotoImage(file=icon_path)
        self.master.iconphoto(False, icon_image)

    def build_ui(self):
        import core.parametres
        from core.langues import translate
        import core.traductions

        importlib.reload(core.parametres)
        importlib.reload(core.langues)
        importlib.reload(core.traductions)

        for widget in self.winfo_children():
            widget.destroy()

        center_frame = tk.Frame(self, bg="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        logo_frame = tk.Frame(center_frame, bg="#f0f0f0")
        logo_frame.pack(pady=(30, 10))
        
        logo_image = Image.open(os.path.join(ASSETS_DIR, "logo.png")).resize((180, 180))
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = tk.Label(logo_frame, image=logo_photo, bg="#f0f0f0")
        logo_label.image = logo_photo
        logo_label.pack()

        tk.Label(center_frame, text=translate("welcome_to_portal"), 
                 font=("Arial", 18, "bold"), bg="#f0f0f0", 
                 fg="#004d99").pack(pady=10)
        tk.Label(center_frame, text=translate("enter_username"), 
                 font=("Arial", 13), bg="#f0f0f0").pack(pady=10)

        self.username_var = tk.StringVar()
        username_entry = tk.Entry(center_frame, textvariable=self.username_var,
                         font=("Arial", 13), width=18, bg="#fff",
                         bd=2, relief="groove", justify="center",
                         highlightthickness=2, highlightbackground="#b3d9ff",
                         highlightcolor="#4CAF50")
        username_entry.pack(ipady=6, ipadx=2)
        username_entry.focus_set()
        username_entry.bind("<Return>", lambda event: self.enter_portal())

        enter_button = tk.Button(center_frame, text=translate("enter_portal"),
                           font=("Arial", 13, "bold"), bg="#219150", fg="white",
                           activebackground="#19713c", activeforeground="white",
                           width=20, height=2, bd=0, relief="flat",
                           highlightthickness=1, highlightbackground="#19713c",
                           cursor="hand2", command=self.enter_portal)
        enter_button.pack(pady=30, ipadx=2, ipady=2)
        enter_button.bind("<Enter>", lambda event: enter_button.configure(bg="#19713c"))
        enter_button.bind("<Leave>", lambda event: enter_button.configure(bg="#219150"))

        self.build_sound_controls()
        self.build_language_selector()

        self.master.title(translate("title"))

    def get_current_volume(self):
        try:
            return self.master.volume_var.get()
        except AttributeError:
            try:
                from core.musique import SoundBar
                return SoundBar.last_volume
            except Exception:
                return None

    def enter_portal(self):
        import menu_gui
        from tkinter import messagebox
        from core.langues import translate
        username = self.username_var.get().strip()
        if not username:
            messagebox.showerror(translate("error"), translate("username_required"))
            return
        current_volume = self.get_current_volume()
        for widget in self.master.winfo_children():
            widget.destroy()
        menu_gui.show_menu(self.master, username=username, volume=current_volume)

    def build_sound_controls(self):
        from core.musique import SoundBar, set_volume
        if hasattr(self.master, 'volume_var'):
            self.master.volume_var.set(self.initial_volume if self.initial_volume is not None else self.master.volume_var.get())
            self.volume_var = self.master.volume_var
            soundbar_frame = SoundBar(self, volume_var=self.volume_var)
        else:
            initial = self.initial_volume if self.initial_volume is not None else 50
            self.volume_var = tk.IntVar(value=initial)
            self.master.volume_var = self.volume_var
            soundbar_frame = SoundBar(self, volume_var=self.volume_var)
        set_volume(self.volume_var.get())
        soundbar_frame.pack(side="left", anchor="sw", padx=10, pady=10)

    def build_language_selector(self):
        language_selector = LanguageSelector(self, assets_dir=ASSETS_DIR, callback=self.on_language_changed)
        language_selector.pack(side="right", anchor="se", padx=18, pady=18)

    def on_language_changed(self, new_language):
        from core.parametres import set_language
        set_language(new_language)
        show_login(self.master, volume=self.volume_var.get() if hasattr(self, 'volume_var') else None)


def show_login(root_window=None, volume=None):
    if root_window:
        for widget in root_window.winfo_children():
            widget.destroy()
        screen = LoginScreen(master=root_window, initial_volume=volume)
    else:
        screen = LoginScreen(initial_volume=volume)
