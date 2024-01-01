from enum import Enum

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
    def __init__(self, message_content: bytes):
        self.record_type = message_content[0].decode('utf-8')
        self.time_of_modification = message_content[1:5].decode('utf-8')
        self.file_name = message_content[6:].decode('utf-8')
    
    def object_encode(self):
        return (self.record_type + self.time_of_modification + self.file_name).encode('utf-8')

class FileList:
    def __init__(self, message_content: bytes):
        self.message_type = MessageType.FILE_LIST
        list_of_file_records = []
        for file_record in message_content.split('\x00'):
            list_of_file_records.append(FileRecord(file_record))
        self.list_of_file_records = list_of_file_records
        
    def object_encode(self):
        return (self.message_type.value + '\x00'.join(self.list_of_file_records)).encode('utf-8')


class FileRequest:
    def __init__(self, message_content: bytes):
        self.message_type = MessageType.FILE_REQUEST
        self.file_name = message_content.split('\x00')[0].decode('utf-8')
    
    def object_encode(self):
        return (self.message_type.value + self.file_name).encode('utf-8')

class FileTransmission:
    def __init__(self, message_content: bytes):
        self.message_type = MessageType.FILE_TRANSMISSION
        self.time_of_modification = message_content[:4]
        file_name, file_size_and_content = message_content[5:].split('\x00')
        self.file_name = file_name.decode('utf-8')
        self.file_size = file_size_and_content[:4].decode('utf-8')
        self.encrypted_content = file_size_and_content[5:int(self.file_size)].decode('utf-8')
    
    def object_encode(self):
        return (self.message_type.value + self.time_of_modification + self.file_name + '\x00' + self.file_size + self.encrypted_content).encode('utf-8')


class DataParser:
    def parse_stream_to_object(self, stream: bytes):
        message_type = MESSAGE_TYPE_MAP[int(stream[0].decode('utf-8'))]
        obj = None
        if message_type == MessageType.FILE_LIST:
            obj = FileList(stream[1:])
        elif message_type == MessageType.FILE_REQUEST:
            obj = FileRequest(stream[1:])
        elif message_type == MessageType.FILE_TRANSMISSION:
            obj = FileTransmission(stream[1:])
        else:
            raise TypeError('Incorrect message type')
        return obj
    
    def parse_object_to_stream(self, object):
        return object.object_encode()
