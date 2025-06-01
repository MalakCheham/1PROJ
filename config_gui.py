import tkinter as tk
import sys
import subprocess
import socket
import os
import customtkinter as ctk
from customtkinter import CTkImage

from plateau_builder import launch_board_builder
from quadrant_editor_live import QuadrantEditorLive
from core.langues import translate
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from core.network.game_network import host_server, join_server, start_discovery, stop_discovery
from core.musique import play_music, set_volume, SoundBar


"""Variables globales"""
variables_dict = {
    "requested_game": sys.argv[1] if len(sys.argv) > 1 else "katarenga",
    "network_mode": "local", 
    "client_socket": None,
    "mode": "1v1",
    "game_ready": False,
    "board_mode": "auto"
}

def center_window(window, width, height, parent_root):
    window.update_idletasks()
    x_position = parent_root.winfo_x() + (parent_root.winfo_width() // 2) - (width // 2)
    y_position = parent_root.winfo_y() + (parent_root.winfo_height() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x_position}+{y_position}")

def back_to_config(root):
    for widget in root.winfo_children():
        widget.destroy()
    afficher_interface_choix(root)

def open_host_window(root_window):
    """Open the window to host a network game"""
    server_name = simpledialog.askstring(translate("host"), translate("enter_server_name"), parent=root_window)
    if not server_name:
        return
    player_name = variables_dict.get("username") or getattr(root_window, 'USERNAME', None)
    variables_dict["host_name"] = server_name
    variables_dict["player_name"] = player_name
    variables_dict["is_host"] = True
    variables_dict["is_client"] = False
    variables_dict["network_mode"] = "network"
    variables_dict["game_ready"] = True
    update_go_button_state(root_window)

def open_network_window(root_window):
    """Open the window to choose between hosting or joining a network game"""
    network_window = ctk.CTkToplevel(root_window)
    network_window.title(translate("choose_game_mode"))
    center_window(network_window, 300, 180, root_window)
    network_window.transient(root_window)
    network_window.grab_set()
    network_window.configure(fg_color="#e0f7fa")
    ctk.CTkLabel(network_window, text=translate("host_or_join"), font=("Helvetica", 13, "bold"), fg_color="#e0f7fa", text_color="#222").pack(pady=15)
    host_button = ctk.CTkButton(network_window, text=translate("host"), font=("Helvetica", 12), width=150, text_color="#222", fg_color="#b2ebf2", command=lambda: [network_window.destroy(), open_host_window(root_window)])
    host_button.pack(pady=5)
    join_button = ctk.CTkButton(network_window, text=translate("join_server"), font=("Helvetica", 12), width=150, text_color="#222", fg_color="#b2ebf2", command=lambda: [network_window.destroy(), open_join_window(root_window)])
    join_button.pack(pady=5)

def open_join_window(root_window):
    """Open the window to join an existing network game"""
    join_window = ctk.CTkToplevel(root_window)
    join_window.title(translate("join_server"))
    center_window(join_window, 350, 350, root_window)
    join_window.transient(root_window)
    join_window.grab_set()
    join_window.configure(fg_color="#e0f7fa")
    ctk.CTkLabel(join_window, text=translate("available_servers"), font=("Helvetica", 13, "bold"), fg_color="#e0f7fa", text_color="#222").pack(pady=10)
    server_list_frame = ctk.CTkFrame(join_window, fg_color="#e0f7fa")
    server_list_frame.pack(pady=5, fill="both", expand=True)
    found_servers = []
    server_buttons = []
    def add_server(server_info):
        found_servers.append(server_info)
        button = ctk.CTkButton(server_list_frame, text=f"{server_info['nom']} ({server_info['ip']}:{server_info['port']})", font=("Helvetica", 12), width=300, anchor="w", text_color="#222", fg_color="#b2ebf2", command=lambda s=server_info: join_server_ui(s, join_window, root_window))
        button.pack(pady=3)
        server_buttons.append(button)
    discovery = start_discovery(add_server)
    def on_close():
        stop_discovery()
        join_window.destroy()
    join_window.protocol("WM_DELETE_WINDOW", on_close)
    def refresh():
        for button in server_buttons:
            button.destroy()
        server_buttons.clear()
        found_servers.clear()
        if hasattr(discovery, 'found'):
            discovery.found.clear()
    ctk.CTkButton(join_window, text=translate("refresh"), command=refresh, fg_color="#b2ebf2", text_color="#222").pack(pady=5)

def start_network_game(root, is_host, player_name=None, player_name_black=None, sock=None, board=None, pieces=None):
    """Lance la partie réseau avec les bons paramètres"""
    for widget in root.winfo_children():
        widget.destroy()
    if is_host:
        player_name_white = player_name
        player_name_black = None
    else:
        player_name_white = None
        player_name_black = player_name_black or player_name
    if variables_dict["requested_game"] == "katarenga":
        from jeux.katarenga import launch_network_game
        launch_network_game(root, is_host=is_host, player_name_white=player_name_white, player_name_black=player_name_black, sock=sock, board=board, pieces=pieces)
    elif variables_dict["requested_game"] == "isolation":
        from jeux.isolation import launch_network_game
        launch_network_game(root, is_host=is_host, player_name_white=player_name_white, player_name_black=player_name_black, sock=sock, board=board, pieces=pieces)
    elif variables_dict["requested_game"] == "congress":
        from jeux.congress import launch_network_game
        launch_network_game(root, is_host=is_host, player_name_white=player_name_white, player_name_black=player_name_black, sock=sock, board=board, pieces=pieces)
    else:
        tk.Label(root, text="Network mode not implemented for this game.", font=("Helvetica", 15, "bold"), fg="#d32f2f", bg="#e6f2ff").pack(pady=60)

def join_server_ui(server, fenetre, root):
    """Tente de rejoindre le serveur sélectionné avec le nom utilisateur existant"""
    fenetre.destroy()
    player_name = variables_dict.get("username") or getattr(root, 'USERNAME', None)
    if not player_name:
        messagebox.showerror(translate("join_server"), translate("error_username"))
        return
    ip = server['ip']
    port = server.get('port', 5555)
    sock = join_server(ip, port)
    if sock:
        variables_dict["game_ready"] = True
        update_go_button_state(root)
        start_network_game(root, is_host=False, player_name=player_name, sock=sock)
    else:
        messagebox.showerror(translate("join_server"), f"{translate('connection_attempt')} {server['nom']} ({ip})\n{translate('connection_failed')}")
        variables_dict["game_ready"] = False
        update_go_button_state(root)

def update_go_button_state(root):
    """Active ou désactive le bouton 'Jouer' selon les choix de l'utilisateur"""
    btn = variables_dict.get("play_btn")
    if not btn:
        return
    if variables_dict["mode"] == "ia":
        btn.configure(state="normal", fg_color="#4CAF50")
    elif variables_dict["mode"] == "1v1":
        if variables_dict["network_mode"] == "local":
            btn.configure(state="normal", fg_color="#4CAF50")
        elif variables_dict["network_mode"] == "network":
            btn.configure(state="normal", fg_color="#4CAF50")
        else:
            btn.configure(state="disabled", fg_color="#888888")
    else:
        btn.configure(state="disabled", fg_color="#888888")
    mode_label = variables_dict.get("mode_label")
    if not mode_label:
        mode_label = ctk.CTkLabel(root, font=("Helvetica", 11, "italic"), fg_color="#e6f2ff", text_color="#004d40")
        mode_label.pack()
        variables_dict["mode_label"] = mode_label
    if variables_dict["network_mode"] == "local":
        mode_label.configure(text=translate("solo_mode"))
    elif variables_dict["network_mode"] == "network":
        if variables_dict.get("is_host"):
            mode_label.configure(text=translate("network_mode_host"))
        elif variables_dict.get("is_client"):
            mode_label.configure(text=translate("network_mode_client"))
        else:
            mode_label.configure(text=translate("network_mode"))
    else:
        mode_label.configure(text="Mode : ?")

def play(root):
    """Lance la partie selon les choix de l'utilisateur"""
    if variables_dict["network_mode"] == "network" and variables_dict.get("is_host"):
        def lancer_partie_reseau(plateau=None, pions=None):
            from core.network.game_network import host_server
            def on_client_connect(attente_win, client_socket, addr):
                attente_win.destroy()
                root.after(0, lambda: start_network_game(root, is_host=True, player_name=variables_dict.get("host_name"), sock=client_socket, board=plateau, pieces=pions))
            def on_stop(attente_win):
                attente_win.destroy()
                messagebox.showinfo(translate("host"), translate("server_stopped"))
                variables_dict["game_ready"] = False
                update_go_button_state(root)
            host_server(
                server_name=variables_dict.get("host_name","Serveur"),
                on_client_connect=on_client_connect,
                on_stop=on_stop,
                root=root,
                tk=tk,
                traduire=translate,
                center_window=lambda win, w, h: center_window(win, w, h, root)
            )
        if variables_dict["board_mode"] == "auto":
            def on_lancer_partie(plateau, pions):
                lancer_partie_reseau(plateau, pions)
            launch_board_builder(variables_dict["requested_game"], False, "auto", on_lancer_partie, root)
        else:
            QuadrantEditorLive(root, on_back=lambda: back_to_config(root), on_network=lancer_partie_reseau)
    elif variables_dict["network_mode"] == "network" and variables_dict.get("is_client"):
        start_network_game(root, is_host=False, player_name=variables_dict.get("player_name"), sock=variables_dict.get("client_socket"))
    else:
        if variables_dict["board_mode"] == "auto":
            for widget in root.winfo_children():
                widget.destroy()
            launch_board_builder(variables_dict["requested_game"], variables_dict["mode"] == "ia", variables_dict["board_mode"], None, root)
        elif variables_dict["board_mode"] == "perso":
            for widget in root.winfo_children():
                widget.destroy()
            QuadrantEditorLive(root, requested_game=variables_dict["requested_game"], on_back=lambda: back_to_config(root), mode=variables_dict["mode"])

def open_mode_choice_window(root):
    """Ouvre la fenêtre pour choisir entre solo et réseau"""
    fenetre = ctk.CTkToplevel(root)
    fenetre.title(translate("choose_game_mode"))
    center_window(fenetre, 300, 180, root)
    fenetre.transient(root)
    fenetre.grab_set()
    fenetre.configure(fg_color="#e0f7fa")
    ctk.CTkLabel(fenetre, text=translate("choose_game_mode"), font=("Helvetica", 13, "bold"), fg_color="#e0f7fa", text_color="#222").pack(pady=15)
    def set_local():
        variables_dict["network_mode"] = "local"
        variables_dict["is_host"] = False
        variables_dict["is_client"] = False
        variables_dict["game_ready"] = True
        update_go_button_state(root)
        fenetre.destroy()
    def set_reseau():
        variables_dict["network_mode"] = "network"
        variables_dict["is_host"] = False
        variables_dict["is_client"] = False
        variables_dict["game_ready"] = False
        update_go_button_state(root)
        fenetre.destroy()
        open_network_window(root)
    btn_solo = ctk.CTkButton(fenetre, text=translate("solo_mode"), font=("Helvetica", 12), width=150, text_color="#222", fg_color="#b2ebf2", command=set_local)
    btn_solo.pack(pady=5)
    btn_reseau = ctk.CTkButton(fenetre, text=translate("network_mode"), font=("Helvetica", 12), width=150, text_color="#222", fg_color="#b2ebf2", command=set_reseau)
    btn_reseau.pack(pady=5)

def afficher_interface_choix(root):
    """Choice screen"""
    for widget in root.winfo_children():
        widget.destroy()
    header_bg = "#e0e0e0"
    header = ctk.CTkFrame(root, fg_color=header_bg, height=80)
    header.pack(side="top", fill="x")
    from core.langues import translate
    username = variables_dict.get('username') or getattr(root, 'USERNAME', None)
    bienvenue = ctk.CTkLabel(header, text=f"{translate('welcome')} {username if username else ''}", font=("Arial", 22, "bold"), fg_color=header_bg, text_color="#5b7fce")
    bienvenue.pack(side="left", padx=32, pady=18)
    img = Image.open(os.path.join("assets", "lyrique.png")).convert("RGBA").resize((40, 40))
    icon = CTkImage(light_image=img, dark_image=img, size=(40, 40))
    btn_icon = ctk.CTkButton(header, image=icon, fg_color=header_bg, width=40, height=40, text="", corner_radius=8, hover_color=header_bg)
    btn_icon.image = icon
    btn_icon.pack(side="right", padx=28, pady=12)

    """Submenu"""
    from core.langues import translate
    def show_logout_menu(event):
        import tkinter as tk
        menu = tk.Menu(root, tearoff=0)
        menu.add_command(label=translate("about"), command=lambda: messagebox.showinfo(translate("about"), translate("about_text")))
        menu.add_command(label=translate("credits"), command=lambda: messagebox.showinfo(translate("credits"), translate("credits_text")))
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
        menu.add_command(label=translate("logout"), command=go_to_login)
        menu.add_command(label=translate("close"), command=root.quit)
        menu.tk_popup(event.x_root, event.y_root)
    btn_icon.bind("<Button-1>", show_logout_menu)

    """Soundbar"""
    from core.musique import SoundBar, set_volume
    from core.parametres import LanguageSelector
    volume_transmis = getattr(root, 'VOLUME', None)
    initial_volume = 50
    if variables_dict.get('volume') is not None:
        initial_volume = variables_dict['volume']
    elif volume_transmis is not None:
        initial_volume = volume_transmis
    elif hasattr(root, 'volume_var'):
        try:
            initial_volume = root.volume_var.get()
        except Exception:
            pass
    if hasattr(root, 'volume_var'):
        root.volume_var.set(initial_volume)
        soundbar = SoundBar(root, volume_var=root.volume_var)
    else:
        root.volume_var = tk.IntVar(value=initial_volume)
        soundbar = SoundBar(root, volume_var=root.volume_var)
    set_volume(root.volume_var.get())
    soundbar.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)

    """Language"""
    def on_language_changed(new_lang):
        try:
            current_volume = soundbar.volume_var.get()
        except Exception:
            current_volume = variables_dict.get('volume')
        current_mode = variables_dict.get("mode", "1v1")
        current_network_mode = variables_dict.get("network_mode", "local")
        current_board_mode = variables_dict.get("board_mode", "auto")
        current_username = username
        import importlib
        import core.langues
        importlib.reload(core.langues)
        main(root, variables_dict["requested_game"], username=current_username, volume=current_volume, mode=current_mode, network_mode=current_network_mode, board_mode=current_board_mode)
    lang_selector = LanguageSelector(root, assets_dir="assets", callback=on_language_changed)
    lang_selector.place(relx=1.0, rely=1.0, anchor="se", x=-18, y=-18)

    main_frame = ctk.CTkFrame(root, fg_color="#f0f0f0")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(main_frame, text=translate(variables_dict["requested_game"]).upper(), font=("Helvetica", 16, "bold"), text_color="#004d40", fg_color="#f0f0f0").pack(pady=10)

    variables_dict["mode_var"] = ctk.StringVar(value=variables_dict["mode"])
    variables_dict["board_mode_var"] = ctk.StringVar(value=variables_dict["board_mode"])

    frame_mode = ctk.CTkFrame(main_frame, fg_color="#f0f0f0")
    frame_mode.pack(pady=10)

    frame1 = ctk.CTkFrame(frame_mode, fg_color="#f0f0f0")
    frame1.pack(pady=10)

    ctk.CTkRadioButton(frame1, text=translate("mode_1v1"), variable=variables_dict["mode_var"], value="1v1", font=("Helvetica", 12), fg_color="#219150", text_color="#222", command=lambda: on_mode_change(root)).pack(anchor="w", pady=2)
    ctk.CTkRadioButton(frame1, text=translate("mode_ai"), variable=variables_dict["mode_var"], value="ia", font=("Helvetica", 12), fg_color="#219150", text_color="#222", command=lambda: on_mode_change(root)).pack(anchor="w", pady=2)

    frame_board = ctk.CTkFrame(main_frame, fg_color="#f0f0f0")
    frame_board.pack(pady=10)

    ctk.CTkLabel(frame_board, text=translate("board"), fg_color="#f0f0f0", font=("Helvetica", 13), text_color="#222").pack()
    ctk.CTkRadioButton(frame_board, text=translate("auto_board"), variable=variables_dict["board_mode_var"], value="auto", fg_color="#219150", font=("Helvetica", 12), text_color="#222", command=lambda: on_board_mode_change(root)).pack(anchor="w", padx=20)
    ctk.CTkRadioButton(frame_board, text=translate("custom_quadrants"), variable=variables_dict["board_mode_var"], value="perso", fg_color="#219150", font=("Helvetica", 12), text_color="#222", command=lambda: on_board_mode_change(root)).pack(anchor="w", padx=20)

    btns_frame = ctk.CTkFrame(main_frame, fg_color="#f0f0f0")
    btns_frame.pack(pady=20)
    variables_dict["play_btn"] = ctk.CTkButton(btns_frame, text=translate("play"), command=lambda: play(root), font=("Helvetica", 12, "bold"), fg_color="#4CAF50", text_color="white", width=150, corner_radius=8, state="disabled")
    variables_dict["play_btn"].pack(side="left", padx=5)
    btn_mode_select = ctk.CTkButton(btns_frame, text=translate("game_mode"), font=("Helvetica", 12, "bold"), fg_color="#4CAF50", text_color="white", width=150, corner_radius=8, command=lambda: open_mode_choice_window(root))
    btn_mode_select.pack(side="left", padx=5)

    if variables_dict.get("mode_label"):
        variables_dict["mode_label"].destroy()
    variables_dict["mode_label"] = ctk.CTkLabel(main_frame, font=("Helvetica", 11, "italic"), fg_color="#f0f0f0", text_color="#004d40")
    variables_dict["mode_label"].pack(pady=(0, 10))
    update_go_button_state(root)

    """Bouton retour"""
    def return_to_menu():
        import menu_gui
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
        menu_gui.show_menu(root, username=variables_dict.get("username") or getattr(root, "USERNAME", None), volume=current_volume)
    img_retour = Image.open(os.path.join("assets", "en-arriere.png")).resize((48, 48))
    icon_retour = CTkImage(light_image=img_retour, dark_image=img_retour, size=(48, 48))
    btn_retour = ctk.CTkButton(root, image=icon_retour, command=return_to_menu, fg_color="#f0f0f0", width=48, height=48, text="", corner_radius=8, hover_color="#e0e0e0")
    btn_retour.image = icon_retour
    btn_retour.place(relx=0.0, rely=0.5, anchor="w", x=18)

def on_mode_change(root):
    """Met à jour le mode de jeu choisi dans le dictionnaire"""
    variables_dict["mode"] = variables_dict["mode_var"].get()
    update_go_button_state(root)

def on_board_mode_change(root):
    """Met à jour le mode de plateau choisi dans le dictionnaire"""
    variables_dict["board_mode"] = variables_dict["board_mode_var"].get()

def get_local_ip():
    """Renvoie l'adresse IP locale de la machine (pour le réseau)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def main(root, jeu_type, username=None, volume=None, mode=None, network_mode=None, board_mode=None):
    global variables_dict
    variables_dict = {
        "requested_game": jeu_type,
        "network_mode": network_mode if network_mode is not None else "local",
        "client_socket": None,
        "mode": mode if mode is not None else "1v1",
        "game_ready": False,
        "board_mode": board_mode if board_mode is not None else "auto",
        "username": username,
        "volume": volume
    }
    
    if username:
        setattr(root, 'USERNAME', username)
    afficher_interface_choix(root)