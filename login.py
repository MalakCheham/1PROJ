import customtkinter as ctk
from PIL import Image, ImageTk
import os

from customtkinter import CTkImage

import core.parametres as parameters
import core.langues as languages
from core.musique import set_volume, SoundBar
from core.parametres import LanguageSelector

"""Login screen"""

ASSETS_DIR = parameters.get_assets_dir()
class LoginScreen(ctk.CTkFrame):
    def __init__(self, master=None, initial_volume=None):
        from core.langues import translate

        root_window = master or ctk.CTk()
        super().__init__(root_window, fg_color="#f0f0f0")
        self.master = root_window
        self.master.geometry("900x800")
        self.master.configure(fg_color="#f0f0f0")
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

        for widget in self.winfo_children():
            widget.destroy()

        center_frame = ctk.CTkFrame(self, fg_color="#f0f0f0")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        logo_frame = ctk.CTkFrame(center_frame, fg_color="#f0f0f0")
        logo_frame.pack(pady=(30, 10))
        
        logo_image = Image.open(os.path.join(ASSETS_DIR, "logo.png")).resize((180, 180))
        logo_ctk_image = CTkImage(light_image=logo_image, dark_image=logo_image, size=(180, 180))
        logo_label = ctk.CTkLabel(logo_frame, image=logo_ctk_image, text="", fg_color="#f0f0f0")
        logo_label.image = logo_ctk_image
        logo_label.pack()

        ctk.CTkLabel(center_frame, text=translate("welcome_to_portal"), 
                 font=("Arial", 18, "bold"), text_color="#004d99", fg_color="#f0f0f0").pack(pady=10)
        ctk.CTkLabel(center_frame, text=translate("enter_username"), 
                 font=("Arial", 13), text_color="#222222").pack(pady=10)

        self.username_var = ctk.StringVar()
        username_entry = ctk.CTkEntry(center_frame, textvariable=self.username_var,
                         font=("Arial", 13), width=180, fg_color="#d1d1d1", text_color="#3B3B3B",
                         border_width=2, corner_radius=8, justify="center")
        username_entry.pack(ipady=6, ipadx=2)
        username_entry.focus_set()
        username_entry.bind("<Return>", lambda event: self.enter_portal())

        enter_button = ctk.CTkButton(center_frame, text=translate("enter_portal"),
                           font=("Arial", 13, "bold"), fg_color="#219150", text_color="white",
                           hover_color="#19713c", width=180, height=40, corner_radius=8,
                           command=self.enter_portal)
        enter_button.pack(pady=30, ipadx=2, ipady=2)

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
            self.volume_var = ctk.IntVar(value=initial)
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
