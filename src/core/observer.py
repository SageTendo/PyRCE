import abc


class RCEEventObserver:
    """
    Interface for the implementation of observers for RCE events that the server may emit
    i.e. connection, disconnection, messages, logs, errors, etc.
    """

    @abc.abstractmethod
    def on_connect(self, client_address: str):
        """
        Handles a client connection event
        :param client_address: The address of the client
        """
        raise NotImplementedError

    @abc.abstractmethod
    def on_disconnect(self, client_address: str):
        """
        Handles a client disconnection event
        :param client_address: The address of the client
        """
        raise NotImplementedError

    @abc.abstractmethod
    def on_message(self, sender: str, message: str):
        """
        Handles message events
        :param sender: The address of the client that sent the message
        :param message: The message sent by the client
        """
        raise NotImplementedError

    @abc.abstractmethod
    def on_info(self, message: str, prefix=""):
        """
        Handles information log events
        :param message: The message to be logged
        :param prefix: An optional prefix to be added to the message (e.g. a client address)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def on_debug(self, message: str, prefix=""):
        """
        Handles debug log events
        :param message: The message to be logged
        :param prefix: An optional prefix to be added to the message (e.g. a client address)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def on_error(self, error: str, prefix=""):
        """
        Handles error log events
        :param error: The error message to be logged
        :param prefix: The prefix to be added to the error message
        """
        raise NotImplementedError
