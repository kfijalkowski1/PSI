import socket
import time
import struct
import uuid

import globals
import logger
from utils import ExceptThread


class Handler(ExceptThread):
    def __init__(self, sock, address, port, client_id):
        super().__init__(f"tcp_handler{address}_{port}")

        self.sock = sock
        self.address = address
        self.port = port
        self.client_id = client_id

    def main(self):
        logger.info(f"Connection established with client {self.client_id}!")
        s = self.sock
        while True:
            s.sendall(b"Hello, world!")
            data = s.recv(1024)
            logger.info("Recieved " + str(data))

            time.sleep(5)


def accept(sock: socket.socket, address, port):
    # send welcome message
    # TODO use data_parser
    logger.debug("Sending welcome message...")
    data = struct.pack("16s", globals.CLIENT_ID.bytes)
    sock.sendall(data)

    logger.debug("Recieving welcome message...")
    data = sock.recv(1024)
    (client_id,) = struct.unpack("16s", data)
    client_id = uuid.UUID(bytes=client_id)

    globals.CONNECTIONS[client_id] = {
        "address": address,
        "port": port,
    }

    Handler(sock, address, port, client_id).start()


def start(address, port, client_id):
    logger.info(
        f"Connecting to client {client_id} on address {address} using port {port}"
    )

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    accept(s, address, port)
