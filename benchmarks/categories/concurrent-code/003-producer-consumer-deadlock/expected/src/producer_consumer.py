import threading


class Buffer:
    """A bounded buffer using a single condition variable correctly."""

    def __init__(self, size):
        self.size = size
        self.items = []
        self.cond = threading.Condition()

    def put(self, item):
        with self.cond:
            while len(self.items) >= self.size:
                self.cond.wait()
            self.items.append(item)
            self.cond.notify()

    def get(self):
        with self.cond:
            while len(self.items) == 0:
                self.cond.wait()
            item = self.items.pop(0)
            self.cond.notify()
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
