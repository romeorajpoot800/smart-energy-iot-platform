"""
database/db_handler.py
SQLiteHandler class for managing the energy readings database.
Uses sqlite3 only (no SQLAlchemy).
DB path: database/energy.db
"""

import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join("database", "energy.db")


class SQLiteHandler:
    """Handles all SQLite database operations for energy readings."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connect(self):
        """Create and return a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Create the readings table if it does not exist."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mac TEXT NOT NULL,
                voltage REAL NOT NULL,
                current REAL NOT NULL,
                predicted_power REAL NOT NULL,
                anomaly INTEGER NOT NULL DEFAULT 0,
                energy_kwh REAL DEFAULT 0,
                relay_state INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def insert_reading(self, mac: str, voltage: float, current: float,
                       predicted_power: float, anomaly: bool,
                       energy_kwh: float = 0, relay_state: int = 0):
        """Insert a single reading into the database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO readings (mac, voltage, current, predicted_power, anomaly, energy_kwh, relay_state, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mac,
            voltage,
            current,
            predicted_power,
            1 if anomaly else 0,
            energy_kwh or 0,
            1 if relay_state else 0,
            datetime.now().isoformat(),
        ))
        conn.commit()
        conn.close()

    def get_last_n(self, n: int = 50) -> list:
        """Return the last n readings as a list of dicts."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, mac, voltage, current, predicted_power, anomaly, timestamp
            FROM readings
            ORDER BY id DESC
            LIMIT ?
        """, (n,))
        rows = cursor.fetchall()
        conn.close()

        # Convert Row objects to dicts and return in chronological order
        results = []
        for row in reversed(rows):
            results.append({
                "id": row["id"],
                "mac": row["mac"],
                "voltage": row["voltage"],
                "current": row["current"],
                "predicted_power": row["predicted_power"],
                "anomaly": bool(row["anomaly"]),
                "timestamp": row["timestamp"],
            })
        return results
