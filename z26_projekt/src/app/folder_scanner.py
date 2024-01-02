import os
import time
from classes import FileState, FileStatus
import globals
import data_parser
from utils import ExceptThread


class Scanner(ExceptThread):
    def __init__(self, folder_path):
        super().__init__(f"folder_scanner")

        self.folder_path = folder_path

    def main(self):
        print(f"Starting folder scan for: {self.folder_path}")

        while True:
            with globals.folder_state_lock:
                print("Scanning folder...")
                # files_to_delete = [file for file in globals.folder_state if globals.folder_state[file].status == "usuniety"]

                # for file in files_to_delete:
                #    del globals.folder_state[file]

                current_timestamp = int(time.time() * 1000)

                current_files = set(os.listdir(self.folder_path))

                for file in current_files:
                    file_path = os.path.join(self.folder_path, file)
                    modification_timestamp = int(os.path.getmtime(file_path) * 1000)

                    if file in globals.folder_state:
                        if (
                            globals.folder_state[file].modification_timestamp
                            != modification_timestamp
                        ):
                            print(f"file updated: {file}")
                            globals.folder_state[file].update(
                                modification_timestamp, FileStatus.LATEST
                            )
                    else:
                        print(f"new file detected: {file}")
                        globals.folder_state[file] = FileState(
                            file, modification_timestamp, FileStatus.LATEST
                        )

                known_files = set(globals.folder_state.keys())
                removed_files = known_files - current_files
                for file in removed_files:
                    print(f"File removed: {file} in timestamp: {current_timestamp}")
                    globals.folder_state[file].update(
                        current_timestamp, FileStatus.DELETED
                    )

            print("current state:")
            for file, state in globals.folder_state.items():
                print(f"{file}: {state}")

            for connection in globals.CONNECTIONS.values():
                connection.transmit_queue.put(
                    data_parser.FileList(globals.folder_state)
                )

            print("scan completed waiting for next scan...")
            time.sleep(5)


def start():
    Scanner("./test").run()
