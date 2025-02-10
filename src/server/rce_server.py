import socket
import threading
import time

from src.core.logger import logger
from src.core.message import Message, MessageType
from src.core.shared import Shared
from src.server.rce_server_thread import RCEServerThread


class RCEServer:
    socket: socket.socket

    def __init__(self, host, port):
        self.running = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((host, port))
            self.socket.listen()

            logger.info("Starting server...")
            logger.info(f"Listening on {host}:{port}")
            self.connection_thread = threading.Thread(target=self.connection_thread)
            self.heartbeat_thread = threading.Thread(target=self.heartbeat_thread)
        except ConnectionRefusedError:
            logger.error(f"Connection to {host}:{port} refused")

    def start(self):
        self.connection_thread.start()
        self.heartbeat_thread.start()

    def stop(self):
        Shared.close_all_clients()
        self.running = False
        self.connection_thread.join()
        self.heartbeat_thread.join()

    def connection_thread(self):
        self.running = True
        logger.info("Listening for connections...")
        while self.running:
            conn, addr = self.socket.accept()
            logger.info(f"New connection from {addr}")
            Shared.clients[addr] = RCEServerThread(conn, addr)
            Shared.clients[addr].start()
            logger.info(f"Client connected from {addr}")

    def heartbeat_thread(self):
        while self.running:
            with Shared.client_synchronize_mutex:
                for client in Shared.clients.values():
                    if not client.is_connected():
                        continue

                    client.send_message(Message(message_type=MessageType.HEARTBEAT))
                    logger.debug(f"Sent heartbeat to {client.get_address()}")
            time.sleep(5)

    @staticmethod
    def broadcast_message(message: Message):
        Shared.broadcast_message(message)
