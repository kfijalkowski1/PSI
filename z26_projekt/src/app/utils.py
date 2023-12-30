import threading
import traceback

import logger


class ExceptThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.daemon = True
        self.thread_name = name

    def run(self):
        try:
            self.main()
        except Exception:
            logger.error(
                f"Thread {self.thread_name} crashed!\n" + traceback.format_exc()
            )
            pass

    def main():
        pass
