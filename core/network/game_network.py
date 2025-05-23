import threading
from core.network.server import wait_for_first_client
from core.network.client import start_client
from core.network.discovery import ServerBroadcaster, ServerDiscovery

_broadcaster = None
_discovery = None

# === Server Side ===
def host_server(server_name, port=5555, on_client_connect=None, on_stop=None, root=None, tk=None, traduire=None, center_window=None):
    """
    Start hosting a server and broadcasting it on the network.
    Calls on_client_connect() when a client connects.
    Calls on_stop() if the server is stopped (e.g. window closed).
    Returns a tuple (attente_win, stop_callback)
    """
    global _broadcaster
    ip = _get_local_ip()
    _broadcaster = ServerBroadcaster(server_name, port)
    _broadcaster.start()
    print(f"Serveur créé: {server_name} ({ip}:{port})")
    attente_win = tk.Toplevel(root)
    attente_win.title(traduire("heberger"))
    center_window(attente_win, 300, 120)
    attente_win.transient(root)
    attente_win.grab_set()
    attente_win.configure(bg="#e0f7fa")
    label = tk.Label(attente_win, text=traduire("attente_joueur"), font=("Helvetica", 13, "bold"), bg="#e0f7fa")
    label.pack(pady=30)
    def server_thread():
        client_socket, addr = wait_for_first_client(port=port)
        if _broadcaster:
            _broadcaster.stop()
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
    global _broadcaster
    if _broadcaster:
        _broadcaster.stop()
        _broadcaster = None
        print("Serveur arrêté par l'utilisateur.")

# === Client Side ===
def join_server(ip, port=5555):
    return start_client(ip, port)

# === Discovery ===
def start_discovery(on_server_found):
    """
    Start network discovery. Calls on_server_found(server_dict) for each found server.
    Returns the discovery object (call .stop() to end).
    """
    global _discovery
    _discovery = ServerDiscovery(on_server_found)
    _discovery.start()
    return _discovery

def stop_discovery():
    global _discovery
    if _discovery:
        _discovery.stop()
        _discovery = None

# === Utility ===
def _get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
