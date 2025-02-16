import socket
import threading
from typing import Optional

from src.core.logger import Logger
from src.core.message import Message
from src.core.shared import Shared
from src.server.rce_server_thread import RCEServerThread


class RCEServer:
    """
    Represents a remote code execution (RCE) server that listens for and handles client connections and messages.
    """
    __socket: socket.socket
    __running = False

    def __init__(self, host: str, port: int, debug=False):
        self.__host = host
        self.__port = port
        self.connection_thread: Optional[threading.Thread] = None
        self.__logger = Logger(self.__class__.__name__, debug)

    def __init_socket(self):
        """
        Initializes the server socket and starts listening for client connections.
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind((self.__host, self.__port))
        self.__socket.listen(5)
        self.__socket.settimeout(1)
        self.__running = True

    def __connection_thread(self):
        """
        Handles incoming client connections and creates a new RCEServerThread for handling each client connection.
        New clients are synchronously added to the dictionary of connected clients.
        """
        while self.__running:
            try:
                conn, addr = self.__socket.accept()
                with Shared.client_synchronize_mutex:
                    Shared.connected_clients[addr] = RCEServerThread(conn, addr, self.__logger)
                    Shared.connected_clients[addr].start()
                self.__logger.info(f"Client {addr} connected")
            except socket.timeout:
                pass

    def start(self):
        """
        Starts the RCE server by initializing the socket and starting the connection thread which listens for and
        handles new client connections.
        """
        try:
            self.__init_socket()
            self.__logger.info(f"Server started at {self.__host}:{self.__port}")
            self.__logger.info("Listening for connections...")

            self.connection_thread = threading.Thread(target=self.__connection_thread)
            self.connection_thread.start()
        except ConnectionRefusedError:
            self.__logger.error(f"Connection to {self.__host}:{self.__port} refused")

    def stop(self):
        """
        Stops the RCE server by closing all client connections and the socket.
        """
        self.__running = False

        self.close_all_clients()
        if self.connection_thread:
            self.connection_thread.join()
        self.__socket.close()

    def broadcast_message(self, message: Message):
        """
        Synchronously sends a message to all connected clients.
        :param message: A message object representing the message to be sent to all connected clients.
        """
        with Shared.client_synchronize_mutex:
            for client in Shared.connected_clients.values():
                if not client.is_connected():
                    continue

                try:
                    client.send_message(message)
                except OSError as e:
                    self.__logger.debug(f"Failed to send message to {client.get_address()}:{e}")

    def close_all_clients(self):
        """
        Synchronously closes all connected clients and clears the connected clients dictionary.
        """
        with Shared.client_synchronize_mutex:
            if len(Shared.connected_clients) == 0:
                return

            for client in Shared.connected_clients.values():
                if not client.is_connected():
                    continue
                client.close()
            Shared.connected_clients.clear()
            self.__logger.debug("All clients disconnected")

    def is_running(self) -> bool:
        return self.__running

    def get_host(self):
        return self.__host

    def get_port(self):
        return self.__port

    def get_address(self):
        return self.__host, self.__port
