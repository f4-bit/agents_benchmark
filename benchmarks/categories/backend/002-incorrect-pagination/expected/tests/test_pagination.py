import pytest
from pagination import paginate, total_pages


ITEMS = list(range(1, 11))


def test_first_page():
    assert paginate(ITEMS, 1, 3) == [1, 2, 3]


def test_second_page():
    assert paginate(ITEMS, 2, 3) == [4, 5, 6]


def test_last_partial_page():
    assert paginate(ITEMS, 4, 3) == [10]


def test_out_of_range_page_returns_empty():
    assert paginate(ITEMS, 5, 3) == []


def test_total_pages_accounts_for_leftovers_and_empty():
    assert total_pages(ITEMS, 3) == 4
    assert total_pages([], 3) == 0
    assert total_pages(ITEMS, 10) == 1
    assert total_pages(ITEMS, 11) == 1


def test_invalid_page_raises():
    with pytest.raises(ValueError):
        paginate(ITEMS, 0, 3)


def test_invalid_page_size_raises():
    with pytest.raises(ValueError):
        paginate(ITEMS, 1, 0)
