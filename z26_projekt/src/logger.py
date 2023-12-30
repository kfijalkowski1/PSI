BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
GRAY = "\033[37m"
CLEAR = "\033[0m"


def debug(msg):
    print(f"{GRAY}[ DEBUG ]", msg, CLEAR)


def info(msg):
    print(f"{CYAN}[  INFO ]", msg, CLEAR)


def warning(msg):
    print(f"{YELLOW}[WARNING]", msg, CLEAR)


def error(msg):
    print(f"{BOLD}{RED}[ ERROR ]", msg, CLEAR)
