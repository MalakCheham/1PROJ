import tkinter as tk
from tkinter import messagebox

COULEURS = ["R", "J", "B", "V"]
COULEURS_HEX = {
    "R": "#ff9999", "J": "#ffffb3", "B": "#99ccff", "V": "#b3ffb3"
}

class QuadrantEditorLive:
    def __init__(self, root, retour_callback, network_callback=None, jeu_demande=None):
        from core.langues import traduire
        self.root = root
        self.retour_callback = retour_callback
        self.network_callback = network_callback
        self.current_color = "R"
        self.quadrants = []
        self.grille = [[None for _ in range(4)] for _ in range(4)]
        self.jeu_demande = jeu_demande if jeu_demande is not None else getattr(root, 'jeu_demande', None)

        for widget in root.winfo_children():
            widget.destroy()

        root.configure(bg="#f0f4f8")

        header_bg = "#e0e0e0"
        header = tk.Frame(root, bg=header_bg, height=80)
        header.pack(side="top", fill="x")
        from core.langues import traduire
        username = getattr(root, 'USERNAME', None)
        titre = tk.Label(header, text=traduire("creer_quadrant_4x4"), font=("Arial", 22, "bold"), bg=header_bg, fg="#5b7fce")
        titre.pack(side="left", padx=32, pady=18)
        from PIL import Image, ImageTk
        import os
        img = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
        if hasattr(root, 'tk'):
            icon = ImageTk.PhotoImage(img, master=root)
        else:
            icon = ImageTk.PhotoImage(img)
        self.icon = icon  # Prevent garbage collection
        btn_icon = tk.Button(header, image=self.icon, bg=header_bg, bd=0, relief="flat", cursor="hand2", activebackground=header_bg, highlightthickness=0)
        btn_icon.image = self.icon
        btn_icon.pack(side="right", padx=28, pady=12)

        # Sous-menu (about, credits, logout, close)
        from tkinter import messagebox
        def show_logout_menu(event):
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label=traduire("a_propos"), command=lambda: messagebox.showinfo(traduire("a_propos"), traduire("a_propos_texte")))
            menu.add_command(label=traduire("credits"), command=lambda: messagebox.showinfo(traduire("credits"), traduire("credits_texte")))
            menu.add_separator()
            def go_to_login():
                import login
                try:
                    current_volume = root.volume_var.get()
                except AttributeError:
                    try:
                        from core.musique import SoundBar
                        current_volume = SoundBar.last_volume
                    except Exception:
                        current_volume = None
                for w in root.winfo_children():
                    w.destroy()
                login.show_login(root, volume=current_volume)
            menu.add_command(label=traduire("se_deconnecter"), command=go_to_login)
            menu.add_command(label=traduire("fermer"), command=root.quit)
            menu.tk_popup(event.x_root, event.y_root)
        btn_icon.bind("<Button-1>", show_logout_menu)

        """barre de son et gestion langue"""
        from core.musique import SoundBar, regler_volume
        from core.parametres import LanguageSelector
        volume_transmis = getattr(root, 'VOLUME', None)
        initial_volume = 50
        if hasattr(root, 'volume_var'):
            try:
                initial_volume = root.volume_var.get()
            except Exception:
                pass
            root.volume_var.set(initial_volume)
            soundbar = SoundBar(root, volume_var=root.volume_var)
        else:
            root.volume_var = tk.IntVar(value=initial_volume)
            soundbar = SoundBar(root, volume_var=root.volume_var)
        regler_volume(root.volume_var.get())
        soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)
        def on_language_changed(new_lang):
            import importlib
            import core.langues
            importlib.reload(core.langues)
            self.reload_ui()
        lang_selector = LanguageSelector(root, assets_dir="assets", callback=on_language_changed)
        lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

        # --- Main Frame ---
        main_frame = tk.Frame(root, bg="#f0f4f8")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.cadre = tk.Frame(main_frame, bg="#f0f4f8")
        self.cadre.pack(pady=5)

        self.boutons = [[None for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                btn = tk.Button(self.cadre, text="", width=4, height=2)
                btn.grid(row=i, column=j, padx=2, pady=2)
                btn.bind("<Button-1>", lambda e, x=i, y=j: self.peindre_case(x, y, e))
                btn.bind("<Button-3>", lambda e, x=i, y=j: self.peindre_case(x, y, e))
                self.boutons[i][j] = btn

        self.choix_couleurs = tk.Frame(main_frame, bg="#f0f4f8")
        self.choix_couleurs.pack(pady=10)

        self.color_buttons = {}
        for c in COULEURS:
            btn = tk.Button(self.choix_couleurs, bg=COULEURS_HEX[c], width=4, height=2, command=lambda col=c: self.choisir_couleur(col))
            btn.pack(side="left", padx=10)
            self.color_buttons[c] = btn
        self.update_color_highlight()

        self.controls = tk.Frame(main_frame, bg="#f0f4f8")
        self.controls.pack(pady=10)

        btn_save = tk.Button(self.controls, text=traduire("sauvegarder_quadrant"), command=self.valider_quadrant, font=("Helvetica", 10), bg="#4CAF50", fg="white", padx=10, pady=5)
        btn_new = tk.Button(self.controls, text=traduire("nouveau_quadrant"), command=self.reset, font=("Helvetica", 10), padx=10, pady=5)
        btn_save.pack(side="left", padx=8)
        btn_new.pack(side="left", padx=8)

        self.info = tk.Label(main_frame, text=traduire("quadrant_num", num=1), font=("Helvetica", 12), bg="#f0f4f8")
        self.info.pack(pady=5)

        self.play_button = tk.Button(main_frame, text=traduire("jouer_avec_quadrants"), command=self.construire_plateau, font=("Helvetica", 12, "bold"), bg="#0066cc", fg="white")
        self.play_button.pack(pady=10)
        self.play_button.config(state="disabled")


        img_retour = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
        if hasattr(root, 'tk'):
            icon_retour = ImageTk.PhotoImage(img_retour, master=root)
        else:
            icon_retour = ImageTk.PhotoImage(img_retour)
        self.icon_retour = icon_retour
        btn_retour = tk.Button(root, image=self.icon_retour, command=self.retour_callback, bg="#f0f4f8", bd=0, relief="flat", cursor="hand2", activebackground="#e0e0e0")
        btn_retour.image = self.icon_retour
        btn_retour.place(relx=0.0, rely=0.5, anchor="w", x=18)

    def choisir_couleur(self, couleur):
        self.current_color = couleur
        self.update_color_highlight()

    def update_color_highlight(self):
        for c, btn in self.color_buttons.items():
            if c == self.current_color:
                btn.config(relief="solid", bd=4, highlightbackground="#333", highlightcolor="#333")
            else:
                btn.config(relief="flat", bd=2, highlightbackground="#f0f4f8", highlightcolor="#f0f4f8")

    def peindre_case(self, i, j, event=None):
        if event is not None and event.num == 3:
            for x in range(4):
                for y in range(4):
                    self.boutons[x][y].config(bg=COULEURS_HEX[self.current_color])
                    self.grille[x][y] = self.current_color
        else:
            self.boutons[i][j].config(bg=COULEURS_HEX[self.current_color])
            self.grille[i][j] = self.current_color

    def valider_quadrant(self):
        from core.langues import traduire
        if any(None in row for row in self.grille):
            messagebox.showwarning(traduire("incomplet"), traduire("toutes_cases_colorees"))
            return
        self.quadrants.append({"recto": [row[:] for row in self.grille]})
        if len(self.quadrants) == 4:
            messagebox.showinfo("OK", traduire("quatre_quadrants_prets"))
            self.play_button.config(state="normal")
        else:
            self.reset()
            if hasattr(self, 'info'):
                self.info.config(text=traduire("quadrant_num", num=len(self.quadrants)+1))

    def reset(self):
        self.grille = [[None for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                self.boutons[i][j].config(bg="SystemButtonFace")
        from core.langues import traduire
        if hasattr(self, 'info'):
            self.info.config(text=traduire("quadrant_num", num=len(self.quadrants)+1))

    def construire_plateau(self):
        if len(self.quadrants) != 4:
            messagebox.showerror("Erreur", "Il faut 4 quadrants pour construire le plateau.")
            return

        from core.plateau import Plateau
        from core.joueur import Joueur
        from jeux.katarenga import JeuKatarenga
        from jeux.congress import JeuCongress
        from jeux.isolation import JeuIsolation

        plateau = Plateau()
        positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
        for i, q in enumerate(self.quadrants):
            bloc = q["recto"]
            for dx in range(4):
                for dy in range(4):
                    plateau.cases[positions[i][0] + dx][positions[i][1] + dy] = bloc[dx][dy]

        pions = {
            'X': {(0, j) for j in range(8)},
            'O': {(7, j) for j in range(8)}
        }
        joueurs = [Joueur(0, 'X'), Joueur(1, 'O')]
        if self.network_callback:
            self.network_callback(plateau, pions)
        else:
            for widget in self.root.winfo_children():
                widget.destroy()
            if hasattr(self, 'jeu_demande') and self.jeu_demande == 'congress':
                JeuCongress(plateau, joueurs, root=self.root).jouer()
            elif hasattr(self, 'jeu_demande') and self.jeu_demande == 'isolation':
                JeuIsolation(plateau, joueurs, root=self.root).jouer()
            else:
                JeuKatarenga(plateau, joueurs, root=self.root).jouer()

    def reload_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root, self.retour_callback, self.network_callback)
