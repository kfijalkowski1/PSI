from enum import Enum
import struct
from classes import FileState
import logger


class MessageType(Enum):
    FILE_LIST = 0
    FILE_REQUEST = 1
    FILE_TRANSMISSION = 2


MESSAGE_TYPE_MAP = {
    0: MessageType.FILE_LIST,
    1: MessageType.FILE_REQUEST,
    2: MessageType.FILE_TRANSMISSION,
}


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
        self.encrypted_content = content

    def serialize(self):
        # TODO encryption

        return (
            struct.pack("B", self.message_type.value)
            + struct.pack("L", self.time_of_modification)
            + self.file_name.encode("utf8")
            + b"\x00"
            + struct.pack("I", self.file_size)
            + self.encrypted_content
        )

    def deserialize(stream: bytes):
        stream_len = len(stream) - struct.calcsize("L")
        time, stream = struct.unpack(f"L{stream_len}s", stream)

        name = stream.split(b"\x00")[0]
        name_len = len(name) + 1
        stream = stream[name_len:]

        size_len = len(stream) - struct.calcsize("I")
        size, content = struct.unpack(f"I{size_len}s", stream)

        return FileTransmission(name.decode("utf8"), time, content)


class DataParser:
    def parse_stream_to_content(stream: bytes):
        message_type, message_content = struct.unpack(f"B{len(stream) - 1}s", stream)
        message_type = MESSAGE_TYPE_MAP[message_type]
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
