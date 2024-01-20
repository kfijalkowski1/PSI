import socket
import time

import logger
import config
import globals
import tcp_handler
import data_parser
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

        data = data_parser.UDPDiscovery(globals.CLIENT_ID, globals.TCP_PORT).serialize()

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

                discovery_packet = data_parser.UDPDiscovery.deserialize(data)

                if discovery_packet.client_id == globals.CLIENT_ID:
                    continue

                if not data:
                    logger.warning("Invalid datagram recieved")
                    continue

                with globals.CONNECTIONS_LOCK:
                    if discovery_packet.client_id not in globals.CONNECTIONS.keys():
                        logger.info(f"Detected new client {discovery_packet.client_id}")
                        tcp_handler.start(
                            address,
                            discovery_packet.tcp_port,
                            discovery_packet.client_id,
                        )


def start():
    Broadcaster().start()
    Server().start()
