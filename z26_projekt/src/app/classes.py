import queue
import socket
import struct
from enum import Enum

import globals
import logger


class FileStatus(Enum):
    LATEST = 0
    DELETED = 1
    PENDING = 2


class FileState:
    def __init__(self, name, modification_timestamp, status=FileStatus.LATEST):
        self.name = name
        self.modification_timestamp = modification_timestamp
        self.status = status

    def update(self, modification_timestamp, status=None):
        if modification_timestamp:
            self.modification_timestamp = modification_timestamp
        if status:
            self.status = status

    def serialize(self) -> bytes:
        return struct.pack(
            "BL", self.status.value, self.modification_timestamp
        ) + self.name.encode("utf8")

    def deserialize(stream: bytes):
        name_size = len(stream) - struct.calcsize("BL")
        rec_type, time, name = struct.unpack(f"BL{name_size}s", stream)

        return FileState(name.decode("utf8"), time, rec_type)

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
