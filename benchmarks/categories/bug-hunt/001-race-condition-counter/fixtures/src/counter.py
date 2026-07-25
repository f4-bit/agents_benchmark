import threading
import time


class Counter:
    def __init__(self):
        self.value = 0

    def increment(self, n=1):
        for _ in range(n):
            current = self.value
            # Yield the GIL between read and write so the race condition
            # reliably loses increments.
            time.sleep(0)
            self.value = current + 1
