import pytest
from repository import OrderRepository


class Row(dict):
    pass


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.execute_count = 0
        self.last_params = None

    def execute(self, query, params=None):
        self.execute_count += 1
        self.last_query = query
        self.last_params = params
        return self

    def fetchall(self):
        ids = self.last_params
        if ids is None:
            return []
        if isinstance(ids, tuple):
            ids = list(ids)
        if not isinstance(ids, list):
            ids = [ids]
        return [row for row in self.rows if row["user_id"] in ids]


def test_constant_number_of_queries():
    rows = [
        Row(user_id=1, order_id=101, total=10.0),
        Row(user_id=1, order_id=102, total=20.0),
        Row(user_id=2, order_id=201, total=15.0),
    ]
    cursor = FakeCursor(rows)
    repo = OrderRepository(cursor)
    result = repo.get_users_with_orders([1, 2, 3])

    assert cursor.execute_count == 1
    assert result == {
        1: [
            {"user_id": 1, "order_id": 101, "total": 10.0},
            {"user_id": 1, "order_id": 102, "total": 20.0},
        ],
        2: [{"user_id": 2, "order_id": 201, "total": 15.0}],
        3: [],
    }
