class MessageTypeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NoSuchFileError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class FileWriteError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class FileReadError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
