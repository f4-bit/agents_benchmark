import threading

NUM_PHILOSOPHERS = 5
forks = [threading.Lock() for _ in range(NUM_PHILOSOPHERS)]
meals_eaten = [0] * NUM_PHILOSOPHERS


def philosopher(index, barrier):
    left = index
    right = (index + 1) % NUM_PHILOSOPHERS
    # Enforce a global lock order to prevent circular wait.
    first, second = sorted((left, right))
    barrier.wait()
    with forks[first]:
        with forks[second]:
            meals_eaten[index] += 1


def run_simulation():
    """Run the dining philosophers simulation once per philosopher.

    Returns a tuple (meals_eaten, alive_flags). When there is no deadlock,
    every philosopher eats exactly once and no thread remains alive.
    """
    meals_eaten[:] = [0] * NUM_PHILOSOPHERS
    barrier = threading.Barrier(NUM_PHILOSOPHERS)
    threads = []
    for i in range(NUM_PHILOSOPHERS):
        t = threading.Thread(target=philosopher, args=(i, barrier))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join(timeout=0.3)

    alive = [t.is_alive() for t in threads]
    return meals_eaten[:], alive


if __name__ == "__main__":
    print(run_simulation())
