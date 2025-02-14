import logging
import threading


class Logger:
    """
    Custom logger class for logging messages with different colors and prefixes.
    A mutex is used to prevent concurrent access to a shared logger instance.
    """
    logging_mutex = threading.Lock()

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
        console_handler = logging.StreamHandler()

        log_level = logging.DEBUG if debug else logging.INFO
        self.__logger.setLevel(log_level)
        console_handler.setLevel(log_level)

        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.__logger.addHandler(console_handler)
        self.info(f"Logger initialized with level {logging.getLevelName(log_level)}")

    def info(self, message, prefix=""):
        """
        Logs an information message.
        :param message: The message to be logged.
        :param prefix: An optional prefix to be added to the message.
        """
        with Logger.logging_mutex:
            self.__logger.info(f"{self.Colors.INFO}{prefix}{message}{self.Colors.ENDC}")

    def debug(self, message, prefix=""):
        """
        Logs a debug message.
        :param message: The message to be logged.
        :param prefix: An optional prefix to be added to the message.
        """
        with Logger.logging_mutex:
            self.__logger.debug(f"{self.Colors.DEBUG}{prefix}{message}{self.Colors.ENDC}")

    def error(self, message, prefix=""):
        """
        Logs an error message.
        :param message: The message to be logged.
        :param prefix: An optional prefix to be added to the message.
        """
        with Logger.logging_mutex:
            self.__logger.error(f"{self.Colors.ERROR}{prefix}{message}{self.Colors.ENDC}")

    def warning(self, message, prefix=""):
        """
        Logs a warning message.
        :param message: The message to be logged.
        :param prefix: An optional prefix to be added to the message.
        """
        with Logger.logging_mutex:
            self.__logger.warning(f"{self.Colors.WARNING}{prefix}{message}{self.Colors.ENDC}")

    def critical(self, message, prefix=""):
        """
        Logs a critical message.
        :param message: The message to be logged.
        :param prefix: An optional prefix to be added to the message.
        """
        with Logger.logging_mutex:
            self.__logger.critical(f"{self.Colors.CRITICAL}{prefix}{message}{self.Colors.ENDC}")
