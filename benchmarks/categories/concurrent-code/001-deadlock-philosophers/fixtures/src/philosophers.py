import threading

NUM_PHILOSOPHERS = 5
forks = [threading.Lock() for _ in range(NUM_PHILOSOPHERS)]
meals_eaten = [0] * NUM_PHILOSOPHERS


def philosopher(index, start_barrier, hold_barrier):
    left = index
    right = (index + 1) % NUM_PHILOSOPHERS
    start_barrier.wait()
    forks[left].acquire()
    # At this point every philosopher holds its left fork, creating the
    # classic circular wait. The next barrier guarantees all are stuck here
    # before they try to acquire the right fork.
    hold_barrier.wait()
    forks[right].acquire()
    meals_eaten[index] += 1
    forks[right].release()
    forks[left].release()


def run_simulation():
    """Run the dining philosophers simulation once per philosopher.

    Returns a tuple (meals_eaten, alive_flags). When there is no deadlock,
    every philosopher eats exactly once and no thread remains alive.
    """
    meals_eaten[:] = [0] * NUM_PHILOSOPHERS
    start_barrier = threading.Barrier(NUM_PHILOSOPHERS)
    hold_barrier = threading.Barrier(NUM_PHILOSOPHERS)
    threads = []
    for i in range(NUM_PHILOSOPHERS):
        t = threading.Thread(
            target=philosopher, args=(i, start_barrier, hold_barrier)
        )
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join(timeout=0.3)

    alive = [t.is_alive() for t in threads]
    return meals_eaten[:], alive


if __name__ == "__main__":
    print(run_simulation())
