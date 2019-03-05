import yaml
import socket
from functools import wraps


class Job():
    pass


class Client():
    def __init__(self, host, port):
        self.connection = Connection(host, port)

    def _send_command(self, command: str):
        self.connection.write(command)

    def _read_response(self, with_id=False, with_body=True):
        result = {}
        line = self.connection.read_line()
        response = line.split()
        status = response.pop(0)
        result['status'] = status
        if with_id and response:
            result['id'] = response.pop(0)
        if with_body and response:
            length = int(response.pop(0))
            body_s = self.connection.read_bytes(length + 2)
            body = yaml.load(body_s)
            result['body'] = body
        return result

    def stats(self):
        self._send_command('stats\r\n')
        response = self._read_response()
        return response

    def strrrats(self):
        self._send_command('strrrats\r\n')
        response = self._read_response()
        return response

    def stats_tube(self, tube: str):
        self._send_command(f'stats-tube {tube}\r\n')
        response = self._read_response()
        return response

    def put(self, body: str):
        cmd = f'put 1 0 120 {len(body)}\r\n{body}\r\n'
        self._send_command(cmd)
        response = self._read_response(with_id=True, with_body=False)
        return response

    def reserve(self):
        self._send_command('reserve\r\n')
        response = self._read_response(with_id=True, with_body=True)
        return response

    def delete(self, job_id):
        self._send_command(f'delete {job_id}\r\n')
        response = self._read_response(with_id=False, with_body=False)
        return response

    def use(self, tube):
        self._send_command(f'use {tube}\r\n')
        response = self._read_response(with_id=True, with_body=False)
        return response

    def watch(self, tube):
        self._send_command(f'watch {tube}\r\n')
        response = self._read_response(with_id=True, with_body=False)
        return response

    def watching(self):
        self._send_command(f'list-tubes-watched\r\n')
        response = self._read_response()
        return response

    def ignore(self, tube):
        self._send_command(f'ignore {tube}\r\n')
        response = self._read_response(with_id=True, with_body=False)
        return response


def _with_connection(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if not self._socket:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            self._socket = sock
            self._socket_file = sock.makefile('rb')
        return fn(self, *args, **kwargs)
    return wrapper


class Connection():
    def __init__(self, host, port):
        self.encoding = 'ascii'
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
        pass
