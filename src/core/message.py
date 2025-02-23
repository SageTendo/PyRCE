from enum import Enum, auto


class MessageType(Enum):
    """
    Enum representing different message that can be sent or received to/from the server.
    """
    ERROR = auto()
    DISCONNECT = auto()
    ECHO = auto()
    FILE_UPLOAD = auto()
    FILE_DOWNLOAD = auto()
    FILE = auto()
    END_OF_FILE = auto()
    INJECT = auto()
    EXECUTE = auto()


class Message:
    """
    Class representing a message that can be sent or received to/from the server.
    """
    __type: MessageType
    __data: bytes

    def __init__(self, message_type: MessageType = None, data: bytes = None):
        self.__type = message_type
        self.__data = data if data else b''

    @staticmethod
    def from_bytes(data: bytes):
        """
        Creates a Message object from a byte representation of the message data.
        :param data: The byte representation of the message data.
        :return: A Message object.
        """
        packet_type = MessageType(data[0])
        packet_data = b''

        if len(data) > 1:
            packet_data = data[1:]
        return Message(message_type=packet_type, data=packet_data)

    def to_bytes(self):
        """
        Converts the message to its byte representation.
        :return: The byte representation of the message
        """
        return bytes([self.__type.value]) + self.__data

    def get_type(self):
        return self.__type

    def is_type(self, expected: MessageType):
        return self.__type == expected

    @property
    def data(self):
        return self.__data

    def __repr__(self):
        return (f"""
        Message:
          TYPE: {self.__type}
          DATA: {self.__data}
        """)
