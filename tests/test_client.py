from beanstalkio import client
from unittest.mock import patch
import pytest

yaml_resp = "---\natt-a: 0\natt-b: 1\natt-c: Stringy\n"
yaml_dict_rep = {"att-a": 0, "att-b": 1, "att-c": "Stringy"}


@pytest.mark.parametrize(
    "read_line,read_bytes,expected_body,expected_status",
    [
        pytest.param(
            f"OK {len(yaml_resp)}\r\n",
            yaml_resp,
            yaml_dict_rep,
            "OK",
            id="Valid-Response",
        ),
        pytest.param(
            f"OUT_OF_MEMORY\r\n",
            Exception,
            None,
            "OUT_OF_MEMORY",
            id="Error-Response"
        ),
    ],
)
@patch("beanstalkio.client.Connection", autospec=True)
def test_sync_ok(M_Conn, read_line, read_bytes, expected_body, expected_status):
    mock_conn = M_Conn("host", 123)
    mock_conn.read_line.side_effect = [read_line]
    mock_conn.read_bytes.side_effect = [read_bytes]
    C = client.Client("", -1)
    body, status = C.stats()
    assert expected_body == body
    assert expected_status == status
