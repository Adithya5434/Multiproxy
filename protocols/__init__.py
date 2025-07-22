import socket
import logging

from utils import detect_protocol
import config

from . import socks5
from . import socks4
from . import minecraft_proxy
from . import http_proxy

socks5_proxy = socks5.Proxy(config.SOCKS5_USERNAME, config.SOCKS5_PASSWORD)
socks4_proxy = socks4.Proxy(config.SOCKS4_USERNAME)
mc_proxy = minecraft_proxy.Proxy(config.MC_SERVER_IP, config.MC_SERVER_PORT)
httpProxy = http_proxy.Proxy()

logger = logging.getLogger(__name__)

def route_connection(connection: socket.socket, addr, DEBUG=False):
    try:
        data = connection.recv(1024, socket.MSG_PEEK)

        if not data:
            logger.warning(f"No data received from {addr}")
            connection.close()
            return

        protocol = detect_protocol(data)
        logger.debug(f"Detected protocol: {protocol} from {addr}, first few bytes: {data[0:100]}")

        if protocol == "socks5":
            socks5_proxy.handle_client(connection)
            return

        elif protocol == "socks4":
            socks4_proxy.handle_client(connection)
            return

        elif protocol == "http_proxy":
            httpProxy.handle_client(connection)
            return

        elif protocol == "minecraft":
            mc_proxy.handle_client(connection)
            return
        
        else:
            logger.warning(f"Unknown protocol from {addr}, first byte: {data[0]}")
            connection.close()

    except Exception as e:
        logger.error(f"Router error from {addr}: {e}")
        connection.close()