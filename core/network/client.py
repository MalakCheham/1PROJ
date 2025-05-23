import socket
from core.langues import traduire

def start_client(host="127.0.0.1", port=5000):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        print(traduire("connected_to_server"))
        return client
    except Exception as e:
        print(traduire("connection_failed"), e)
        return None

def send_move(client, move):
    client.sendall(move.encode())

def receive_move(client):
    data = client.recv(1024)
    return data.decode()