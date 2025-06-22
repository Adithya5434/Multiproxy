# protocol - https://medium.com/@nimit95/socks-5-a-proxy-protocol-b741d3bec66c
#          - https://datatracker.ietf.org/doc/html/rfc1929
#          - https://datatracker.ietf.org/doc/html/rfc1928

import socket
import select


class Proxy:
    """A simple SOCKS5 proxy server"""

    def __init__(self, username="", password=""):
        self.username = username
        self.password = password
        self.socks_version = 5
        self.protected = True if username or password else False
            
    def handle_client(self, connection: socket.socket):
        ver, num_methods = connection.recv(2)

        if ver != self.socks_version:
            connection.close()
            return

        methods = list(connection.recv(num_methods))

        # check for authentication
        if self.protected:
            if 2 not in set(methods):  # Check if authentication is supported (only user/pass is supported in this proxy)
                connection.sendall(b'\x05\xFF') # NO ACCEPTABLE METHODS
                connection.close()
                return
            
            connection.sendall(b'\x05\x02')  # USERNAME/PASSWORD AUTHENTICATION

            if not self.verify_credentials(connection):
                return
        else:
            connection.sendall(b'\x05\x00')  # NO AUTHENTICATION REQUIRED

    
        ver, cmd, rsv, address_type = connection.recv(4)

        if ver != self.socks_version or rsv != 0:
            connection.close()
            return
        
        if cmd not in (1,): # 1-CONNECT 2-BIND  3-UDP ASSOCIATE 
            connection.sendall(b'\x05\x07\x00' + address_type.to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00\x00') # Command not supported
            connection.close()
            return
        
        if address_type not in (1,3): # 1-ipv4, 3-domain, 4-ipv6
            connection.sendall(b'\x05\x08\x00' + address_type.to_bytes(1, 'big') + b'\x00\x00\x00\x00\x00\x00') # Address type not supported
            connection.close()
            return


        if address_type == 1: # IPV4
            address = socket.inet_ntoa(connection.recv(4))

        elif address_type == 3:
            domain_length = connection.recv(1)[0]
            domain_name = connection.recv(domain_length).decode()
            address = socket.gethostbyname(domain_name)
        
        port = int.from_bytes(connection.recv(2), 'big')

        try:
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.settimeout(5) # optional
            remote_sock.connect((address, port))

            bind_ip, bind_port = remote_sock.getsockname()

            connection.sendall(b'\x05\x00\x00\x01' + socket.inet_aton(bind_ip) + bind_port.to_bytes(2, 'big')) # succeeded
            connection.settimeout(5) # optional
            
            print(f"[SOCKS4] {connection.getpeername()} -> {address}:{port}")

            self.relay_loop(connection, remote_sock)
        except:
            connection.sendall(b'\x05\x04\x00\x01\x00\x00\x00\x00\x00\x00') # Host unreachable
            connection.close()
            return
        
        

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



    def verify_credentials(self, connection: socket.socket):
        ver = connection.recv(1)[0]

        ULEN = ord(connection.recv(1))
        UNAME = connection.recv(ULEN).decode()

        PLEN = ord(connection.recv(1))
        PNAME = connection.recv(PLEN).decode()

        if UNAME == self.username and PNAME == self.password:
            connection.sendall(b'\x05\x00')
            return True
        
        connection.sendall(b'\x05\xFF')
        connection.close()
        return False

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
