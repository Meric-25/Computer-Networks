import socket
import threading
import json
import sys
import config


def receive_loop(sock: socket.socket) -> None:
    buffer = ""
    try:
        while True:
            chunk = sock.recv(config.BUFFER_SIZE).decode("utf-8")
            if not chunk:
                print("\n[!] Server closed the connection.")
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
                    print(f"[?] Unreadable message: {line}")
                    continue

                format_and_print(msg)

    except (ConnectionResetError, OSError):
        print("\n[!] Connection to server lost.")
    finally:
        sock.close()
        sys.exit(0)



def format_and_print(msg: dict) -> None:
    msg_type  = msg.get("type", "")
    data      = msg.get("data", "")
    room      = msg.get("room", "")
    timestamp = msg.get("timestamp", "")

    room_prefix = f"[{room}] " if room else ""

    if msg_type == config.MSG_TYPE_CHAT:
        print(f"\r{room_prefix}{data}  ({timestamp})")
    elif msg_type == config.MSG_TYPE_SYSTEM:
        print(f"\r*** {data}")
    elif msg_type == config.MSG_TYPE_ERROR:
        print(f"\r[ERROR] {data}")
    else:
        print(f"\r[{msg_type}] {data}")

    print("> ", end="", flush=True)



def send_message(sock: socket.socket, text: str) -> None:
    if text.startswith("/"):
        payload = {
            "type": config.MSG_TYPE_COMMAND,
            "data": text,
        }
    else:
        payload = {
            "type": config.MSG_TYPE_CHAT,
            "data": text,
        }
    try:
        sock.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    except OSError as exc:
        print(f"[!] Could not send: {exc}")



def register_username(sock: socket.socket) -> None:
    username = input("Username: ").strip()
    if not username:
        print("[!] Username cannot be empty.")
        sys.exit(1)
    sock.sendall((username + "\n").encode("utf-8"))



def start_client(host: str = config.SERVER_HOST, port: int = config.SERVER_PORT) -> None:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"[!] Could not connect to server: {host}:{port}")
        sys.exit(1)

    print(f"Connected to server: {host}:{port}")
    print("Commands: /create <room>, /join <room>, /invite <user>, /list, /rooms, /quit\n")

    register_username(sock)

    recv_thread = threading.Thread(target=receive_loop, args=(sock,), daemon=True)
    recv_thread.start()


    try:
        while True:
            text = input("> ").strip()
            if not text:
                continue
            if text.lower() == "/quit":
                print("Closing connection...")
                break
            send_message(sock, text)
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
    finally:
        sock.close()


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else config.SERVER_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else config.SERVER_PORT
    start_client(host, port)
