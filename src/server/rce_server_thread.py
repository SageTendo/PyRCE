import socket
from typing import Any

from src.core.base_client import BaseClientThread
from src.core.logger import Logger
from src.core.message import MessageType
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
                elif message.is_type(MessageType.FILE):
                    self.__logger.debug("Received file", prefix=self.__log_prefix)
                elif message.is_type(MessageType.ERROR):
                    self.__logger.debug("Received error", prefix=self.__log_prefix)
                else:
                    self.__logger.debug(f"Unknown message {message.get_type()}", prefix=self.__log_prefix)
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
