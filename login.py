import tkinter as tk
from PIL import Image, ImageTk
import os
import importlib

import core.parametres as parametres
import core.langues as langues
from core.musique import regler_volume
from core.parametres import LanguageSelector

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

class LoginScreen(tk.Frame):
    def __init__(self, master=None, volume=None):
        from core.langues import traduire

        root = master or tk.Tk()
        super().__init__(root, bg="#f0f0f0")
        self.master = root
        self.master.geometry("900x800")
        self.master.configure(bg="#f0f0f0")
        self.load_icon()
        self.pack(expand=True, fill="both")
        self._init_volume = volume  # Store initial volume
        self.build_ui()
        
        if not getattr(self.master, 'initialized', False):
            self.master.initialized = True
            self.master.mainloop()

    def load_icon(self):
        icon_path = os.path.join(ASSETS_DIR, "logo.png")
        icon = ImageTk.PhotoImage(file=icon_path)
        self.master.iconphoto(False, icon)
        

    def build_ui(self):
        import core.parametres
        from core.langues import traduire
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
        
        image = Image.open(os.path.join(ASSETS_DIR, "logo.png")).resize((180, 180))
        logo_img = ImageTk.PhotoImage(image)
        label = tk.Label(logo_frame, image=logo_img, bg="#f0f0f0")
        label.image = logo_img
        label.pack()

        tk.Label(center_frame, text=traduire("bienvenue_portail"), font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#004d99").pack(pady=10)
        tk.Label(center_frame, text=traduire("entrez_nom_utilisateur"), font=("Arial", 13), bg="#f0f0f0").pack(pady=10)

        self.username_var = tk.StringVar()
        entry = tk.Entry(center_frame, textvariable=self.username_var,
                         font=("Arial", 13), width=18, bg="#fff",
                         bd=2, relief="groove", justify="center",
                         highlightthickness=2, highlightbackground="#b3d9ff",
                         highlightcolor="#4CAF50")
        entry.pack(ipady=6, ipadx=2)
        entry.focus_set()

        button = tk.Button(center_frame, text=traduire("entrez_portail"),
                        font=("Arial", 13, "bold"), bg="#219150", fg="white",
                        activebackground="#19713c", activeforeground="white",
                        width=20, height=2, bd=0, relief="flat",  # 'flat' pour compatibilité Mac
                        highlightthickness=1, highlightbackground="#19713c",
                        cursor="hand2", command=self.enter_portal)
        button.pack(pady=30, ipadx=2, ipady=2)
        button.bind("<Enter>", lambda e: button.configure(bg="#19713c"))
        button.bind("<Leave>", lambda e: button.configure(bg="#219150"))

        self.build_sound_controls()
        self.build_language_selector()

        self.master.title(traduire("titre"))

    def enter_portal(self):
        import menu_gui
        try:
            current_volume = self.volume_var.get()
        except AttributeError:
            try:
                from core.musique import SoundBar
                current_volume = SoundBar.last_volume
            except Exception:
                current_volume = None
        for widget in self.master.winfo_children():
            widget.destroy()
        username = self.username_var.get().strip()
        menu_gui.show_menu(self.master, username=username, volume=current_volume)

    """Barre de son"""
    def build_sound_controls(self):
        from core.musique import SoundBar, regler_volume
        if hasattr(self.master, 'volume_var'):
            self.master.volume_var.set(self._init_volume if self._init_volume is not None else self.master.volume_var.get())
            self.volume_var = self.master.volume_var
            frame = SoundBar(self, volume_var=self.volume_var)
        else:
            initial = self._init_volume if self._init_volume is not None else 50
            self.volume_var = tk.IntVar(value=initial)
            self.master.volume_var = self.volume_var
            frame = SoundBar(self, volume_var=self.volume_var)
        regler_volume(self.volume_var.get())
        frame.pack(side="left", anchor="sw", padx=10, pady=10)

    def build_language_selector(self):
        selector = LanguageSelector(self, assets_dir=ASSETS_DIR, callback=self.on_language_changed)
        selector.pack(side="right", anchor="se", padx=18, pady=18)

    def on_language_changed(self, new_lang):
        self.build_ui()

def show_login(root=None, volume=None):
    if root:
        for widget in root.winfo_children():
            widget.destroy()
        screen = LoginScreen(master=root, volume=volume)
    else:
        screen = LoginScreen(volume=volume)
