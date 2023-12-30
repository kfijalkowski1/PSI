import threading
from datetime import datetime
import queue
import time
import socket

import globals
import logger


class FileState:
    def __init__(self, name, modification_timestamp=None, status="aktualny"):
        self.name = name
        self.modification_timestamp = (
            modification_timestamp
            if modification_timestamp is not None
            else time.time()
        )
        self.status = status

    def update(self, modification_timestamp=None, status=None):
        if modification_timestamp:
            self.modification_timestamp = modification_timestamp
        if status:
            self.status = status

    def __repr__(self):
        return f"FileState(name='{self.name}', modification_timestamp='{self.modification_timestamp}', status='{self.status}')"


class ConnectionState:
    def __init__(self, sock: socket.socket, address, port, client_id):
        self.socket = sock
        self.address = address
        self.port = port
        self.client_id = client_id
        self.transmit_queue = queue.Queue()

        self.open = True

    def close(self):
        if self.open is False:
            return

        self.open = False

        # TODO: use dedicated class when data_parser is ready
        self.transmit_queue.put(b"close")
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        logger.success(f"Closed connection with {self.client_id}")

        del globals.CONNECTIONS[self.client_id]

    def __del__(self):
        self.socket.close()

    def __repr__(self):
        return f"ConnectionState(client_id='{self.client_id}', address={self.address}, port={self.port})"
