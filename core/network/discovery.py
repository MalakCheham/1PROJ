import socket
import threading
import time

BROADCAST_PORT = 50010
BROADCAST_INTERVAL = 1.0 
BROADCAST_MESSAGE_PREFIX = "GAME_SERVER:"

class ServerBroadcaster(threading.Thread):
    def __init__(self, server_name, tcp_port):
        super().__init__(daemon=True)
        self.server_name = server_name
        self.tcp_port = tcp_port
        self.running = True

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = f"{BROADCAST_MESSAGE_PREFIX}{self.server_name}:{self.tcp_port}".encode()
        while self.running:
            try:
                sock.sendto(message, ("<broadcast>", BROADCAST_PORT))
            except Exception as e:
                print("Broadcast error:", e)
            time.sleep(BROADCAST_INTERVAL)
        sock.close()

    def stop(self):
        self.running = False

class ServerDiscovery(threading.Thread):
    def __init__(self, on_server_found):
        super().__init__(daemon=True)
        self.on_server_found = on_server_found
        self.running = True
        self.found = set()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", BROADCAST_PORT))
        sock.settimeout(1.0)
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = data.decode()
                if msg.startswith(BROADCAST_MESSAGE_PREFIX):
                    content = msg[len(BROADCAST_MESSAGE_PREFIX):]
                    name, port = content.rsplit(":", 1)
                    key = (addr[0], port)
                    if key not in self.found:
                        self.found.add(key)
                        self.on_server_found({"nom": name, "ip": addr[0], "port": int(port)})
            except socket.timeout:
                continue
            except Exception as e:
                print("Discovery error:", e)
        sock.close()

    def stop(self):
        self.running = False
