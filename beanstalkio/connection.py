import socket
from functools import wraps


def _with_connection(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if not self._socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            self._socket = sock
            self._socket_file = sock.makefile("rb")
        return fn(self, *args, **kwargs)

    return wrapper


class Connection:
    def __init__(self, host, port):
        self.encoding = "ascii"
        self.host = host
        self.port = port
        self._socket = None
        self._socket_file = None

    @_with_connection
    def write(self, message: str):
        return self._socket.sendall(message.encode(self.encoding))

    @_with_connection
    def read_bytes(self, size) -> bytes:
        return self._socket_file.read(size).decode(self.encoding)

    @_with_connection
    def read_line(self) -> bytes:
        return self._socket_file.readline().decode(self.encoding)

    def close(self):
        if self._socket:
            self._socket_file.close()
            self._socket.close()
            self._socket_file = None
            self._socket = None
            return True
        return False
