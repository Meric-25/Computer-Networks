# B205 Computer Networks – Messaging Application

## Project Overview

This project is a simple real-time messaging application developed for the B205 Computer Networks group final project. The application demonstrates socket programming, client-server communication, chat room management, and a JSON-based messaging protocol.

The system allows multiple users to connect to a central server, join chat rooms, create new rooms, invite other users, and exchange messages in real time.

## Team Members

* Ilayda Ray
* Meric Olcan Polat

## Main Features

* Client-server architecture
* TCP socket communication
* Real-time text messaging
* Support for at least three users
* Unique username registration
* Default chat room called `general`
* Ability to create new chat rooms
* Ability to join existing chat rooms
* Ability to invite other users to a room
* JSON-based message format
* Basic error handling and logging
* Console-based user interface

## Project Files

```text
server.py     # Server-side logic and room management
client.py     # Client-side console interface
config.py     # Configuration values such as host, port, and message types
README.md     # Project documentation
```

## Requirements

The project requires Python 3.

No advanced external libraries are required. The application uses standard Python modules:

```text
socket
threading
json
logging
datetime
sys
```

## How to Run the Application

### 1. Start the Server

Open a terminal in the project folder and run:

```bash
python server.py
```

The server starts listening on:

```text
127.0.0.1:9090
```

### 2. Start the Clients

Open a new terminal window for each client and run:

```bash
python client.py
```

To test the application properly, start at least three client instances.

Each client will be asked to enter a username:

```text
Username: Ilayda
```

Each username must be unique.

## Available Commands

| Command            | Description                              |
| ------------------ | ---------------------------------------- |
| `/create roomname` | Creates a new chat room and joins it     |
| `/join roomname`   | Joins an existing chat room              |
| `/invite username` | Invites another user to the current room |
| `/list`            | Displays all connected users             |
| `/rooms`           | Displays all available rooms             |
| `/quit`            | Disconnects from the server              |

## Example Usage

Example client session:

```text
Username: Ilayda

/create study
Hello everyone
/invite Meric
/rooms
/list
```

In this example, the user creates a room called `study`, sends a message, invites another user, checks the available rooms, and lists connected users.

## Communication Protocol

The application uses a JSON-based protocol over TCP sockets.

Example chat message:

```json
{
  "type": "chat",
  "room": "general",
  "data": "Hello everyone",
  "timestamp": "14:30:25"
}
```

Example command message:

```json
{
  "type": "command",
  "data": "/join study"
}
```

## Message Types

| Type      | Purpose                    |
| --------- | -------------------------- |
| `chat`    | Regular user chat messages |
| `command` | Commands sent by clients   |
| `system`  | Server notifications       |
| `error`   | Error messages             |

## Architecture

The application follows a client-server architecture. The server manages all connected clients, chat rooms, and message broadcasting. Each client connects to the server using a TCP socket.

The server uses a separate thread for each connected client, allowing multiple users to communicate at the same time.

## Testing

The application was tested by running one server instance and three client instances. The following functions were tested:

* Connecting multiple users
* Registering unique usernames
* Sending and receiving messages
* Creating new rooms
* Joining existing rooms
* Inviting users
* Listing connected users
* Listing available rooms
* Disconnecting from the server

## Notes

This project was developed as part of the B205 Computer Networks group final project at GISMA University of Applied Sciences.
