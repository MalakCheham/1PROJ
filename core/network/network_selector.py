import tkinter as tk
from core.langues import translate
from core.musique import set_volume, SoundBar

"""network selector module for choosing game mode"""
class network_selector:
    def __init__(self, parent, on_result, root, volume_var):
        self.parent = parent
        self.on_result = on_result
        self.root = root
        self.volume_var = volume_var
        self.ask_network_mode()

    def ask_network_mode(self):
        win = tk.Toplevel(self.parent)
        win.title(translate("choose_mode"))
        win.geometry("300x120")
        win.grab_set()
        tk.Label(win, text=translate("play_locally_or_online"), font=("Helvetica", 12)).pack(pady=10)
        tk.Button(win, text=translate("local"), width=12, command=lambda: self.choose("local", win)).pack(side="left", padx=20, pady=20)
        tk.Button(win, text=translate("network"), width=12, command=lambda: [win.destroy(), self.ask_host_or_join()]).pack(side="right", padx=20, pady=20)

    def ask_host_or_join(self):
        win = tk.Toplevel(self.parent)
        win.title(translate("online_mode"))
        win.geometry("300x120")
        win.grab_set()
        tk.Label(win, text=translate("host_or_join"), font=("Helvetica", 12)).pack(pady=10)
        tk.Button(win, text=translate("host"), width=12, command=lambda: self.choose("host", win)).pack(side="left", padx=20, pady=20)
        tk.Button(win, text=translate("join"), width=12, command=lambda: self.choose("join", win)).pack(side="right", padx=20, pady=20)

    def choose(self, value, win):
        win.destroy()
        set_volume(self.volume_var.get())
        soundbar = SoundBar(self.root, volume_var=self.volume_var)
        set_volume(self.root.volume_var.get())
        soundbar = SoundBar(self.root, volume_var=self.root.volume_var)