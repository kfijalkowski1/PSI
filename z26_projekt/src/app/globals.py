import threading

folder_state = {}

folder_state_lock = threading.Lock()

CLIENT_ID = ""

CONNECTIONS = {}
CONNECTIONS_LOCK = threading.Lock()

TCP_PORT = 8888
gui = False
