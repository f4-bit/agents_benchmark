import threading


class Buffer:
    """A bounded buffer with broken condition-variable usage."""

    def __init__(self, size):
        self.size = size
        self.items = []
        self.mutex = threading.Lock()
        self.not_full = threading.Condition(self.mutex)
        self.not_empty = threading.Condition(self.mutex)

    def put(self, item):
        with self.not_full:
            while len(self.items) >= self.size:
                self.not_full.wait()
            self.items.append(item)
        # Bug: notify the wrong condition and outside the lock.
        self.not_full.notify()

    def get(self):
        with self.not_empty:
            while len(self.items) == 0:
                self.not_empty.wait()
            item = self.items.pop(0)
        # Bug: notify the wrong condition and outside the lock.
        self.not_empty.notify()
        return item


def produce(buffer, count):
    for i in range(count):
        buffer.put(i)


def consume(buffer, count):
    return [buffer.get() for _ in range(count)]


def run_producer_consumer(count=20):
    """Run one producer and one consumer through a bounded buffer.

    Returns a tuple (consumed_items, alive_flags). With the correct
    implementation, all items are consumed and both threads finish.
    """
    buffer = Buffer(size=5)
    consumed = []

    def consumer_task():
        consumed.extend(consume(buffer, count))

    producer = threading.Thread(target=produce, args=(buffer, count))
    consumer = threading.Thread(target=consumer_task)
    producer.daemon = True
    consumer.daemon = True

    producer.start()
    consumer.start()

    producer.join(timeout=3.0)
    consumer.join(timeout=3.0)

    alive = (producer.is_alive(), consumer.is_alive())
    return consumed[:], alive


if __name__ == "__main__":
    print(run_producer_consumer())
