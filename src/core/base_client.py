import abc
import socket
import threading
from typing import Optional, Any

from src.core.logger import logger
from src.core.message import Message, MessageType


class BaseClientThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.__host = ""
        self.__port = 0
        self.__address = None
        self.__connected = False
        self.__socket = None
        self.__listener_thread = None

    def init(self, client_socket: socket.socket, addr: Any):
        self.__socket = client_socket
        self.__address = addr
        self.__connected = True

    def connect_to_server(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__connected = False

        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((host, port))
            self.__listener_thread = threading.Thread(target=self.run)
            self.__listener_thread.start()
            self.__connected = True
            logger.info(f"Connected to {host}:{port}")
        except ConnectionRefusedError:
            logger.error(f"Connection to {host}:{port} refused")

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

    def close(self):
        self.__connected = False
        self.__socket.close()

    def is_connected(self):
        return self.__connected

    def send_message(self, message: Message):
        try:
            data = message.set_sender(self.__socket.getsockname()).to_bytes()
            data_size = len(data).to_bytes(4, byteorder='little')
            self.__socket.sendall(data_size)
            self.__socket.sendall(data)
        except OSError:
            logger.info("Client disconnected.. No data sent")

    def receive_message(self) -> Optional[Message]:
        try:
            data_size = int.from_bytes(self.__socket.recv(4), byteorder='little')
            if not data_size:
                raise OSError
            return Message.from_bytes(self.__socket.recv(data_size))
        except OSError:
            logger.info("Client disconnected.. No data received")
            return Message(message_type=MessageType.NULL)

    def get_address(self):
        return self.__address
