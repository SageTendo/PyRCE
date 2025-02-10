import argparse
import time

from src.client.rce_client import RCEClient
from src.core.message import MessageType, Message
from src.server.rce_server import RCEServer

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--mode', '-m', type=str, default='server', choices=['server', 'client'])
    arg_parser.add_argument('--host', '-H', type=str, default='localhost')
    arg_parser.add_argument('--port', '-p', type=int, default=6000)
    arg_parser.add_argument('--payload', '-P', type=str, default=None)
    args = arg_parser.parse_args()

    if args.host == 'localhost':
        args.host = '127.0.0.1'

    if args.mode == 'client':
        client = RCEClient(host=args.host, port=args.port)
        try:
            p = Message(message_type=MessageType.CONNECT, data=b"Hello world")
            client.send_message(p)

            while client.is_connected():
                p = Message(message_type=MessageType.HEARTBEAT)
                client.send_message(p)
                time.sleep(5)
        except KeyboardInterrupt:
            client.close()
    elif args.mode == 'server':
        server = RCEServer(args.host, args.port)
        try:
            server.start()

            # FIXME: This is test code, and will be removed in future
            old_f = None
            while True:
                if args.payload:
                    f = open(args.payload, 'r').read()
                    f = bytes(f, 'utf-8')
                    server.broadcast_message(Message(message_type=MessageType.INJECT, data=f))
                    server.broadcast_message(Message(message_type=MessageType.EXECUTE))
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
