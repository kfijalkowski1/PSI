import os
import time
from data_parser import FileState, FileStatus
import globals
import data_parser
from utils import ExceptThread
import logger

FOLDER_SCANNER = None

class Scanner(ExceptThread):
    def __init__(self, folder_path):
        super().__init__(f"folder_scanner")

        self.folder_path = folder_path

    def main(self):
        logger.info(f"Starting folder scan for: {self.folder_path}")
        while True:
            self.scan()
            
            for connection in globals.CONNECTIONS.values():
                connection.transmit_queue.put(
                data_parser.FileList(globals.folder_state)
            )

            logger.info("scan completed waiting for next scan...")
            time.sleep(5)


    def scan(self):
        with globals.folder_state_lock:
            logger.info("Scanning folder...")

            current_files = set(os.listdir(self.folder_path))

            for file_name in current_files:
                file_path = os.path.join(self.folder_path, file)
                modification_timestamp = int(os.path.getmtime(file_path) * 1000)

                if file_name in globals.folder_state:
                    logger.warning(f'dir: {globals.folder_state[file_name].modification_timestamp}, time: {modification_timestamp}')
                    if (
                        globals.folder_state[file_name].modification_timestamp
                        < modification_timestamp
                    ):
                        logger.info(f"file updated: {file_name}")
                        globals.folder_state[file_name].update(
                            modification_timestamp, FileStatus.LATEST
                        )
                else:
                    logger.info(f"new file detected: {file_name}")
                    globals.folder_state[file_name] = FileState(
                        file_name, modification_timestamp, FileStatus.LATEST
                    )

            known_files = set(globals.folder_state.keys())
            removed_files = known_files - current_files
            for file_name in removed_files:
                current_timestamp = int(time.time() * 1000)
                logger.info(f"File removed: {file_name} in timestamp: {current_timestamp}")
                globals.folder_state[file_name].update(
                    current_timestamp, FileStatus.DELETED
                )

        logger.info("current state:")
        for file, state in globals.folder_state.items():
            logger.info(f"{file}: {state}")

def start(folder_path):
    global FOLDER_SCANNER
    FOLDER_SCANNER = Scanner(folder_path)
    FOLDER_SCANNER.run()
