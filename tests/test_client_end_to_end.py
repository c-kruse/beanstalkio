from beanstalkio import Client, BeanstalkdConnection
import pytest


@pytest.mark.integration
def test_end_to_end():
    C = Client("127.0.0.1", 11300)
    before = C.stats()
    for i in range(10):
        tube = f"tube-{i}"
        C.use(tube)
        for c in range(10):
            C.put(f"Msg-{i}-{c}")
        watching = C.watching()
        C.watch(tube)
        for w in [w for w in watching if not w == tube]:
            C.ignore(w)
        for c in range(10):
            body, j_id = C.reserve()
            assert body == f"Msg-{i}-{c}"
            C.delete(j_id)
    after = C.stats()
    assert after.get("total-jobs") == before.get("total-jobs") + 100


@pytest.mark.integration
def test_connection_error():
    # Invalid IP Forces EAI_NONAME
    C = Client("999.0.999.0", 43594)
    with pytest.raises(BeanstalkdConnection):
        C.stats()


@pytest.mark.integration
def test_connection_close():
    C = Client("127.0.0.1", 11300)
    before = C.stats().get('total-connections')
    C.disconnect()
    after = C.stats().get('total-connections')
    assert before < after
