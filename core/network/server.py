import socket
from core.langues import translate

"""server module for handling client connections and messages"""
def handle_client(client_socket, addr):
    print(translate("client_connected_from").format(addr=addr))
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(translate("received_from").format(addr=addr, msg=data.decode()))
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()
        print(translate("client_disconnected").format(addr=addr))

def wait_for_first_client(server_ready=None, host="0.0.0.0", port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((host, port))
        server.listen(2)
        client_socket, addr = server.accept()
        if server_ready is not None:
            server_ready.set()
        return client_socket, addr
    except Exception as e:
        print(f"Error waiting for client: {e}")
        return None, None
    finally:
        server.close()