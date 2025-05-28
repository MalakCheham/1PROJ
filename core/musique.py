import os
import pygame
import tkinter as tk

MUSIQUE_LANCEE = False

def jouer_musique():
    global MUSIQUE_LANCEE
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    if not MUSIQUE_LANCEE:
        chemin_musique = os.path.join("assets", "musique.mp3")
        pygame.mixer.music.load(chemin_musique)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        MUSIQUE_LANCEE = True

def regler_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)

def pause():
    pygame.mixer.music.pause()

def reprendre():
    pygame.mixer.music.unpause()

class SoundBar(tk.Frame):
    def __init__(self, master, volume_var=None, **kwargs):
        super().__init__(master, bg="#f0f0f0", **kwargs)  # couleur plus standard
        self.master = master
        from PIL import Image, ImageTk
        import os
        # Correction : utilise le bon master pour les images
        if hasattr(master, 'tk'):
            vol_icon = ImageTk.PhotoImage(Image.open(os.path.join("assets", "cone-de-haut-parleur.png")).resize((24, 24)), master=master)
            vol_icon_mute = ImageTk.PhotoImage(Image.open(os.path.join("assets", "volume-reduit.png")).resize((24, 24)), master=master)
        else:
            vol_icon = ImageTk.PhotoImage(Image.open(os.path.join("assets", "cone-de-haut-parleur.png")).resize((24, 24)))
            vol_icon_mute = ImageTk.PhotoImage(Image.open(os.path.join("assets", "volume-reduit.png")).resize((24, 24)))
        # Correction inversion : 'vol' = volume-reduit (volume faible), 'mute' = cone-de-haut-parleur (muet)
        self.vol_icon = vol_icon_mute
        self.vol_icon_mute = vol_icon
        self.icons = {'vol': vol_icon_mute, 'mute': vol_icon}
        self.volume_var = volume_var or tk.IntVar(value=50)
        self.sound_icon = tk.Label(self, image=self.vol_icon, bg="#f0f0f0", cursor="hand2")
        self.sound_icon.image = self.vol_icon
        self.sound_icon.pack(side="left", padx=(0, 6))
        self.scale = tk.Scale(self, from_=0, to=100, orient="horizontal",
                              variable=self.volume_var, showvalue=0, length=160,
                              command=self.on_volume_change, bg="#f0f0f0", highlightthickness=0)
        self.scale.pack(side="left")
        self.sound_icon.bind("<Button-1>", self.toggle_mute)
        self.on_volume_change(self.volume_var.get())

    def on_volume_change(self, val):
        from core.musique import regler_volume, jouer_musique
        v = int(val)
        icon = self.icons['mute'] if v == 0 else self.icons['vol']
        self.sound_icon.config(image=icon)
        self.sound_icon.image = icon
        try:
            jouer_musique()  # S'assure que le mixer est initialisé
        except Exception:
            pass
        regler_volume(v)

    def toggle_mute(self, _=None):
        if self.volume_var.get() == 0:
            self.volume_var.set(50)
        else:
            self.volume_var.set(0)
        self.on_volume_change(self.volume_var.get())
