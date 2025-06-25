import socket
import select
import logging

logger = logging.getLogger(__name__)

class Proxy:
    """A simple Socks4 proxy server"""

    def __init__(self, username= ""):
        self.socks_version = 4
        self.username = username
        self.protected = True if username else False


    def handle_client(self, connection: socket.socket):
        client_ip = None
        try:
            client_ip = connection.getpeername()[0]
            ver, cmd = connection.recv(2)

            if ver != self.socks_version or cmd != 0x01:
                logger.warning("Invalid SOCKS version %s from %s", ver, client_ip)
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
                    logger.warning("Client %s failed auth with username '%s'", client_ip, userid)
                    connection.close()
                    return
                logger.info("Client %s authenticated successfully as '%s'", client_ip, userid)

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

            logger.info("Client %s requested connection to %s:%d", client_ip, address, port)

            # connect to remote host
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # remote_sock.settimeout(5) # optional
            remote_sock.connect((address, port))

            bind_ip, bind_port = remote_sock.getsockname()

            connection.sendall(b'\x00\x5A' + port.to_bytes(2, 'big') + socket.inet_aton(bind_ip)) # success 
            # connection.settimeout(5) # optional

            logger.info("Connection from %s to %s:%d established", client_ip, address, port)

            self.relay_loop(connection, remote_sock, client_ip)
    
        except Exception as e:
            logger.error("Error handling client %s: %s", client_ip or "Unknown", e)
            try:
                connection.sendall(b'\x00\x5B\x00\x00\x00\x00\x00\x00')
            except:
                pass
            connection.close()
            



    def relay_loop(self, client_socket: socket.socket, remote_socket: socket.socket, client_ip: str):
        logger.debug("Started relaying traffic for %s", client_ip)
        try:
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
        except Exception as e:
            logger.warning("Relay error with %s: %s", client_ip, e)
        finally:
            client_socket.close()
            remote_socket.close()
            logger.debug("Closed connections for %s", client_ip)


    def start(self, host = "0.0.0.0", port = 1080):
        import threading

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()

        logger.info("Socks4 proxy Listening on %s:%d", host, port)

        while True:
            conn, addr = sock.accept()
            logger.info("Accepted connection from %s", addr)
            threading.Thread(target=self.handle_client, args=(conn,)).start()
            

if __name__ == "__main__":
    proxy = Proxy()
    proxy.start()