import pytest
from atomic_counter import run_threads


def test_counter_reaches_exact_total():
    result = run_threads(num_threads=100, increments_per_thread=1000)
    assert result == 100000, f"Expected 100000, got {result}"
