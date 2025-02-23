import abc
import os.path
import socket
import threading
from pathlib import Path
from typing import Any, Optional

import config
from src.core.exception import FileWriteError, FileReadError, MessageTypeError
from src.core.message import Message, MessageType


class BaseClientThread(threading.Thread):
    """
    Base class for client/server threads that are responsible for sending and receiving messages from/to the server
    """

    def __init__(self):
        super().__init__()
        self.__host = ""
        self.__port = 0
        self.__address = None
        self.__connected = False
        self.__socket: Optional[socket.socket] = None

    def init(self, client_socket: socket.socket, addr: Any):
        self.__socket = client_socket
        self.__address = addr
        self.__connected = True

    def connect_to_server(self, host: str, port: int):
        """
        Connects to the server at the given host and port.
        :param host: The server's hostname or IP.
        :param port: The port number.
        :raises ConnectionRefusedError: If the connection is refused.
        """
        self.__host = host
        self.__port = port
        self.__connected = False

        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((host, port))
            self.__connected = True
        except ConnectionRefusedError as error:
            raise error

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

    def close(self):
        """
        Closes the socket connection.
        If the connection is already closed, the method returns immediately.
        :raises: OSError: If an error occurs during socket shutdown or closure.
        """
        if not self.__connected:
            return

        self.__connected = False
        self.__socket.shutdown(socket.SHUT_RDWR)
        self.__socket.close()

    def is_connected(self):
        return self.__connected

    def send_message(self, message: Message):
        """
        Sends a message over the socket.
        This method performs the following steps:
          1. Sets the sender information for the message using the socket's own address.
          2. Converts the message to its byte representation.
          3. Calculates the length of the data and converts this length to a 4-byte little-endian integer.
          4. Sends the length of the data followed by the actual data over the socket.

        :param message: The message object to be sent.
        :raises: OSError: If an error occurs while sending data over the socket.
        """
        try:
            data = message.to_bytes()
            data_size = len(data).to_bytes(4, byteorder="little")
            self.__socket.sendall(data_size)
            self.__socket.sendall(data)
        except OSError as error:
            raise error

    def receive_message(self):
        """
        Receives a message from the socket.
        This method performs the following steps:
            1. Reads 4 bytes from the socket and converts them to an integer (little-endian)
                representing the size of the incoming message.
            2. Checks if the received size is zero and raises an OSError if true.
            3. Reads the specified number of bytes from the socket.
            4. Converts the received bytes into a Message object.

       :returns: A Message object containing the data received from the socket.
       :raises: OSError: If an error occurs while receiving data or if the received message size is zero.
       """

        def __receive_all(size):
            """
            Helper function to receive `size` bytes reliably.

            :param size: Number of bytes to receive.
            :returns: The received bytes.
            :raises OSError: If the connection is closed unexpectedly.
            """
            buffer = bytearray()
            while len(buffer) < size:
                next_chunk_size = size - len(buffer)
                if not (packet := self.__socket.recv(next_chunk_size)):
                    raise OSError("Connection closed while receiving data")
                buffer.extend(packet)
            return bytes(buffer)

        try:
            if not (data_size := self.__socket.recv(4)):
                raise OSError("Connection closed by peer")

            if not (data_size_as_int := int.from_bytes(data_size, byteorder='little')):
                raise OSError("Received null bytes for message size")

            data = __receive_all(data_size_as_int)
            return Message.from_bytes(data)
        except OSError as error:
            raise error

    def send_file(self, source_path: str, destination_path: str = ""):
        """
        Sends a file to the client/server.
        :param source_path: The path to the file to be sent.
        :param destination_path: The path where the file should be saved on the server.
        :raises:
            FileNotFoundError: When a file with the given path does not exist.
            FileReadError: When an error occurs while reading the file.
        """
        filepath = Path(source_path)
        if not filepath.exists():
            raise FileNotFoundError(f"{filepath} does not exist")

        if not filepath.is_file():
            raise FileNotFoundError(f"{filepath} is not a file")

        filename_with_destination = os.path.join(destination_path, filepath.name).encode()
        self.send_message(Message(message_type=MessageType.FILE_UPLOAD, data=filename_with_destination))
        try:
            with open(filepath, 'rb') as file:
                while chunk := file.read(config.FILE_CHUNK_SIZE):
                    self.send_message(Message(MessageType.FILE, chunk))
                self.send_message(Message(MessageType.END_OF_FILE))
        except OSError:
            raise FileReadError(f"Failed to read file {filepath}")

    def receive_file(self, filename: str, save_path: Path = None):
        """
        Receives a file from the server and saves it locally.
        :param filename: The name of the file to be saved.
        :param save_path: The path where the file should be saved (applies to client-side handling).
        :raises:
            MessageTypeError: When the next message is not of type MessageType.FILE.
            FileWriteError: When an error occurs while writing the file.
        """
        if not save_path:  # Server-side handling
            save_path = config.DOWNLOAD_DIR / f"{self.__address[0]}:{self.__address[1]}"

        if not save_path.exists():
            os.makedirs(save_path, exist_ok=True)

        try:
            file_path = save_path / filename
            with open(file_path, 'wb') as file:
                while True:
                    message = self.receive_message()
                    if message.is_type(MessageType.END_OF_FILE):
                        break

                    if not message.is_type(MessageType.FILE):
                        raise MessageTypeError(
                            f"Invalid message type provided: {message.get_type()}, expected FILE type")
                    file.write(message.data)
        except OSError:
            raise FileWriteError(f"Failed to save file {save_path}")

    def get_address(self):
        return self.__address
