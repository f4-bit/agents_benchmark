import threading

import counter


def test_counter_thread_safety():
    c = counter.Counter()
    threads = []
    for _ in range(100):
        t = threading.Thread(target=c.increment, args=(1000,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    assert c.value == 100000
