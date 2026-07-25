import pytest
from producer_consumer import run_producer_consumer


@pytest.mark.timeout(5)
def test_all_items_consumed_no_deadlock():
    consumed, alive = run_producer_consumer(count=20)
    assert not any(alive), "Producer or consumer thread deadlocked"
    assert consumed == list(range(20)), (
        f"Expected items 0..19 in order, got {consumed}"
    )
