import socket
import select

class Proxy:
    def __init__(self, username= ""):
        self.socks_version = 4
        self.username = username
        self.protected = True if username else False

    def handle_client(self, connection: socket.socket):
        ver, cmd = connection.recv(2)

        if ver != self.socks_version or cmd != 0x01:
            connection.close()
            return
        
        port = int.from_bytes(connection.recv(2), 'big')
        address = socket.inet_ntoa(connection.recv(4))
        
        # read userid
        userid = b''
        while True:
            u_char = connection.recv(1)
            if u_char == b'\x00':
                break
            userid += u_char

        # check for authentication
        if self.protected:
            if userid.decode(errors='ignore') != self.username:
                connection.close()
                return

        # check if its socks4a
        if address.startswith("0.0.0."):
            domain = b''
            while True:
                d_char = connection.recv(1)
                if d_char == b'\x00':
                    break
                domain += d_char

            domain = domain.decode()
            address = socket.gethostbyname(domain)

        # connect to remote host
        try:
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.settimeout(5) # optional
            remote_sock.connect((address, port))

            bind_ip, bind_port = remote_sock.getsockname()

            connection.sendall(b'\x00\x5A' + port.to_bytes(2, 'big') + socket.inet_aton(bind_ip)) # success 
            connection.settimeout(5) # optional

            print(f"[SOCKS4] {connection.getpeername()} -> {userid.decode(errors='ignore')}@{address}:{port}")

            self.relay_loop(connection, remote_sock)

        except Exception as e:
            connection.sendall(b'\x00\x5B\x00\x00\x00\x00\x00\x00')
            connection.close()
            print(f"[SOCKS4 ERROR] ({connection.getpeername()} -> {userid.decode(errors='ignore')}@{address}:{port}): {e}")
            return
        
        print(f"[SOCKS4] Connection closed () -> {userid.decode(errors='ignore')}@{address}:{port})")
    
    def relay_loop(self, client_socket: socket.socket, remote_socket: socket.socket):
        while True:
            readable, _, _ = select.select([client_socket, remote_socket], [], [])

            if client_socket in readable:
                data = client_socket.recv(4096)
                if not data:
                    break
                remote_socket.sendall(data)

            if remote_socket in readable:
                data = remote_socket.recv(4096)
                if not data:
                    break
                client_socket.sendall(data)

        client_socket.close()
        remote_socket.close()


    def start(self, host = "0.0.0.0", port = 1080):
        import threading

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()

        print(f"Listening on {host}:{port}")

        while True:
            conn, addr = sock.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(conn,)).start()
            

if __name__ == "__main__":
    proxy = Proxy()
    proxy.start()