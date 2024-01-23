import os
import datetime
import logging
import globals


if not os.path.exists("logs"):
    os.mkdir("logs")

timestamp_str = datetime.datetime.today().strftime("%Y-%m-%d_%H-%M-%S-%f")
logging_path = os.path.join("logs", f"{timestamp_str}.log")

logging.basicConfig(filename=logging_path, format='%(asctime)s %(levelname)-8s %(message)s',
                    encoding='utf-8', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

if not globals.gui:
    # pipe with logs to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    console_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(console_formatter)

    logging.getLogger().addHandler(console_handler)


def debug(msg):
    logging.debug(msg)


def info(msg):
    logging.info(msg)


def success(msg):
    logging.info("[SUCCESS] " + msg)


def warning(msg):
    logging.warning(msg)


def error(msg):
    logging.error(msg)
