import socket
from core.langues import translate
from core.musique import set_volume, SoundBar

"""network client module for connecting to a game server"""

def start_client(host="127.0.0.1", port=5555):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        print(translate("connected_to_server"))
        return client
    except Exception as e:
        print(translate("connection_failed"), e)
        return None

def send_move(client, move):
    try:
        client.sendall(move.encode())
    except Exception as e:
        print(f"Error sending move: {e}")

def receive_move(client):
    try:
        data = client.recv(1024)
        return data.decode()
    except Exception as e:
        print(f"Error receiving move: {e}")
        return None

def update_volume(root):
    set_volume(root.volume_var.get())

def create_soundbar(root):
    soundbar = SoundBar(root, volume_var=root.volume_var)