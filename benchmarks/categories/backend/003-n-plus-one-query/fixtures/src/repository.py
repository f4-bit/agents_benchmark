class OrderRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_users_with_orders(self, user_ids):
        result = {}
        for uid in user_ids:
            self.cursor.execute(
                "SELECT user_id, order_id, total FROM orders WHERE user_id = ?",
                (uid,),
            )
            rows = self.cursor.fetchall()
            result[uid] = [dict(row) for row in rows]
        return result
