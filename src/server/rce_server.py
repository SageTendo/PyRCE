import re
import socket
import threading
from typing import Optional

import config
from src.core.exception import FileReadError
from src.core.logger import Logger
from src.core.message import Message
from src.core.observer import RCEEventObserver
from src.server.rce_server_thread import RCEServerThread


class RCEServer:
    """
    Represents a remote code execution (RCE) server that listens for and handles client connections and messages.
    """
    __socket: socket.socket
    __running = False
    client_synchronize_mutex = threading.Lock()
    connected_clients = dict[tuple[str, int], RCEServerThread]()

    def __init__(self, host: str, port: int, debug=False):
        self.__host = host
        self.__port = port
        self.connection_thread: Optional[threading.Thread] = None
        self.observers: list[RCEEventObserver] = []
        self.observers.append(Logger(self.__class__.__name__, debug))
        self.debug = debug

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
                with self.client_synchronize_mutex:
                    self.connected_clients[addr] = RCEServerThread(conn, addr, self)
                    self.connected_clients[addr].start()
            except socket.timeout:
                pass

    def start(self):
        """
        Starts the RCE server by initializing the socket and starting the connection thread which listens for and
        handles new client connections.
        """
        if self.__running:
            return False

        try:
            self.__init_socket()
            self.on_info(f"Server started at {self.__host}:{self.__port}")
            self.on_info("Listening for connections...")
            self.connection_thread = threading.Thread(target=self.__connection_thread)
            self.connection_thread.start()
            return True
        except ConnectionRefusedError:
            self.on_error(f"Connection to {self.__host}:{self.__port} refused")
        return False

    def stop(self):
        """
        Stops the RCE server by closing all client connections and the socket.
        """
        if not self.__running:
            return False

        self.__running = False
        self.__close_all_clients()
        if self.connection_thread:
            self.connection_thread.join()
        self.__socket.close()
        return True

    def broadcast_message(self, message: Message):
        """
        Synchronously sends a message to all connected clients.
        :param message: A message object representing the message to be sent to all connected clients.
        """
        with self.client_synchronize_mutex:
            for client in self.connected_clients.values():
                if not client.is_connected():
                    continue

                try:
                    client.send_message(message)
                except OSError as e:
                    self.on_error(f"Failed to send message to {client.get_address()}:{e}")

    def send_message_to_client(self, client_address: str, message: Message):
        """
        Sends a message to a specific client.
        :param client_address: String representation of the client's address
        :param message: A message object representing the message to be sent to the client
        """
        try:
            if client := self.__get_client_from_address(client_address):
                client.send_message(message)
        except OSError as e:
            self.on_error(f"Failed to send message to {client_address}: {e}")

    def send_file_to_client(self, client_address: str, filename: str, destination_path: str = ""):
        """
        Sends a file to a specific client.
        :param client_address: String representation of the client's address
        :param filename: The name of the file to send to the client
        :param destination_path: The destination path which the file will be saved client-side
        """
        try:
            if client := self.__get_client_from_address(client_address):
                client.send_file(filename, destination_path)
        except (FileNotFoundError, FileReadError) as e:
            self.on_error(e)
        except OSError as e:
            self.on_error(f"Failed to send file to {client_address}: {e}")

    def __get_client_from_address(self, client_address: str):
        """
        Returns a client with the given address
        :param client_address: The address of the client (as IPV4)
        :return: The client thread corresponding to the client address
        """
        if not re.match(config.IPV4_PATTERN, client_address):
            self.on_error(f"Invalid client address: {client_address}")
            return

        host, port = client_address.split(":")
        client_addr = (host, int(port))
        with self.client_synchronize_mutex:
            if not (client := self.connected_clients.get(client_addr)) or not client.is_connected():
                self.on_error(f"Client '{client_addr}' not found")
                return
            return client

    def __close_all_clients(self):
        """
        Synchronously closes all connected clients and clears the connected clients dictionary.
        """
        with self.client_synchronize_mutex:
            if len(self.connected_clients) == 0:
                return

            for client in self.connected_clients.values():
                if not client.is_connected():
                    continue
                client.close()
            self.connected_clients.clear()
            self.on_debug("All clients disconnected")

    def is_running(self) -> bool:
        return self.__running

    def get_host(self):
        return self.__host

    def get_port(self):
        return self.__port

    def get_address(self):
        return self.__host, self.__port

    def add_observer(self, observer: RCEEventObserver):
        self.observers.append(observer)

    def on_connect(self, client_address: str):
        for observer in self.observers:
            observer.on_connect(client_address)

    def on_disconnect(self, client_address: str):
        for observer in self.observers:
            observer.on_disconnect(client_address)

    def on_message(self, sender: str, message: Message):
        for observer in self.observers:
            observer.on_message(sender, message.data.decode())

    def on_info(self, message: str, prefix=""):
        for observer in self.observers:
            observer.on_info(message, prefix)

    def on_debug(self, message: str, prefix=""):
        if not self.debug:
            return

        for observer in self.observers:
            observer.on_debug(message, prefix)

    def on_error(self, error: str, prefix=""):
        for observer in self.observers:
            observer.on_error(error, prefix)
