from beanstalkio import client
import pytest


@pytest.mark.integration
def test_end_to_end():
    C = client.Client("127.0.0.1", 11300)
    before, _ = C.stats()
    for i in range(10):
        tube = f"tube-{i}"
        C.use(tube)
        for c in range(10):
            C.put(f"Msg-{i}-{c}")
        watching, _ = C.watching()
        C.watch(tube)
        for w in [w for w in watching if not w == tube]:
            C.ignore(w)
        for c in range(10):
            body, j_id, status = C.reserve()
            assert body == f"Msg-{i}-{c}"
            assert C.delete(j_id) == "DELETED"
    after, _ = C.stats()
    assert after.get("total-jobs") == before.get("total-jobs") + 100
