import threading
import uuid

import tcp_server
import udp_server
import logger
import globals

if __name__ == "__main__":
    globals.CLIENT_ID = uuid.uuid4()

    logger.info(f"Client id is: {globals.CLIENT_ID.hex}")

    tcp_server.start()
    udp_server.start()

    logger.info("All services started")

    threading.Event().wait()
