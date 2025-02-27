import abc


class RCEEventObserver:
    """
    Interface for the implementation of observers for RCE events that the server may emit
    i.e. connection, disconnection, messages, logs.
    errors, etc.
    """

    @abc.abstractmethod
    def on_connect(self, client_address: str):
        raise NotImplementedError

    @abc.abstractmethod
    def on_disconnect(self, client_address: str):
        raise NotImplementedError

    @abc.abstractmethod
    def on_message(self, sender: str, message: str):
        raise NotImplementedError

    @abc.abstractmethod
    def on_info(self, message: str, prefix=""):
        raise NotImplementedError

    @abc.abstractmethod
    def on_debug(self, message: str, prefix=""):
        raise NotImplementedError

    @abc.abstractmethod
    def on_error(self, error: str, prefix=""):
        raise NotImplementedError
