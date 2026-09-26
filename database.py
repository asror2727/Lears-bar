import sqlite3

from config import STARTING_DOLLARS, STARTING_DIAMONDS

DB_PATH = "game.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            dollars INTEGER DEFAULT 0,
            diamonds INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            games INTEGER DEFAULT 0,
            rating INTEGER DEFAULT 1000,
            banned INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


def get_or_create_user(user_id, username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO users (user_id, username, dollars, diamonds) VALUES (?, ?, ?, ?)",
            (user_id, username, STARTING_DOLLARS, STARTING_DIAMONDS),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    else:
        conn.execute("UPDATE users SET username=? WHERE user_id=?", (username, user_id))
        conn.commit()
    conn.close()
    return dict(row)


def get_user(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_balance(user_id, dollars=0, diamonds=0):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET dollars = dollars + ?, diamonds = diamonds + ? WHERE user_id=?",
        (dollars, diamonds, user_id),
    )
    conn.commit()
    conn.close()


def add_result(user_id, win: bool):
    conn = get_conn()
    if win:
        conn.execute(
            "UPDATE users SET games = games + 1, wins = wins + 1, rating = rating + 15 WHERE user_id=?",
            (user_id,),
        )
    else:
        conn.execute(
            "UPDATE users SET games = games + 1, rating = MAX(rating - 5, 0) WHERE user_id=?",
            (user_id,),
        )
    conn.commit()
    conn.close()


def top_players(limit=10):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users ORDER BY rating DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_ban(user_id, banned: bool):
    conn = get_conn()
    conn.execute("UPDATE users SET banned=? WHERE user_id=?", (1 if banned else 0, user_id))
    conn.commit()
    conn.close()


def all_user_ids():
    conn = get_conn()
    rows = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [r["user_id"] for r in rows]
