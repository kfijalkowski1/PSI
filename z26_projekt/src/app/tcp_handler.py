import socket
import struct
import uuid

import globals
import logger
from utils import ExceptThread
from classes import ConnectionState, FileStatus
import data_parser


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
                # TODO: use dedicated class when data_parser is ready
                if message == b"close":
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
                logger.info(message)
                if isinstance(message, data_parser.FileList):
                    for file in message.file_records.values():
                        if file.name not in globals.folder_state:
                            if file.status == FileStatus.DELETED:
                                globals.folder_state[file.name] = file
                            else:
                                self.conn.transmit_queue.put(
                                    data_parser.FileRequest(file.name)
                                )
                                pass
                        else:
                            if (
                                globals.folder_state[file.name].modification_timestamp
                                < file.modification_timestamp
                            ):
                                if file.status == FileStatus.DELETED:
                                    # TODO delete file
                                    pass
                                else:
                                    self.conn.transmit_queue.put(
                                        data_parser.FileRequest(file.name)
                                    )
                                    pass

                elif isinstance(message, data_parser.FileRequest):
                    self.conn.transmit_queue.put(
                        data_parser.FileTransmission(
                            message.file_name,
                            globals.folder_state[
                                message.file_name
                            ].modification_timestamp,
                            # TODO read file contents
                            b"AAAAAAAAAAAAA",
                        )
                    )

                    pass
                elif isinstance(message, data_parser.FileTransmission):
                    logger.info(message.encrypted_content)
                    # TODO save file
                    pass

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
    # TODO use data_parser
    logger.debug("Sending welcome message...")
    data = struct.pack("16s", globals.CLIENT_ID.bytes)
    sock.sendall(data)

    logger.debug("Recieving welcome message...")
    data = sock.recv(1024)
    (client_id,) = struct.unpack("16s", data)
    client_id = uuid.UUID(bytes=client_id)

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
