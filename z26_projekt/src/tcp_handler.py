import globals
import logger


def start(address, port, client_id):
    logger.info(
        f"Connecting to client {client_id} on address {address} using port {port}"
    )
    globals.CONNECTIONS[client_id] = {
        "address": address,
        "port": port,
        "status": "pending",
    }
