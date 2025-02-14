import argparse

from src.client.rce_client import RCEClient
from src.console.server_cli import ServerCLI
from src.server.rce_server import RCEServer

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--mode', '-m', type=str, default='server', choices=['server', 'client'])
arg_parser.add_argument('--host', '-H', type=str, default='localhost')
arg_parser.add_argument('--port', '-p', type=int, default=6000)
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
        server_cli = None
        try:
            server = RCEServer(args.host, args.port, args.debug)
            server_cli = ServerCLI(server)
            ServerCLI(server).cmdloop()
        except KeyboardInterrupt:
            server_cli.do_exit("")
            exit(0)
    else:
        print("Unknown mode: %s" % args.mode)
        exit(1)


if __name__ == '__main__':
    main()
