from rich.layout import Layout
from time import sleep
from rich.live import Live
from rich.panel import Panel
import globals
from logger import logging_path


def get_log_color(line):
    log_colors = {
        "SUCCESS": "green",
        "INFO": "white",
        "DEBUG": "blue",
        "WARNING": "yellow",
        "ERROR": "red"
    }
    for key, val in log_colors.items():
        if key in line:
            return val
    return "white"


def get_logs():
    result = ""

    with open(logging_path, 'r') as file:
        file_size = file.tell()
        last_ten_lines = file.readlines()[(file_size - 10):]
        for line in last_ten_lines:
            color = get_log_color(line)
            result += f"[{color}]{line}"

    return result


def get_file_states():
    result = ""
    for key, val in globals.folder_state.items():
        result += str(key) + "\n\t" + str(val) + "\n"
    return result


def get_connections():
    result = ""
    for key, val in globals.CONNECTIONS.items():
        address = val.address
        port = val.port
        result += f"client: {key}\n\taddress: {address}\n\tport: {port}"
    return result


def generate_layout():
    layout = Layout()

    layout.split_column(
        Layout(name="upper"),
        Layout(name="lower")
    )

    layout["lower"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )
    layout["upper"].update(
        Panel(get_logs(), title="Logs")
    )
    layout["left"].update(
        Panel(get_file_states(), title="Files state")
    )
    layout["right"].update(
        Panel(get_connections(), title="Connections")
    )
    return layout


def run_gui():
    with Live(generate_layout(), refresh_per_second=4) as live:
        while True:
            live.update(generate_layout())
            sleep(0.25)
