import os
import socket
import struct

import globals
import logger
from utils import ExceptThread
from classes import ConnectionState
import data_parser
import folder_scanner


class Sender(ExceptThread):
    def __init__(self, connection):
        super().__init__(f"tcp_sender{connection.client_id}")

        self.conn = connection

    def main(self):
        s = self.conn.socket
        queue = self.conn.transmit_queue
        try:
            while True:
                message = queue.get()
                if isinstance(message, data_parser.CloseConnection):
                    logger.debug(f"Sender disconnecting from {self.conn.client_id}")
                    return

                data = message.serialize()

                prefix = struct.pack("I", len(data))
                s.sendall(prefix)
                s.sendall(data)
                message = None
        except BrokenPipeError:
            logger.debug(
                f"Socket closed unexpectedly, sender disconnecting from {self.conn.client_id}"
            )
            self.conn.close()


class Reciever(ExceptThread):
    def __init__(self, connection):
        super().__init__(f"tcp_reciever{connection.client_id}")

        self.conn = connection

    def main(self):
        s = self.conn.socket
        try:
            while True:
                data_len_raw = s.recv(4)
                if len(data_len_raw) == 0:
                    self.emergency_close()
                    return

                (data_len,) = struct.unpack("I", data_len_raw)

                data = bytearray()
                while len(data) < data_len:
                    tmp = s.recv(data_len - len(data))
                    if len(tmp) == 0:
                        self.emergency_close()
                        return
                    data.extend(tmp)

                if len(data) < data_len:
                    logger.warning(
                        f"Recieved less data than expected! (expected {data_len}, got {len(data)})"
                    )
                    self.emergency_close()
                    return

                logger.info("Recieved " + str(len(data)) + " bytes")

                message = data_parser.DataParser.parse_stream_to_content(data)
                logger.info(f'Received message: {message}')

                folder_scanner.FOLDER_SCANNER.scan()

                if isinstance(message, data_parser.FileList):
                    for file in message.file_records.values():
                        file_path = os.path.join(folder_scanner.FOLDER_SCANNER.folder_path, file.name)
                        if file.name not in globals.folder_state:
                            if file.status == data_parser.FileStatus.DELETED:
                                globals.folder_state[file.name] = file
                            else:
                                self.conn.transmit_queue.put(
                                    data_parser.FileRequest(file.name)
                                )
                        else:
                            if (
                                globals.folder_state[file.name].modification_timestamp
                                < file.modification_timestamp
                            ):
                                if str(file.status) == "1":
                                    if os.path.exists(file_path):
                                        os.remove(file_path)
                                        logger.info(f'Deleted file: {file.name}')
                                    else:
                                        logger.warning(f'File {file.name} does not exist, therefore cannot be deleted')
                                else:
                                    self.conn.transmit_queue.put(
                                        data_parser.FileRequest(file.name)
                                    )

                elif isinstance(message, data_parser.FileRequest):
                    logger.info(f'Sending file {message.file_name}')
                    with globals.folder_state_lock:
                        self.conn.transmit_queue.put(
                            data_parser.FileTransmission(
                                message.file_name,
                                globals.folder_state[
                                    message.file_name
                                ].modification_timestamp,
                                open(os.path.join(folder_scanner.FOLDER_SCANNER.folder_path, message.file_name), 'rb').read()
                            )
                        )

                elif isinstance(message, data_parser.FileTransmission):
                    with globals.folder_state_lock:
                        logger.info(f'Writing file {message.file_name} with data: {message.content}')
                        file_path = os.path.join(folder_scanner.FOLDER_SCANNER.folder_path, message.file_name)
                        with open(file_path, 'wb') as fh:
                            fh.write(message.content)
                            
                        os.utime(file_path, times=(message.time_of_modification / 1000, message.time_of_modification / 1000))

                data = None

        except ConnectionResetError:
            self.emergency_close()

    def emergency_close(self):
        logger.debug(
            f"Socket closed unexpectedly, reciever disconnecting from {self.conn.client_id}"
        )
        self.conn.close()


def accept(sock: socket.socket, address, port):
    # send welcome message
    logger.debug("Sending welcome message...")
    data = data_parser.TCPWelcome(globals.CLIENT_ID).serialize()
    sock.sendall(data)

    logger.debug("Recieving welcome message...")
    data = sock.recv(1024)
    tcp_welcome = data_parser.TCPWelcome.deserialize(data)
    client_id = tcp_welcome.client_id

    globals.CONNECTIONS[client_id] = ConnectionState(sock, address, port, client_id)
    logger.success(f"Connection established with client {client_id}!")

    Sender(globals.CONNECTIONS[client_id]).start()
    Reciever(globals.CONNECTIONS[client_id]).start()


def start(address, port, client_id):
    logger.info(
        f"Connecting to client {client_id} on address {address} using port {port}"
    )

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    accept(s, address, port)
