# import
import cmd

from src.server.rce_server import RCEServer


class CLI(cmd.Cmd):
    def __init__(self, rce_server: RCEServer):
        super().__init__()
        self.prompt = ">> "
        self.intro = "RCE CLI\nType help or ? to list commands."
        self.rce_server = rce_server

    def do_help(self, command: str): ...

    def do_disconnect(self, command: str): ...

    def do_inject(self, command: str): ...

    def do_execute(self, command: str): ...

    def do_exit(self, command: str): ...
