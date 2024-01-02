from enum import Enum
import struct

class MessageType(Enum):
    FILE_LIST = 0
    FILE_REQUEST = 1
    FILE_TRANSMISSION = 2

MESSAGE_TYPE_MAP = {
    0: MessageType.FILE_LIST,
    1: MessageType.FILE_REQUEST,
    2: MessageType.FILE_TRANSMISSION
}

class FileRecord:
    def __init__(self, stream: bytes):
        self.deserialize(stream)

    def serialize(self) -> bytes:
        return self.record_type + self.time_of_modification + self.file_name

    def deserialize(self, stream: bytes):
        name_size = len(stream) - struct.calcsize('BI')
        rec_type, time, name = struct.unpack(f'BI{name_size}s', stream)
        self.record_type = rec_type
        self.time_of_modification = time
        self.file_name = name

class FileList:
    def __init__(self, stream: bytes):
        self.message_type = MessageType.FILE_LIST
        self.deserialize(stream)
    
    def serialize(self):
        return self.message_type.value + b'\x00'.join(self.list_of_file_records)

    def deserialize(self, stream: bytes):
        list_of_file_records = []
        for file_record in stream.split(b'\x00'):
            list_of_file_records.append(FileRecord(file_record))
        self.list_of_file_records = list_of_file_records

class FileRequest:
    def __init__(self, stream: bytes):
        self.message_type = MessageType.FILE_REQUEST
        self.deserialize(stream)
        
    def serialize(self):
        return self.message_type.value + self.file_name

    def deserialize(self, stream: bytes):
        self.file_name = stream.split(b'\x00')[0]

class FileTransmission:
    def __init__(self, stream: bytes):
        self.message_type = MessageType.FILE_TRANSMISSION
        self.deserialize(stream)
    
    def serialize(self):
        return self.message_type.value + self.time_of_modification + self.file_name + b'\x00' + self.file_size + self.encrypted_content

    def deserialize(self, stream: bytes):
        time_name, size_content = stream.split('\x00')
        time, name = struct.unpack(f'I{len(time_name) - struct.calcsize("I")}s', time_name)
        size = struct.unpack('I', size_content[:4])[0]
        content = struct.unpack(f'{size}s', size_content[4:])[0]
        
        self.time_of_modification = time
        self.file_name = name
        self.file_size = size
        self.encrypted_content = content
        
class DataParser:
    def parse_stream_to_content(self, stream: bytes):
        message_type, message_content = struct.unpack(f'B{len(stream) - 1}s', stream)
        message_type = MESSAGE_TYPE_MAP[message_type]
        obj = None
        if message_type == MessageType.FILE_LIST:
            obj = FileList(message_content)
        elif message_type == MessageType.FILE_REQUEST:
            obj = FileRequest(message_content)
        elif message_type == MessageType.FILE_TRANSMISSION:
            obj = FileTransmission(message_content)
        else:
            raise TypeError('Incorrect message type')
        return obj
    
    def serialize_object(self, object):
        return object.serialize()

    def deserialize_object(self, object):
        return object.deserialize()
