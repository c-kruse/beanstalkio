import yaml
from beanstalkio.connection import Connection


class Client:
    def __init__(self, host, port):
        self.connection = Connection(host, port)

    def _send_command(self, command):
        self.connection.write(command)

    def _read_server_response(self):
        line = self.connection.read_line()
        return line.split()

    def _get_response_with_status(self):
        response = self._read_server_response()
        return response[0]

    def _get_response_with_result(self):
        response = self._read_server_response()
        status = response.pop(0)
        if response:
            result = response.pop(0)
            return result, status
        return None, status

    def _get_response_with_body(self):
        body = status = None
        response = self._read_server_response()
        status = response.pop(0)
        if response:
            length = int(response.pop(0))
            body = self.connection.read_bytes(length + 2)
        return body, status

    def _get_response_with_yaml_body(self):
        body, status = self._get_response_with_body()
        if body:
            parsed = yaml.load(body, Loader=yaml.SafeLoader)
            return parsed, status
        return None, status

    def _get_response_complex(self):
        status = result = body = None
        response = self._read_server_response()
        status = response.pop(0)
        if response:
            result = response.pop(0)
        if response:
            length = int(response.pop(0))
            body = self.connection.read_bytes(length + 2)[:-2]
        return body, result, status

    def stats(self):
        self._send_command("stats\r\n")
        body, status = self._get_response_with_yaml_body()
        return body, status

    def strrrats(self):
        self._send_command("starrrrrts\r\n")
        body, status = self._get_response_with_yaml_body()
        return body, status

    def stats_tube(self, tube: str):
        self._send_command(f"stats-tube {tube}\r\n")
        body, status = self._get_response_with_yaml_body()
        return body, status

    def put(self, body: str, priority=2 ** 31, delay=0, ttr=120):
        command = f"put 1 0 120 {len(body)}\r\n{body}\r\n"
        self._send_command(command)
        results, status = self._get_response_with_result()
        return results, status

    def reserve(self):
        self._send_command("reserve\r\n")
        body, result, status = self._get_response_complex()
        return body, result, status

    def delete(self, job_id):
        self._send_command(f"delete {job_id}\r\n")
        return self._get_response_with_status()

    def use(self, tube):
        self._send_command(f"use {tube}\r\n")
        result, status = self._get_response_with_result()
        return result, status

    def watch(self, tube):
        self._send_command(f"watch {tube}\r\n")
        result, status = self._get_response_with_result()
        return result, status

    def watching(self):
        self._send_command(f"list-tubes-watched\r\n")
        body, status = self._get_response_with_yaml_body()
        return body, status

    def ignore(self, tube):
        self._send_command(f"ignore {tube}\r\n")
        result, status = self._get_response_with_result()
        return result, status
