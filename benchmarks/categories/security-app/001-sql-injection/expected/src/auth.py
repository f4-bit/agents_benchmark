import sqlite3


def _init_db():
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'secret'))
    conn.commit()
    return conn


_conn = _init_db()


def authenticate(username, password):
    cur = _conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    return cur.fetchone() is not None
