import socket
from typing import Any

from src.core.base_client import BaseClientThread
from src.core.logger import logger
from src.core.message import MessageType
from src.core.shared import Shared


class RCEServerThread(BaseClientThread):
    def __init__(self, client_socket: socket.socket, addr: Any):
        super().__init__()
        self.init(client_socket, addr)

    def run(self):
        logger.info("Listening for messages...")
        while self.is_connected():
            if message := self.receive_message():
                if message.is_type(MessageType.HEARTBEAT):
                    logger.info(f"Received heartbeat from {self.get_address()}")
                elif message.is_type(MessageType.ECHO):
                    logger.info(f"Received echo from {self.get_address()}:\n{message}")
                    logger.info(message.data.decode())
                elif message.is_type(MessageType.DATA):
                    logger.info(f"Received data from {self.get_address()}:\n{message}")
                elif message.is_type(MessageType.CONNECT):
                    logger.info(f"Received connect from {self.get_address()}:\n{message}")
                elif message.is_type(MessageType.DISCONNECT):
                    logger.info(f"Received disconnect from {self.get_address()}")
                    self.close()
                    logger.info(f"Client disconnected from {self.get_address()}")
                elif message.is_type(MessageType.ERROR):
                    self.close()
                    logger.info(f"Received error from {self.get_address()}:\n{message}")
                elif message.is_type(MessageType.NULL):
                    self.close()
                    logger.info(f"{self.get_address()} DISCONNECTED: Received null packet")
                else:
                    logger.info(f"Received unknown packet type from {self.get_address()}: {message.get_type()}")
            else:
                self.close()
                logger.info(f"Client disconnected from {self.get_address()}... No data received")

    def close(self):
        with Shared.client_synchronize_mutex:
            Shared.clients.pop(self.get_address())
        super().close()
