import argparse

import config
from src.client.rce_client import RCEClient
from src.console.server_gui import ServerGUI
from src.server.rce_server import RCEServer

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--mode', '-m', type=str, default='server', choices=['server', 'client'])
arg_parser.add_argument('--host', '-H', type=str, default=config.HOST)
arg_parser.add_argument('--port', '-p', type=int, default=config.PORT)
arg_parser.add_argument('--debug', '-d', action='store_true', default=0)
args = arg_parser.parse_args()


def main():
    if args.host == 'localhost':
        args.host = '127.0.0.1'

    if args.mode == 'client':
        client = None
        try:
            client = RCEClient(host=args.host, port=args.port, debug=args.debug)
            client.start()
        except KeyboardInterrupt:
            client.close()
    elif args.mode == 'server':
        gui = None
        try:
            server = RCEServer(args.host, args.port, args.debug)
            gui = ServerGUI(server)
            gui.build()
        except KeyboardInterrupt:
            gui.close_windows()
            exit(0)
    else:
        print("Unknown mode: %s" % args.mode)
        exit(1)


if __name__ == '__main__':
    main()
