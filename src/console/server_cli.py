import cmd
from pathlib import Path

from src.core.message import Message, MessageType
from src.server.rce_server import RCEServer


class ServerCLI(cmd.Cmd):
    def __init__(self, server: RCEServer):
        super().__init__()
        self.prompt = 'server> '
        self.server = server
        if not self.server.is_running():
            self.server.start()

    @staticmethod
    def __parse_args(arg):
        return arg.split(' ')

    def default(self, line):
        print('Unknown command: %s' % line)
        return 0

    def do_exit(self, line):
        self.server.stop()
        return True

    def do_start(self, line):
        if self.server.is_running():
            print("Server is already running")
            return

        if not self.server.start():
            print("Failed to start server")

    def do_stop(self, line):
        if not self.server.is_running():
            print("Server is not running")
            return

        if not self.server.stop():
            print("Failed to stop server")

    def do_inject(self, line):
        args = self.__parse_args(line)
        if len(args) < 2:
            print("Usage: inject <file>")
            return

        print(args)
        if args[0] != '-f' and args[0] != '--file':
            print("Usage: inject -f/--file <file>")
            return

        file = Path(args[1])
        if not file.exists():
            print(f"File {file} does not exist")
            return

        with open(file, 'rb') as f:
            self.server.broadcast_message(Message(message_type=MessageType.INJECT, data=f.read()))

    def do_execute(self, line):
        self.server.broadcast_message(Message(message_type=MessageType.EXECUTE, data=b''))
