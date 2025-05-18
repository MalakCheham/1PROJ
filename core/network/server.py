import socket
import threading
from core.langues import traduire

def handle_client(client_socket, addr):
    print(traduire("client_connected_from").format(addr=addr))
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            print(traduire("received_from").format(addr=addr, msg=data.decode()))
        except:
            break
    client_socket.close()
    print(traduire("client_disconnected").format(addr=addr))

def wait_for_first_client(server_ready=None, host="0.0.0.0", port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(2)
    client_socket, addr = server.accept()
    if server_ready is not None:
        server_ready.set()
    handle_client(client_socket, addr)