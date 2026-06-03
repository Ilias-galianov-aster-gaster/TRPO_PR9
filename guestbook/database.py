import sqlite3
from datetime import date


DATABASE = 'guestbook.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def add_test_messages():
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO messages (name, message, created_at) VALUES (?, ?, ?)',
        ('Анна', 'Отличный сайт!', '2026-05-28')
    )
    conn.execute(
        'INSERT INTO messages (name, message, created_at) VALUES (?, ?, ?)', 
        ('Иван', 'Всем привет', '2026-05-27'))
    conn.commit()
    conn.close()


def get_all_messages():
    conn = get_db_connection()
    messages = conn.execute(
        'SELECT * FROM messages ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return messages