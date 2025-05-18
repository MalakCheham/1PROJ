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

def start_server(host="0.0.0.0", port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(2)
    print(traduire("server_listening_on").format(host=host, port=port))
    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()