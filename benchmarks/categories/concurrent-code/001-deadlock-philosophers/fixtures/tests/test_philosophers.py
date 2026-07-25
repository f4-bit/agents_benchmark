import pytest
from philosophers import run_simulation, NUM_PHILOSOPHERS


@pytest.mark.timeout(5)
def test_philosophers_complete_without_deadlock():
    meals, alive = run_simulation()
    assert not any(alive), "Deadlock detected: some philosopher threads did not finish"
    assert sum(meals) == NUM_PHILOSOPHERS, (
        f"Expected each philosopher to eat once, got {meals}"
    )
    assert all(m == 1 for m in meals), (
        f"Each philosopher should eat exactly once, got {meals}"
    )
