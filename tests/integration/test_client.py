from beanstalkio import client


def test_client():
    C = client.Client('127.0.0.1', 11300)
    s1 = C.stats()
    print(s1)
    for i in range(10):
        tube = f'tube-{i}'
        print(C.use(tube))
        for c in range(10):
            print(C.put(f'Msg-{i}-{c}'))
        watching = C.watching()['body']
        for w in watching:
            print(C.ignore(w))
        print(C.watch(tube))
        for c in range(10):
            j = C.reserve()
            print(j)
            print(C.delete(j.get('id')))
        print(C.stats_tube(tube))
    s2 = C.stats()
    print(s2)
    assert s2