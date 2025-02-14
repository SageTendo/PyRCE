import threading
import typing

if typing.TYPE_CHECKING:
    from src.server.rce_server_thread import RCEServerThread


class Shared:
    """
    A class to manage shared resources between threads.
    """
    client_synchronize_mutex = threading.Lock()
    connected_clients: dict[tuple[str, int], "RCEServerThread"] = {}
