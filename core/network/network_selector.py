import tkinter as tk
from core.langues import traduire

class network_selector:
    def __init__(self, parent, on_result):
        self.parent = parent
        self.on_result = on_result
        self.ask_network_mode()

    def ask_network_mode(self):
        win = tk.Toplevel(self.parent)
        win.title(traduire("choisir_mode"))
        win.geometry("300x120")
        win.grab_set()
        tk.Label(win, text=traduire("jouer_local_ou_online"), font=("Helvetica", 12)).pack(pady=10)
        tk.Button(win, text=traduire("local"), width=12, command=lambda: self._choose("local", win)).pack(side="left", padx=20, pady=20)
        tk.Button(win, text=traduire("reseau"), width=12, command=lambda: [win.destroy(), self.ask_host_or_join()]).pack(side="right", padx=20, pady=20)

    def ask_host_or_join(self):
        win = tk.Toplevel(self.parent)
        win.title(traduire("mode_onligne"))
        win.geometry("300x120")
        win.grab_set()
        tk.Label(win, text=traduire("host_or_join"), font=("Helvetica", 12)).pack(pady=10)
        tk.Button(win, text=traduire("host"), width=12, command=lambda: self._choose("host", win)).pack(side="left", padx=20, pady=20)
        tk.Button(win, text=traduire("join"), width=12, command=lambda: self._choose("join", win)).pack(side="right", padx=20, pady=20)

    def _choose(self, value, win):
        win.destroy()
        self.on_result(value)