import socket
import time
import struct
import uuid

import logger
import config
import globals
import tcp_handler
from utils import ExceptThread


class Broadcaster(ExceptThread):
    def __init__(self):
        super().__init__("udp_broadcaster")

    def main(self):
        interfaces = socket.getaddrinfo(
            host=socket.gethostname(), port=None, family=socket.AF_INET
        )
        addresses = [interface[-1][0] for interface in interfaces]
        addresses = list(set(addresses))

        # TODO use data_parser
        data = struct.pack("16sH", globals.CLIENT_ID.bytes, globals.TCP_PORT)

        logger.success("UDP broadcaster started")
        while True:
            for ip in addresses:
                logger.debug(f"Broadcasting on {ip}")
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    s.bind((ip, 0))
                    s.sendto(data, ("255.255.255.255", config.UDP_PORT))

            time.sleep(10)


class Server(ExceptThread):
    def __init__(self):
        super().__init__("udp_server")

    def main(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", config.UDP_PORT))

            logger.success("UDP server started")
            while True:
                (data, (address, port)) = s.recvfrom(1024)

                # TODO use data_parser
                client_id_raw, port = struct.unpack("16sH", data)
                client_id = uuid.UUID(bytes=client_id_raw)

                if client_id == globals.CLIENT_ID:
                    continue

                if not data:
                    logger.warning("Invalid datagram recieved")
                    continue

                with globals.CONNECTIONS_LOCK:
                    if client_id not in globals.CONNECTIONS.keys():
                        logger.info(f"Detected new client {client_id}")
                        tcp_handler.start(address, port, client_id)


def start():
    Broadcaster().start()
    Server().start()
