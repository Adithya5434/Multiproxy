import socket
import select
import threading

class Proxy:
    def __init__(self, mc_host = "localhost", mc_port = 25565):
        """mc_host/mc_port - internal minecraft host and port"""
        self.mc_port = mc_port
        self.mc_host = mc_host

    def handle_client(self, connection: socket.socket):
        try:
            remote_socket = socket.create_connection((self.mc_host, self.mc_port))
            remote_socket.settimeout(10)
            connection.settimeout(10)

            threading.Thread(target=self.relay_loop, args=(connection, remote_socket)).start()
            threading.Thread(target=self.relay_loop, args=(remote_socket, connection)).start()

            print(f"[Minecraft] Connection closed by {connection.getpeername()}")
        except:
            connection.close()
            print(f"[Minecraft] Connection failed to {self.mc_host}:{self.mc_port}")
            return

    def relay_loop(self, source: socket.socket, destination: socket.socket):
        try:
            while True:
                readable, _, _ = select.select([source], [], [])

                if source in readable:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.sendall(data)
        except:
            pass
        source.close()
        destination.close()

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