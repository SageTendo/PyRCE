import socket
from typing import Any

from src.core.base_client import BaseClientThread
from src.core.exception import FileReadError, FileWriteError, MessageTypeError
from src.core.logger import Logger
from src.core.message import MessageType, Message
from src.core.shared import Shared


class RCEServerThread(BaseClientThread):
    """
    Represents a thread that is responsible for receiving and processing messages sent by the connected client to the
    server.
    """

    def __init__(self, client_socket: socket.socket, addr: Any, logger: Logger):
        super().__init__()
        self.init(client_socket, addr)
        host, port = addr
        self.__logger = logger
        self.__log_prefix = f"CLIENT {host}:{port} - "

    def run(self):
        self.__logger.info("Listener thread started", prefix=self.__log_prefix)
        while self.is_connected():
            try:
                message = self.receive_message()
                if message.is_type(MessageType.DISCONNECT):
                    raise OSError("RECEIVED DISCONNECT")

                if message.is_type(MessageType.ECHO):
                    self.__logger.debug("Received echo", prefix=self.__log_prefix)
                    self.__logger.info(message.data.decode(), prefix=self.__log_prefix)
                elif message.is_type(MessageType.FILE_UPLOAD):
                    self.__logger.debug("Receiving file...")
                    filename = message.data.decode()
                    self.receive_file(filename)
                    self.__logger.info(f"Received file '{filename}'", prefix=self.__log_prefix)
                elif message.is_type(MessageType.ERROR):
                    self.__logger.error(message.data.decode(), prefix=self.__log_prefix)
                else:
                    self.__logger.debug(f"Unknown message {message.get_type()}", prefix=self.__log_prefix)
            except (FileNotFoundError, MessageTypeError, FileReadError, FileWriteError) as e:
                self.__logger.error(e, prefix=self.__log_prefix)
                self.send_message(Message(message_type=MessageType.ERROR, data=e.args[0].encode()))
            except OSError as e:
                self.__logger.error(f"DISCONNECTED => {e}", prefix=self.__log_prefix)
                self.__close_and_remove_client()

    def __close_and_remove_client(self):
        """
        Closes the client socket and synchronously removes it from the connected clients dictionary.
        This should only be called from within the listener thread when the client disconnects from the server.
        """
        self.close()
        with Shared.client_synchronize_mutex:
            if self in Shared.connected_clients.values():
                del Shared.connected_clients[self.get_address()]
        self.__logger.debug("Client thread closed and removed from dictionary", prefix=self.__log_prefix)
