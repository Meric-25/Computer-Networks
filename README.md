# B205 Computer Networks – Messaging Application

## Project Overview

This project is a simple real-time messaging application developed for the B205 Computer Networks group final project. It uses TCP socket programming, a client-server architecture, chat rooms, and a JSON-based message format.

## Team Members

* Ilayda Ray
* Meric Olcan Polat

## Features

* Client-server architecture
* TCP socket communication
* Real-time messaging
* Support for multiple users
* Unique usernames
* Chat room creation and joining
* User invitation
* JSON-based message format
* Console-based interface
* Basic error handling and logging

## Project Files

```text
server.py   - Server-side logic, client handling, and room management
client.py   - Client-side console interface
config.py   - Configuration values such as host, port, and message types
README.md   - Project documentation
```

## Requirements

Python 3 is required.

The application uses only standard Python libraries:

```text
socket
threading
json
logging
datetime
sys
```

## How to Run

### 1. Start the server

```bash
python server.py
```

The server listens on:

```text
127.0.0.1:9090
```

### 2. Start the clients

Open a new terminal for each client and run:

```bash
python client.py
```

Enter a unique username when asked. For testing, run at least three clients.

## Available Commands

| Command            | Description                        |
| ------------------ | ---------------------------------- |
| `/create roomname` | Creates a new chat room            |
| `/join roomname`   | Joins an existing room             |
| `/invite username` | Invites a user to the current room |
| `/list`            | Lists connected users              |
| `/rooms`           | Lists available rooms              |
| `/quit`            | Disconnects from the server        |

## Example Usage

```text
Username: Ilayda

/create study
Hello everyone
/invite Meric
/rooms
/list
```

## Communication Protocol

The application uses JSON messages over TCP sockets.

Example message:

```json
{
  "type": "chat",
  "room": "general",
  "data": "Hello everyone",
  "timestamp": "14:30:25"
}
```

## Testing

The application was tested with one server and at least three client instances. The main functions tested were user connection, room creation, room joining, message sending, user invitation, and disconnection.

## Notes

This project was developed as part of the B205 Computer Networks group final project at GISMA University of Applied Sciences.
