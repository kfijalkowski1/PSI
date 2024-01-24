import threading
import uuid

import tcp_server
import udp_server
import folder_scanner
import logger
import globals
import argparse
import os

from gui import run_gui


def parse_arguments():
    parser = argparse.ArgumentParser(description="Script running client to client file server")
    parser.add_argument("--gui", action="store_true", help="Flag to enable GUI")
    parser.add_argument("folder_path", help="Path to the folder with observed files")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    globals.CLIENT_ID = uuid.uuid4()
    globals.gui = True if args.gui else False

    if globals.gui:
        logger.info("GUI starting")
        gui_thread = threading.Thread(target=run_gui)
        gui_thread.start()
    logger.set_logger()

    logger.info(f"Client id is: {globals.CLIENT_ID.hex}")

    tcp_server.start()
    udp_server.start()

    if not os.path.exists(args.folder_path):
        os.mkdir(args.folder_path)

    folder_scanner.start(args.folder_path)

    logger.info("All services started")



    threading.Event().wait()

