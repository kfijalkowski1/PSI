import threading
from datetime import datetime

class FileState:
    def __init__(self, name, modification_timestamp=None, status='aktualny'):
        self.name = name
        self.modification_timestamp = modification_timestamp if modification_timestamp is not None else time.time()
        self.status = status

    def update(self, modification_timestamp=None, status=None):
        if modification_timestamp:
            self.modification_timestamp = modification_timestamp
        if status:
            self.status = status

    def __repr__(self):
        return f"FileState(name='{self.name}', modification_timestamp='{self.modification_timestamp}', status='{self.status}')"

