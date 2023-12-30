BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[36m"
CYAN = "\033[96m"
GRAY = "\033[37m"
CLEAR = "\033[0m"

import inspect
import os


def display(color, text, msg):
    stack_frame = inspect.stack()[2]
    filename = os.path.splitext(os.path.basename(stack_frame.filename))[0]
    line_number = stack_frame.lineno
    print(f"{color}{text}", f"{BLUE}{filename}:{line_number}{color}", msg, CLEAR)


def debug(msg):
    display(GRAY, "[ DEBUG ]", msg)


def info(msg):
    display(CYAN, "[  INFO ]", msg)


def warning(msg):
    display(YELLOW, "[WARNING]", msg)


def error(msg):
    display(f"{BOLD}{RED}", "[ ERROR ]", msg)
