import socket
import threading
import json
import logging
import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.DEBUG),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("server")


clients_lock = threading.Lock()
rooms_lock   = threading.Lock()

clients: dict[str, socket.socket] = {}

rooms: dict[str, set[str]] = {
    config.DEFAULT_ROOM: set()
}


def handle_client(sock: socket.socket, addr: tuple) -> None:
    log.info("New connection: %s", addr)
    username = None

    try:
        sock.sendall(("Enter your username:\n").encode("utf-8"))
        raw = sock.recv(config.BUFFER_SIZE).decode("utf-8").strip()
        username = raw[:20]

        with clients_lock:
            if username in clients:
                sock.sendall(("Username already taken.\n").encode("utf-8"))
                return
            clients[username] = sock

        log.info("User registered: %s (%s)", username, addr)
        sock.sendall((f"Welcome, {username}!\n").encode("utf-8"))

        while True:
            data = sock.recv(config.BUFFER_SIZE).decode("utf-8")
            if not data:
                break

    except (ConnectionResetError, OSError) as exc:
        log.warning("Connection error (%s): %s", addr, exc)

    finally:
        if username:
            with clients_lock:
                clients.pop(username, None)
            log.info("User disconnected: %s", username)
        sock.close()


def start_server() -> None:
    """
    Opens the TCP socket, accepts connections, and starts a thread for each one.
    """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((config.SERVER_HOST, config.SERVER_PORT))
    srv.listen()
    log.info("Server started: %s:%s", config.SERVER_HOST, config.SERVER_PORT)
    log.info("Waiting for connections...")

    try:
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
            log.debug("Thread started: %s", addr)
    except KeyboardInterrupt:
        log.info("Server shutting down (Ctrl+C).")
    finally:
        srv.close()


if __name__ == "__main__":
    start_server()
