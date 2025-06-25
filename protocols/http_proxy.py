import socket
import threading
import logging

logger = logging.getLogger(__name__)

class Proxy:
    """A simple HTTP proxy server"""
    
    def handle_client(self, connection: socket.socket):
        client_ip = None
        try:
            client_ip = connection.getpeername()[0]

            request = connection.recv(4096)
            if not request:
                connection.close()
                return
            
            first_line = request.decode(errors="ignore").split("\n")[0]
            method = first_line.split(" ")[0]

            # https
            if method.upper() == "CONNECT":
                target = first_line.split(" ")[1]
                host, port = target.split(":")
                port = int(port)

                logger.info("Client %s requested CONNECT to %s:%d", client_ip, host, port)

                remote_sock = socket.create_connection((host, port))
                connection.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                threading.Thread(target=self.relay_loop, args=(connection, remote_sock, client_ip)).start()
                threading.Thread(target=self.relay_loop, args=(remote_sock, connection, client_ip)).start()

            # http
            else: 
                host_header = [line for line in request.decode(errors="ignore").split("\r\n") if line.lower().startswith("host:")]
                if not host_header:
                    logger.warning("Client %s sent HTTP request without Host header", client_ip)
                    connection.close()
                    return
                
                host = host_header[0].split(":", 1)[1].strip()
                if ':' in host:
                    host, port = host.split(":")
                    port = int(port)
                else:
                    port = 80
                
                logger.info("Client %s requested HTTP to %s:%d", client_ip, host, port)

                remote_sock = socket.create_connection((host, port))
                remote_sock.sendall(request)

                threading.Thread(target=self.relay_loop, args=(connection, remote_sock, client_ip)).start()
                threading.Thread(target=self.relay_loop, args=(remote_sock, connection, client_ip)).start()

        except Exception as e:
            logger.error("Error handling client %s: %s", client_ip or "Unknown", e)
            connection.close()


    def relay_loop(self, source: socket.socket, destination: socket.socket, client_ip: str):
        logger.debug("Started relaying traffic for %s", client_ip)
        try:
            while True:
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


    def start(self, host = "0.0.0.0", port = 8080):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()

        logger.info("Http proxy Listening on %s:%d", host, port)

        while True:
            conn, addr = sock.accept()
            logger.info("Accepted connection from %s", addr)
            threading.Thread(target=self.handle_client, args=(conn,)).start()

if __name__ == "__main__":
    proxy = Proxy()
    proxy.start()