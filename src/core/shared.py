import typing
from threading import Lock

from src.core.logger import logger
from src.core.message import Message

if typing.TYPE_CHECKING:
    from src.server.rce_server_thread import RCEServerThread


class Shared:
    client_synchronize_mutex = Lock()
    clients: dict[tuple[str, int], "RCEServerThread"] = {}

    @classmethod
    def broadcast_message(cls, message: Message):
        with cls.client_synchronize_mutex:
            for client in cls.clients.values():
                if not client.is_connected():
                    continue

                client.send_message(message)
                logger.info(f"Sent message to {client.get_address()}")

    @classmethod
    def close_all_clients(cls):
        with cls.client_synchronize_mutex:
            for client_id in cls.clients:
                client = cls.clients.pop(client_id)
                client.close()
