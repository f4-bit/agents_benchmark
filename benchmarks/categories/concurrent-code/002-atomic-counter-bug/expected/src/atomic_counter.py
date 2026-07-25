import threading


class Counter:
    """A thread-safe shared counter incremented by multiple threads."""

    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.value += 1


def run_threads(num_threads=100, increments_per_thread=1000):
    """Increment a shared counter concurrently and return the final value."""
    counter = Counter()
    threads = []

    def worker():
        for _ in range(increments_per_thread):
            counter.increment()

    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return counter.value


if __name__ == "__main__":
    print(run_threads())
