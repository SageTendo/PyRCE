import logging

from src.core.observer import RCEEventObserver


class Logger(RCEEventObserver):
    """
    Custom logger class for logging messages with different colors and prefixes.
    """

    class Colors:
        INFO = '\033[96m'
        DEBUG = '\033[94m'
        WARNING = '\033[93m'
        ERROR = '\033[91m'
        CRITICAL = '\033[95m'
        ENDC = '\033[0m'

    def __init__(self, name, debug=False):
        self.__logger = logging.getLogger(name)
        self.__logger.propagate = False

        log_level = logging.DEBUG if debug else logging.INFO
        self.__logger.setLevel(log_level)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self.get_formatter())
        self.__logger.addHandler(stream_handler)

        self.on_info(f"Logger initialized with level {logging.getLevelName(log_level)}")

    def on_info(self, message, prefix=""):
        """
        Logs an information message.
        :param message: The message to be logged.
        :param prefix: An optional prefix to be added to the message.
        """
        self.__logger.info(f"{self.Colors.INFO}{prefix}{message}{self.Colors.ENDC}")

    def on_debug(self, message, prefix=""):
        """
        Logs a debug message.
        :param message: The message to be logged.
        :param prefix: An optional prefix to be added to the message.
        """
        self.__logger.debug(f"{self.Colors.DEBUG}{prefix}{message}{self.Colors.ENDC}")

    def on_error(self, message, prefix=""):
        """
        Logs an error message.
        :param message: The message to be logged.
        :param prefix: An optional prefix to be added to the message.
        """
        self.__logger.error(f"{self.Colors.ERROR}{prefix}{message}{self.Colors.ENDC}")

    def on_connect(self, client_address: str):
        """
        Logs a message indicating that a client has connected.
        """
        self.on_info(f"Client {client_address} connected")

    def on_disconnect(self, client_address: str):
        """
        Logs a message indicating that a client has disconnected.
        """
        self.on_info(f"Client {client_address} disconnected")

    def on_message(self, sender: str, message: str):
        """
        Logs a message indicating that a message has been received from a client.
        """
        self.on_info(f"{sender}: {message}")

    @staticmethod
    def get_formatter():
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        return formatter
