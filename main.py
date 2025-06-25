import socket
import threading
import logging

import protocols
import config


if config.ENABLE_LOGGING:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(filename)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
else:
    logging.disable(logging.CRITICAL)
    

def main(host = "0.0.0.0", port = 1080):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    sock.settimeout(1)

    logging.info(f"Server Listening on {host}:{port}")

    try:
        while True:
            try:
                conn, addr = sock.accept()
                logging.debug(f"Accepted connection from {addr}")
                threading.Thread(target=protocols.route_connection, args=(conn, addr, True)).start()
                logging.debug(f"Routed connection from {addr}")
            except socket.timeout:
                continue 
    except KeyboardInterrupt:
        logging.info("Shutting down proxy server.")
    finally:
        logging.debug("Closing server socket")
        sock.close()


if __name__ == "__main__":
    logging.debug("starting server...")
    main(config.LISTEN_IP, config.LISTEN_PORT)