import socket
import threading
import json
import logging
import datetime
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


def build_message(msg_type: str, data: str, room: str = "") -> bytes:
    payload = {
        "type":      msg_type,
        "room":      room,
        "data":      data,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
    }
    return (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")


def send_to(sock: socket.socket, msg_type: str, data: str, room: str = "") -> None:
    try:
        sock.sendall(build_message(msg_type, data, room))
    except (BrokenPipeError, OSError):
        pass


def broadcast(room_name: str, msg_type: str, data: str, exclude: str = "") -> None:
    with rooms_lock:
        members = set(rooms.get(room_name, []))

    with clients_lock:
        for username in members:
            if username == exclude:
                continue
            sock = clients.get(username)
            if sock:
                send_to(sock, msg_type, data, room_name)


def room_create(room_name: str) -> bool:
    with rooms_lock:
        if room_name in rooms:
            return False
        rooms[room_name] = set()
        log.info("Room created: %s", room_name)
        return True


def room_join(username: str, room_name: str, sock: socket.socket) -> bool:
    with rooms_lock:
        if room_name not in rooms:
            return False
        if len(rooms[room_name]) >= config.MAX_ROOM_USERS:
            send_to(sock, config.MSG_TYPE_ERROR, "Room is full.", room_name)
            return False
        rooms[room_name].add(username)

    send_to(sock, config.MSG_TYPE_SYSTEM, f"You joined '{room_name}'.", room_name)
    broadcast(room_name, config.MSG_TYPE_SYSTEM,
              f"{username} joined the room.", exclude=username)
    log.info("%s -> joined room %s", username, room_name)
    return True


def room_leave(username: str, room_name: str) -> None:
    with rooms_lock:
        rooms.get(room_name, set()).discard(username)
    broadcast(room_name, config.MSG_TYPE_SYSTEM, f"{username} left the room.")
    log.info("%s left room %s", username, room_name)


def get_room_of(username: str) -> str | None:
    with rooms_lock:
        for room_name, members in rooms.items():
            if username in members:
                return room_name
    return None


def handle_command(username: str, sock: socket.socket, command: str) -> None:
    parts = command.strip().split(maxsplit=1)
    cmd   = parts[0].lower()
    arg   = parts[1].strip() if len(parts) > 1 else ""

    if cmd == "/create":
        if not arg:
            send_to(sock, config.MSG_TYPE_ERROR, "Usage: /create <room_name>")
            return
        if room_create(arg):
            room_join(username, arg, sock)
        else:
            send_to(sock, config.MSG_TYPE_ERROR, f"Room '{arg}' already exists.")

    elif cmd == "/join":
        if not arg:
            send_to(sock, config.MSG_TYPE_ERROR, "Usage: /join <room_name>")
            return
        current = get_room_of(username)
        if current:
            room_leave(username, current)
        if not room_join(username, arg, sock):
            send_to(sock, config.MSG_TYPE_ERROR, f"Room '{arg}' not found.")

    elif cmd == "/invite":
        if not arg:
            send_to(sock, config.MSG_TYPE_ERROR, "Usage: /invite <username>")
            return
        current = get_room_of(username)
        if not current:
            send_to(sock, config.MSG_TYPE_ERROR, "You must be in a room first.")
            return
        with clients_lock:
            target_sock = clients.get(arg)
        if not target_sock:
            send_to(sock, config.MSG_TYPE_ERROR, f"User '{arg}' not found.")
            return
        send_to(target_sock, config.MSG_TYPE_SYSTEM,
                f"{username} invited you to '{current}'. To join: /join {current}")
        send_to(sock, config.MSG_TYPE_SYSTEM, f"Invite sent to {arg}.")

    elif cmd == "/list":
        with clients_lock:
            user_list = ", ".join(clients.keys()) or "(nobody connected)"
        send_to(sock, config.MSG_TYPE_SYSTEM, f"Connected users: {user_list}")

    elif cmd == "/rooms":
        with rooms_lock:
            room_list = ", ".join(
                f"{r}({len(m)})" for r, m in rooms.items()
            ) or "(no rooms)"
        send_to(sock, config.MSG_TYPE_SYSTEM, f"Rooms: {room_list}")

    else:
        send_to(sock, config.MSG_TYPE_ERROR, f"Unknown command: {cmd}")


def handle_client(sock: socket.socket, addr: tuple) -> None:
    log.info("New connection: %s", addr)
    username = None

    try:
        send_to(sock, config.MSG_TYPE_SYSTEM, "Enter your username:")
        raw = sock.recv(config.BUFFER_SIZE).decode("utf-8").strip()
        username = raw[:20]

        with clients_lock:
            if username in clients:
                send_to(sock, config.MSG_TYPE_ERROR, "Username already taken.")
                return
            clients[username] = sock

        log.info("User registered: %s (%s)", username, addr)
        send_to(sock, config.MSG_TYPE_SYSTEM,
                f"Welcome, {username}! Default room: '{config.DEFAULT_ROOM}'")

        room_join(username, config.DEFAULT_ROOM, sock)

        buffer = ""
        while True:
            chunk = sock.recv(config.BUFFER_SIZE).decode("utf-8")
            if not chunk:
                break
            buffer += chunk

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    send_to(sock, config.MSG_TYPE_ERROR, "Invalid JSON format.")
                    continue

                msg_type = msg.get("type", "")
                data     = msg.get("data", "").strip()

                if msg_type == config.MSG_TYPE_COMMAND:
                    handle_command(username, sock, data)

                elif msg_type == config.MSG_TYPE_CHAT:
                    room = get_room_of(username)
                    if room:
                        broadcast(room, config.MSG_TYPE_CHAT,
                                  f"{username}: {data}", exclude=username)
                        log.debug("[%s] %s: %s", room, username, data)
                    else:
                        send_to(sock, config.MSG_TYPE_ERROR, "Join a room first: /join <room>")

    except (ConnectionResetError, OSError) as exc:
        log.warning("Connection error (%s): %s", addr, exc)

    finally:
        if username:
            room = get_room_of(username)
            if room:
                room_leave(username, room)
            with clients_lock:
                clients.pop(username, None)
            log.info("User disconnected: %s", username)
        sock.close()


def start_server() -> None:
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
