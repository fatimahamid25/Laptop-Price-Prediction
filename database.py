
import sqlite3
import hashlib
import os


DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "users.db"
)


def create_table():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL DEFAULT '',
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "username" not in columns:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN username TEXT NOT NULL DEFAULT ''
        """)

    conn.commit()
    conn.close()


def signup(username, email, password):

    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False

    hashed_password = hashlib.sha256(
        password.encode()
    ).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, hashed_password))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def login(email, password):

    email = email.strip().lower()

    hashed_password = hashlib.sha256(
        password.encode()
    ).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE email = ? AND password = ?
    """, (email, hashed_password))

    user = cursor.fetchone()

    conn.close()

    return user
