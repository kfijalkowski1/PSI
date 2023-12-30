from classes import FileState
import threading

folder_state = {}

folder_state_lock = threading.Lock()

