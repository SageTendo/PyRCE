import socket
import typing
from typing import Any

from src.core.base_client import BaseClientThread
from src.core.exception import FileWriteError, MessageTypeError
from src.core.message import MessageType

if typing.TYPE_CHECKING:
    from src.server.rce_server import RCEServer


class RCEServerThread(BaseClientThread):
    """
    Represents a thread that is responsible for receiving and processing messages sent by the connected client to the
    server.
    """

    def __init__(self, client_socket: socket.socket, addr: Any, server_instance: "RCEServer"):
        super().__init__()
        self.init(client_socket, addr)
        host, port = addr
        self.server = server_instance
        self.client_address_str = f"{host}:{port}"
        self.__log_prefix = f"CLIENT {self.client_address_str} "

    def run(self):
        self.server.on_connect(self.client_address_str)
        while self.is_connected():
            try:
                message = self.receive_message()
                if message.is_type(MessageType.DISCONNECT):
                    raise OSError("RECEIVED DISCONNECT")

                if message.is_type(MessageType.ECHO):
                    self.server.on_message(self.client_address_str, message)
                elif message.is_type(MessageType.FILE_UPLOAD):  # TODO: Handle file upload action
                    self.server.on_debug("Receiving file...")
                    filename = message.data.decode()
                    self.receive_file(filename)
                    self.server.on_info(f"Received file '{filename}'", prefix=self.__log_prefix)
                elif message.is_type(MessageType.ERROR):
                    self.server.on_error(message.data.decode(), prefix=self.__log_prefix)
                else:
                    self.server.on_debug(f"Unknown message {message.get_type()}", prefix=self.__log_prefix)
            except (MessageTypeError, FileWriteError) as e:
                self.server.on_error(e, prefix=self.__log_prefix)
            except OSError as e:
                self.server.on_debug(f"DISCONNECTED => {e}", prefix=self.__log_prefix)
                self.__close_and_remove_client()
                self.server.on_disconnect(self.client_address_str)

    def __close_and_remove_client(self):
        """
        Closes the client socket and synchronously removes it from the connected clients dictionary.
        This should only be called from within the listener thread when the client disconnects from the server.
        """
        self.close()
        with self.server.client_synchronize_mutex:
            if self in self.server.connected_clients.values():
                del self.server.connected_clients[self.get_address()]
        self.server.on_debug("Client thread closed and removed from dictionary", prefix=self.__log_prefix)
