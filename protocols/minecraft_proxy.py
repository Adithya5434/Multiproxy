import socket
import select
import threading
import logging

import utils

logger = logging.getLogger(__name__)

class Proxy:
    def __init__(self, mc_host = "localhost", mc_port = 25565):
        self.mc_port = mc_port
        self.mc_host = mc_host

    def handle_client(self, connection: socket.socket):
        client_ip = None
        try:
            client_ip = connection.getpeername()[0]

            # BYPASS TCPshield plugin
            # how TCPshield plugin works:
            # It checks its server ip in initial handshake (0x00 packet) from client
            # and if it doesn't match with the real server ip, it closes the connection.
            # So we need to send the real server ip and port in the initial handshake packet to bypass it.

            # Read initial packet
            raw_packet = b""
            while True:
                part = connection.recv(1024)
                if not part:
                    return
                raw_packet += part
                try:
                    packet_length, header_len = utils.read_varint(raw_packet, 0)
                    total_needed = header_len + packet_length
                    if len(raw_packet) >= total_needed:
                        break
                except ValueError:
                    continue

            # Parse handshake
            packet_id, i = utils.read_varint(raw_packet, header_len)
            if packet_id != 0:
                logger.warning(f"Unexpected packet ID {packet_id}, expected 0x00 handshake")
                return

            protocol_version, i = utils.read_varint(raw_packet, i)
            server_address_length, i = utils.read_varint(raw_packet, i)
            server_address = raw_packet[i:i + server_address_length].decode()
            i += server_address_length
            server_port = int.from_bytes(raw_packet[i:i + 2], 'big')
            i += 2
            intent, i = utils.read_varint(raw_packet, i)

            logger.info(f"[{client_ip}] Intent: {intent}, Protocol: {protocol_version}, Address: {server_address}:{server_port}")

            # construct handshake packet with real host and port
            handshake_payload = (
                utils.write_varint(0) +
                utils.write_varint(protocol_version) +
                utils.write_varint(len(self.mc_host)) +
                self.mc_host.encode() +
                self.mc_port.to_bytes(2, "big") +
                utils.write_varint(intent)
            )
            handshake_packet = utils.write_varint(len(handshake_payload)) + handshake_payload

            remote_socket = socket.create_connection((self.mc_host, self.mc_port))
            remote_socket.sendall(handshake_packet)

            # Forward leftover packet data (e.g., Login Start or Status Request)
            leftover = raw_packet[header_len + packet_length:]
            if leftover:
                remote_socket.sendall(leftover)

            self.relay_loop(remote_socket, connection, client_ip)

        except Exception as e:
            logger.error(f"Error handling client {client_ip or 'Unknown'}: {e}")
            try:
                connection.close()
            except:
                pass

    def relay_loop(self, source: socket.socket, destination: socket.socket, client_ip: str):
        logger.info("Relaying connection from %s to %s:%d", client_ip, self.mc_host, self.mc_port)
        try:
            while True:
                readable, _, _ = select.select([source, destination], [], [])

                if source in readable:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.sendall(data)

                if destination in readable:
                    data = destination.recv(4096)
                    if not data:
                        break
                    source.sendall(data)
        except Exception as e:
            logger.warning("Relay error with %s: %s", client_ip, e)
        finally:
            try: source.close()
            except: pass
            try: destination.close()
            except: pass
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