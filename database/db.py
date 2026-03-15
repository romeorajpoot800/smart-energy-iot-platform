import sqlite3
from datetime import datetime

DB_NAME = "database/energy.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


# -------------------------
# USERS TABLE
# -------------------------

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            voltage REAL,
            current REAL,
            energy REAL,
            predicted_power REAL,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_default_user():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "1234")
        )
        conn.commit()

    conn.close()


def validate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()

    return user is not None


# -------------------------
# LOGS TABLE
# -------------------------

def insert_log(voltage, current, energy, predicted_power, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs 
        (timestamp, voltage, current, energy, predicted_power, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        voltage,
        current,
        energy,
        predicted_power,
        status
    ))

    conn.commit()
    conn.close()


def fetch_logs(limit=100):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM logs ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows