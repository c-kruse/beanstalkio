from beanstalkio import Client, CommandError
from unittest.mock import patch
import pytest

yaml_resp = "---\natt-a: 0\natt-b: 1\natt-c: Stringy\n"
yaml_dict_rep = {"att-a": 0, "att-b": 1, "att-c": "Stringy"}


@pytest.mark.parametrize(
    "method,cd_args",
    [
        ("stats", None),
        ("stats_tube", "t1"),
        ("put", "TestBody"),
        ("reserve", None),
        ("delete", "j1"),
        ("use", "t1"),
        ("watch", "t1"),
        ("watching", None),
        ("ignore", "t1"),
    ],
)
@pytest.mark.parametrize(
    "error_response",
    [("OUT_OF_MEMORY"), ("INTERNAL_ERROR"), ("BAD_FORMAT"), ("UNKNOWN_COMMAND")],
)
@patch("beanstalkio.client.Connection", autospec=True)
def test_errors(M_Conn, method, cd_args, error_response):
    args = ()
    if cd_args:
        args = cd_args.split(",")
    mock_conn = M_Conn("host", 123)
    mock_conn.read_line.side_effect = [error_response]
    C = Client("host", 123)
    with pytest.raises(CommandError) as excinfo:
        getattr(C, method)(*args)
    assert excinfo


@patch("beanstalkio.client.Connection", autospec=True)
def test_sync_ok(M_Conn):
    mock_conn = M_Conn("host", 123)
    mock_conn.read_line.side_effect = [f"OK {len(yaml_resp)}\r\n"]
    mock_conn.read_bytes.side_effect = [yaml_resp]
    C = Client("host", 123)
    body = C.stats()
    assert yaml_dict_rep == body


@pytest.mark.parametrize(
    "method,cd_args,response_line,response_body,expected",
    [
        ("stats", None, f"OK {len(yaml_resp)}\r\n", yaml_resp, yaml_dict_rep),
        ("stats_tube", "t1", f"OK {len(yaml_resp)}\r\n", yaml_resp, yaml_dict_rep),
        ("put", "TestBody", f"INSERTED 2", None, "2"),
        ("reserve", None, "RESERVED 2 430", "TestBody\r\n", ("TestBody", "2")),
        ("delete", "j1", "DELETED j1", None, None),
        ("use", "t1", "USING t1", None, "t1"),
        ("watch", "t1", "WATCHING 3", None, "3"),
        ("watching", None, f"OK {len(yaml_resp)}\r\n", yaml_resp, yaml_dict_rep),
        ("ignore", "t1", "IGNORED t1\r\n", Exception, "t1"),
    ],
)
@patch("beanstalkio.client.Connection", autospec=True)
def test_success(M_Conn, method, cd_args, response_line, response_body, expected):
    args = ()
    if cd_args:
        args = cd_args.split(",")
    mock_conn = M_Conn("host", 123)
    mock_conn.read_line.side_effect = [response_line]
    mock_conn.read_bytes.side_effect = [response_body]
    C = Client("host", 123)
    resp = getattr(C, method)(*args)
    assert resp == expected


@patch("beanstalkio.client.Connection", autospec=True)
def test_close(M_Conn):
    C = Client("Host", 123)
    C.disconnect()
    M_Conn.assert_called_with("Host", 123)
    M_Conn.return_value.close.assert_called_once()
