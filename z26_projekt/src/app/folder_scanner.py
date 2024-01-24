import os
import time
from data_parser import FileState, FileStatus
import globals
import data_parser
from utils import ExceptThread
import logger


class Scanner(ExceptThread):
    def __init__(self, folder_path):
        super().__init__(f"folder_scanner")

        self.folder_path = folder_path

    def main(self):
        logger.info(f"Starting folder scan for: {self.folder_path}")

        while True:
            with globals.folder_state_lock:
                logger.info("Scanning folder...")

                current_timestamp = int(time.time() * 1000)

                current_files = set(os.listdir(self.folder_path))

                for file in current_files:
                    file_path = os.path.join(self.folder_path, file)
                    modification_timestamp = int(os.path.getmtime(file_path) * 1000)

                    if file in globals.folder_state:
                        logger.warning(f'dir: {globals.folder_state[file].modification_timestamp}, time: {modification_timestamp}')
                        if (
                            globals.folder_state[file].modification_timestamp
                            != modification_timestamp
                        ):
                            logger.info(f"file updated: {file}")
                            globals.folder_state[file].update(
                                modification_timestamp, FileStatus.LATEST
                            )
                    else:
                        logger.info(f"new file detected: {file}")
                        globals.folder_state[file] = FileState(
                            file_path, modification_timestamp, FileStatus.LATEST
                        )

                known_files = set(globals.folder_state.keys())
                removed_files = known_files - current_files
                for file in removed_files:
                    logger.info(f"File removed: {file} in timestamp: {current_timestamp}")
                    globals.folder_state[file].update(
                        current_timestamp, FileStatus.DELETED
                    )

            logger.info("current state:")
            for file, state in globals.folder_state.items():
                logger.info(f"{file}: {state}")

            for connection in globals.CONNECTIONS.values():
                connection.transmit_queue.put(
                    data_parser.FileList(globals.folder_state)
                )

            logger.info("scan completed waiting for next scan...")
            time.sleep(5)


def start(folder_path):
    Scanner(folder_path).run()
