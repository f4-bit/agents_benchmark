import threading


class Counter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self, n=1):
        for _ in range(n):
            with self._lock:
                current = self.value
                self.value = current + 1
