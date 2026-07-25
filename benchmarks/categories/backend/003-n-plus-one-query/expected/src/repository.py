class OrderRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_users_with_orders(self, user_ids):
        result = {uid: [] for uid in user_ids}

        if not user_ids:
            return result

        placeholders = ",".join("?" for _ in user_ids)
        query = (
            "SELECT user_id, order_id, total FROM orders "
            f"WHERE user_id IN ({placeholders})"
        )

        self.cursor.execute(query, user_ids)
        rows = self.cursor.fetchall()

        for row in rows:
            uid = row["user_id"]
            if uid in result:
                result[uid].append(dict(row))

        return result
