import queue
import socket

import globals
import logger
import data_parser


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

        self.transmit_queue.put(data_parser.CloseConnection())
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        logger.success(f"Closed connection with {self.client_id}")

        del globals.CONNECTIONS[self.client_id]

    def __del__(self):
        self.socket.close()

    def __repr__(self):
        return f"ConnectionState(client_id='{self.client_id}', address={self.address}, port={self.port})"

    def __str__(self):
        return f"client_id='{self.client_id}', address={self.address}, port={self.port}"
