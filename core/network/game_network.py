import threading
from core.network.server import wait_for_first_client
from core.network.client import start_client
from core.network.discovery import ServerBroadcaster, ServerDiscovery

broadcaster = None
discovery = None

"""Network host & join"""
def host_server(server_name, port=5555, on_client_connect=None, on_stop=None, root=None, tk=None, traduire=None, center_window=None):
    global broadcaster
    ip = _get_local_ip()
    broadcaster = ServerBroadcaster(server_name, port)
    broadcaster.start()
    print(f"Serveur créé: {server_name} ({ip}:{port})")
    attente_win = tk.Toplevel(root)
    attente_win.title(traduire("heberger"))
    center_window(attente_win, 300, 120)
    attente_win.transient(root)
    attente_win.grab_set()
    attente_win.configure(bg="#e0f7fa")
    label = tk.Label(attente_win, text=traduire("waiting_for_player"), font=("Helvetica", 13, "bold"), bg="#e0f7fa")
    label.pack(pady=30)
    def server_thread():
        client_socket, addr = wait_for_first_client(port=port)
        if broadcaster:
            broadcaster.stop()
        if on_client_connect:
            on_client_connect(attente_win, client_socket, addr)
    threading.Thread(target=server_thread, daemon=True).start()
    def stop_callback():
        stop_server()
        if on_stop:
            on_stop(attente_win)
    attente_win.protocol("WM_DELETE_WINDOW", stop_callback)
    return attente_win, stop_callback

def stop_server():
    global broadcaster
    if broadcaster:
        broadcaster.stop()
        broadcaster = None
        print("Serveur arrêté par l'utilisateur.")

def join_server(ip, port=5555):
    return start_client(ip, port)

def start_discovery(on_server_found):
    global discovery
    discovery = ServerDiscovery(on_server_found)
    discovery.start()
    return discovery

def stop_discovery():
    global discovery
    if discovery:
        discovery.stop()
        discovery = None

def _get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip