from classes import FileState
import threading

folder_state = {}

folder_state_lock = threading.Lock()

CLIENT_ID = ""

CONNECTIONS = {}
CONNECTIONS_LOCK = threading.Lock()
