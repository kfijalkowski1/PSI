import socket

import logger
from utils import ExceptThread
import globals
import tcp_handler


class Server(ExceptThread):
    def __init__(self, sock):
        super().__init__("tcp_server")
        self.socket = sock

    def main(self):
        s = self.socket

        s.listen()

        logger.info(f"TCP server started on port {globals.TCP_PORT}")
        while True:
            (client_socket, (ip, port)) = s.accept()

            with globals.CONNECTIONS_LOCK:
                logger.info(f"Accepting connection from new client...")
                tcp_handler.accept(client_socket, ip, port)


def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    globals.TCP_PORT = s.getsockname()[1]

    Server(s).start()
