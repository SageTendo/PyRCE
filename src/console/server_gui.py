import tkinter as tk
from datetime import datetime
from enum import Enum

from src.core.message import MessageType, Message
from src.core.observer import RCEEventObserver
from src.server.rce_server import RCEServer


class ServerGUI(RCEEventObserver):
    class TextColors(Enum):
        FORREST_GREEN = "forestgreen"
        DIM_GRAY = "dimgray"
        RED = "red4"
        PURPLE = "mediumorchid"
        BLACK = "black"

    def __init__(self, server: RCEServer):
        self.server = server
        self.server.add_observer(self)

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
                                             text="Start", command=self.start_server, font=('', 12, 'bold'))
        self.server_stop_button = tk.Button(self.header,
                                            text="Stop", command=self.stop_server, font=('', 12, 'bold'))
        self.message_input = tk.Entry(self.content_bottom, font=('', 12, 'bold'))
        self.send_message_button = tk.Button(self.content_bottom,
                                             text="Send Message", command=self.send_message, font=('', 12, 'bold'))

        # Outputs
        self.messages_area = tk.Text(self.content_top, font=('', 12, 'bold'))
        self.clients_list = tk.Listbox(self.content_top, font=('', 12, 'bold'))

    def close_windows(self):
        if self.server.is_running():
            self.server.stop()
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

    def start_server(self):
        """
        Starts the RCE server
        """
        if self.server.start():
            self.server_start_button["state"] = "disabled"
            self.server_stop_button["state"] = "normal"

    def stop_server(self):
        """
        Stops the RCE server
        """
        if self.server.stop():
            self.server_start_button["state"] = "normal"
            self.server_stop_button["state"] = "disabled"

    def send_message(self):
        """
        Sends a message to all connected clients
        """
        message_string = self.message_input.get()
        message = Message(message_type=MessageType.CMD, data=message_string.encode())
        self.server.broadcast_message(message)

        message_format = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Server: {message_string}"
        self.__update_message_area(message_format, color=ServerGUI.TextColors.BLACK)
        self.message_input.delete(0, tk.END)

    def __update_message_area(self, message: str, color: TextColors = TextColors.DIM_GRAY):
        """
        Updates the message area with a new message
        :param message: The message to be added
        :param color: The color to be used to display the message
        """
        self.messages_area.config(state='normal')
        self.messages_area.tag_config(color.value, foreground=color.value)
        self.messages_area.insert(tk.END, message + '\n', color.value)
        self.messages_area.config(state='disabled')

    def on_connect(self, client_address: str):
        msg_format = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {client_address} connected"
        self.__update_message_area(msg_format, color=ServerGUI.TextColors.FORREST_GREEN)
        self.clients_list.insert(tk.END, client_address)
        self.clients_list.update()

    def on_disconnect(self, client_address: str):
        msg_format = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {client_address} disconnected"
        self.__update_message_area(msg_format, color=ServerGUI.TextColors.FORREST_GREEN)

        for i in range(self.clients_list.size()):
            if self.clients_list.get(i) == client_address:
                self.clients_list.delete(i)
                break
        self.clients_list.update()

    def on_message(self, sender: str, message: str):
        message_format = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {sender}: {message}"
        self.__update_message_area(message_format, color=ServerGUI.TextColors.DIM_GRAY)

    def on_error(self, error: str, prefix=""):
        error_format = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {error}"
        self.__update_message_area(error_format, color=ServerGUI.TextColors.RED)

    def on_info(self, message: str, prefix=""):
        info_format = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}"
        self.__update_message_area(info_format, color=ServerGUI.TextColors.FORREST_GREEN)

    def on_debug(self, message: str, prefix=""):
        debug_format = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}"
        self.__update_message_area(debug_format, color=ServerGUI.TextColors.PURPLE)


if __name__ == "__main__":
    gui = ServerGUI(RCEServer("localhost", 6000))
    gui.build()
