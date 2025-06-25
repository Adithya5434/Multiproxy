import socket
import select
import threading
import logging

logger = logging.getLogger(__name__)

class Proxy:
    def __init__(self, mc_host = "localhost", mc_port = 25565):
        self.mc_port = mc_port
        self.mc_host = mc_host

    def handle_client(self, connection: socket.socket):
        client_ip = None
        try:
            client_ip = connection.getpeername()[0]
            remote_socket = socket.create_connection((self.mc_host, self.mc_port))

            remote_socket.settimeout(10)
            connection.settimeout(10)

            threading.Thread(target=self.relay_loop, args=(connection, remote_socket, client_ip)).start()
            threading.Thread(target=self.relay_loop, args=(remote_socket, connection, client_ip)).start()
        except Exception as e:
            logging.error("Error handling client %s: %s", client_ip or "Unknown", e)
            connection.close()
            return

    def relay_loop(self, source: socket.socket, destination: socket.socket, client_ip: str):
        logger.info("Relaying connection from %s to %s:%d", client_ip, self.mc_host, self.mc_port)
        try:
            while True:
                readable, _, _ = select.select([source], [], [])

                if source in readable:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.sendall(data)
        except Exception as e:
            logger.warning("Relay error with %s: %s", client_ip, e)
        finally:
            source.close()
            destination.close()
            logger.debug("Closed connections for %s", client_ip)

    def start(self, host="0.0.0.0", port=8080):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()

        print(f"[Minecraft Proxy] Listening on {host}:{port}")

        while True:
            conn, addr = sock.accept()
            print(f"[Minecraft Proxy] Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(conn,)).start()

if __name__ == "__main__":
    proxy = Proxy()
    proxy.start()