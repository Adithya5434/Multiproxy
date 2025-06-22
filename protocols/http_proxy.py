import select
import socket
import threading

class Proxy:
    def __init__(self, ):
        pass

    def handle_client(self, connection: socket.socket):
        try:
            first_line = connection.recv(4096).decode(errors="ignore").split("\n")[0]
            method = first_line.split(" ")[0]

            if method.upper() == "CONNECT": # https
                target = first_line.split(" ")[1]
                host, port = target.split(":")
                port = int(port)

                remote_sock = socket.create_connection((host, port))
                # remote_sock.settimeout(5) # optional

                connection.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                threading.Thread(target=self.forward, args=(connection, remote_sock)).start()
                threading.Thread(target=self.forward, args=(remote_sock, connection)).start()
        
            else: # http


        except:
            connection.close()
            return


    def forward(self, source: socket.socket, destination: socket.socket):
        try:
            while True:
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