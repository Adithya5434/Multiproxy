import socket
import threading

import protocols
import config

def main(host = "0.0.0.0", port = 1080):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    sock.settimeout(1)

    print(f"Listening on {host}:{port}")

    try:
        while True:
            try:
                conn, addr = sock.accept()
                print(f"Connection from {addr}")
                threading.Thread(target=protocols.route_connection, args=(conn, addr, True)).start()
            except socket.timeout:
                continue 
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down proxy server.")
    finally:
        sock.close()


if __name__ == "__main__":
    main(config.LISTEN_IP, config.LISTEN_PORT)