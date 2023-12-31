import os
import time
from classes import FileState
import globals

def scan_folder(folder_path):
    print(f"Starting folder scan for: {folder_path}")

    while True:

        with globals.folder_state_lock:
            print("Scanning folder...")
            #files_to_delete = [file for file in globals.folder_state if globals.folder_state[file].status == "usuniety"]

            #for file in files_to_delete:
            #    del globals.folder_state[file]

            current_timestamp = time.time()

            current_files = set(os.listdir(folder_path))


            for file in current_files:
                file_path = os.path.join(folder_path, file)
                modification_timestamp = os.path.getmtime(file_path)

                if file in globals.folder_state:
                    if globals.folder_state[file].modification_timestamp != modification_timestamp:

                        print(f"file updated: {file}")
                        globals.folder_state[file].update(modification_timestamp, 'aktualny')
                else:
                    print(f"new file detected: {file}")
                    globals.folder_state[file] = FileState(file, modification_timestamp, 'aktualny')


            known_files = set(globals.folder_state.keys())
            removed_files = known_files - current_files
            for file in removed_files:
                print(f"File removed: {file} in timestamp: {current_timestamp}")
                globals.folder_state[file].update(current_timestamp, 'usuniety')

        print("current state:")
        for file, state in globals.folder_state.items():
            print(f"{file}: {state}")

        print("scan completed waiting for next scan...")
        time.sleep(30)

if __name__ == "__main__":
    scan_folder('/home/users/mbienko2/projekt/psi/z26_projekt/src/app')  # Replace with your folder path
