from unittest.mock import patch
from beanstalkio import client


@patch('beanstalkio.client.Connection', autospec=True)
def test_sync_ok(M_Conn):
    resp = '''---\natt-a: 0\natt-b: 1\natt-c: Stringy\n'''
    mock_conn = M_Conn.return_value
    mock_conn.read_line.side_effect = [f'OK {len(resp)}']
    mock_conn.read_bytes.side_effect = [resp]
    C = client.Client('', -1)
    resp = C.stats()
    assert resp['status'] == "OK"
    assert 'id' not in resp
    assert resp['body'] == {'att-a': 0, 'att-b': 1, 'att-c': 'Stringy'}


@patch('beanstalkio.client.Connection', autospec=True)
def test_sync_error(M_Conn):
    mock_conn = M_Conn.return_value
    mock_conn.read_line.side_effect = ['OUT_OF_MEMORY']
    mock_conn.read_bytes.side_effect = [Exception]
    C = client.Client('', -1)
    resp = C.stats()
    assert resp['status'] == "OUT_OF_MEMORY"
    assert 'id' not in resp
    assert 'body' not in resp
