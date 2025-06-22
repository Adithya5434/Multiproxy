import socket
import threading

from utils import detect_protocol
import config

import socks5
import socks4

socks5_proxy = socks5.Proxy(config.SOCKS5_USERNAME, config.SOCKS5_PASSWORD)
socks4_proxy = socks4.Proxy(config.SOCKS4_USERNAME)


def route_connection(connection: socket.socket, addr):
    try:
        data = connection.recv(1024, socket.MSG_PEEK)

        if not data:
            print(f"[X] No data form {addr}")
            connection.close()
            return

        protocol = detect_protocol(data)

        if protocol == "socks5":
            threading.Thread(target=socks5_proxy.handle_client, args=(connection,)).start()
            return

        elif protocol == "socks4":
            threading.Thread(target=socks4_proxy.handle_client, args=(connection,)).start()
            return

        elif protocol == "http_proxy":
            pass

        elif protocol == "http_web":
            pass

        elif protocol == "minecraft":
            pass

        else:
            print(f"[x] Unknown protocol from {addr}, first byte: {data[0]}")
            connection.close()

    except Exception as e:
        print(f"[!] Router error form {addr}: ", e)
        connection.close()