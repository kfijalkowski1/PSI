from enum import Enum
import struct
import uuid
from crypting import encrypt, decrypt

class MessageType(Enum):
    FILE_LIST = 0
    FILE_REQUEST = 1
    FILE_TRANSMISSION = 2


class FileStatus(Enum):
    LATEST = 0
    DELETED = 1
    PENDING = 2


class UDPDiscovery:
    def __init__(self, client_id, tcp_port):
        self.client_id = client_id
        self.tcp_port = tcp_port

    def serialize(self):
        return struct.pack("16sH", self.client_id.bytes, self.tcp_port)

    def deserialize(stream: bytes):
        client_id_raw, port = struct.unpack("16sH", stream)

        client_id = uuid.UUID(bytes=client_id_raw)

        return UDPDiscovery(client_id, port)


class TCPWelcome:
    def __init__(self, client_id):
        self.client_id = client_id

    def serialize(self):
        return struct.pack("16s", self.client_id.bytes)

    def deserialize(stream: bytes):
        (client_id_raw,) = struct.unpack("16s", stream)
        client_id = uuid.UUID(bytes=client_id_raw)

        return TCPWelcome(client_id)


class CloseConnection:
    def __init__(self):
        pass


class FileState:
    def __init__(self, name, modification_timestamp, status=FileStatus.LATEST):
        self.name = name
        self.modification_timestamp = modification_timestamp
        self.status = status

    def update(self, modification_timestamp, status=None):
        if modification_timestamp:
            self.modification_timestamp = modification_timestamp
        if status:
            self.status = status

    def serialize(self) -> bytes:
        return struct.pack(
            "BL", self.status.value, self.modification_timestamp
        ) + self.name.encode("utf8")

    def deserialize(stream: bytes):
        name_size = len(stream) - struct.calcsize("BL")
        rec_type, time, name = struct.unpack(f"BL{name_size}s", stream)

        return FileState(name.decode("utf8"), time, rec_type)

    def __repr__(self):
        return f"FileState(name='{self.name}', modification_timestamp='{self.modification_timestamp}', status='{self.status}')"


class FileList:
    def __init__(self, files):
        self.message_type = MessageType.FILE_LIST
        self.file_records = files

    def serialize(self):
        return struct.pack("B", self.message_type.value) + b"\x00".join(
            [file.serialize() for file in self.file_records.values()]
        )

    def deserialize(stream: bytes):
        file_records = {}
        while len(stream) > 0:
            prefix_len = struct.calcsize("BL")
            message = stream[:prefix_len] + stream[prefix_len:].split(b"\x00")[0]

            record = FileState.deserialize(message)
            file_records[record.name] = record

            message_len = len(message) + 1
            stream = stream[message_len:]

        return FileList(file_records)


class FileRequest:
    def __init__(self, file_name):
        self.message_type = MessageType.FILE_REQUEST
        self.file_name = file_name

    def serialize(self):
        return (
            struct.pack("B", self.message_type.value)
            + self.file_name.encode("utf8")
            + b"\x00"
        )

    def deserialize(stream: bytes):
        file_name = stream.split(b"\x00")[0].decode("utf8")
        return FileRequest(file_name)


class FileTransmission:
    def __init__(self, name, time, content):
        self.message_type = MessageType.FILE_TRANSMISSION

        self.time_of_modification = time
        self.file_name = name
        self.file_size = len(content)
        self.content = content

    def serialize(self):
        encryptet_content = encrypt(self.content)

        return (
            struct.pack("B", self.message_type.value)
            + struct.pack("L", self.time_of_modification)
            + self.file_name.encode("utf8")
            + b"\x00"
            + struct.pack("I", self.file_size)
            + encryptet_content
        )

    def deserialize(stream: bytes):
        stream_len = len(stream) - struct.calcsize("L")
        time, stream = struct.unpack(f"L{stream_len}s", stream)

        name = stream.split(b"\x00")[0]
        name_len = len(name) + 1
        stream = stream[name_len:]

        size_len = len(stream) - struct.calcsize("I")
        size, content = struct.unpack(f"I{size_len}s", stream)

        content = decrypt(content)

        return FileTransmission(name.decode("utf8"), time, content)


class DataParser:
    def parse_stream_to_content(stream: bytes):
        message_type, message_content = struct.unpack(f"B{len(stream) - 1}s", stream)
        message_type = MessageType(message_type)
        obj = None
        if message_type == MessageType.FILE_LIST:
            obj = FileList.deserialize(message_content)
        elif message_type == MessageType.FILE_REQUEST:
            obj = FileRequest.deserialize(message_content)
        elif message_type == MessageType.FILE_TRANSMISSION:
            obj = FileTransmission.deserialize(message_content)
        else:
            raise TypeError("Incorrect message type")
        return obj

    def serialize_object(self, object):
        return object.serialize()

    def deserialize_object(self, object):
        return object.deserialize()
