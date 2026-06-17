"""
Smart Energy Monitoring System - Database Module
SQLite database initialization and operations
"""

import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "database/energy.db"


def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    """Create all database tables"""
    conn = get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        created_at TEXT
    )
    """)

    # Devices table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        device_name TEXT,
        mac_address TEXT UNIQUE,
        last_seen TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Energy logs table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS energy_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac_address TEXT,
        voltage REAL,
        current REAL,
        power REAL,
        energy_kwh REAL DEFAULT 0,
        relay_state INTEGER DEFAULT 0,
        timestamp TEXT
    )
    """)

    # Alerts table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mac_address TEXT,
        alert_type TEXT,
        message TEXT,
        value REAL,
        threshold REAL,
        created_at TEXT,
        acknowledged INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

    # Run migrations
    run_migrations()


def run_migrations():
    """Add missing columns to existing tables"""
    conn = get_connection()
    cur = conn.cursor()

    # Add last_seen column to devices if it doesn't exist
    try:
        cur.execute("ALTER TABLE devices ADD COLUMN last_seen TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Add energy_kwh column to energy_logs if it doesn't exist
    try:
        cur.execute("ALTER TABLE energy_logs ADD COLUMN energy_kwh REAL DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Add relay_state column to energy_logs if it doesn't exist
    try:
        cur.execute("ALTER TABLE energy_logs ADD COLUMN relay_state INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()


def create_admin():
    """Create default admin user"""
    conn = get_connection()
    cur = conn.cursor()

    email = "admin@energy.com"
    password = hash_password("admin123")

    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO users(name, email, password, role, created_at)
        VALUES(?, ?, ?, ?, ?)
        """, ("Admin", email, password, "admin", datetime.now()))

    conn.commit()
    conn.close()


# ==================== User Operations ====================

def signup_user(name, email, password):
    """Register a new user"""
    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    try:
        cur.execute("""
        INSERT INTO users(name, email, password, role, created_at)
        VALUES(?, ?, ?, 'user', ?)
        """, (name, email, hashed, datetime.now()))

        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False


def login_user(email, password):
    """Authenticate user"""
    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    cur.execute("""
    SELECT id, name, email, role FROM users
    WHERE email=? AND password=?
    """, (email, hashed))

    user = cur.fetchone()
    conn.close()

    return user


def get_all_users():
    """Get all users (admin only)"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, email, role, created_at FROM users")
    data = cur.fetchall()
    conn.close()

    return data


# ==================== Device Operations ====================

def add_device(user_id, name, mac):
    """Add a new device"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO devices(user_id, device_name, mac_address, created_at)
        VALUES(?, ?, ?, ?)
        """, (user_id, name, mac, datetime.now()))

        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False


def get_user_devices(user_id):
    """Get all devices for a user"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT device_name, mac_address, last_seen
    FROM devices
    WHERE user_id=?
    """, (user_id,))

    data = cur.fetchall()
    conn.close()

    return data


def get_all_devices():
    """Get all devices (admin only)"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT d.id, d.device_name, d.mac_address, u.name, d.created_at
    FROM devices d
    JOIN users u ON d.user_id = u.id
    """)

    data = cur.fetchall()
    conn.close()

    return data


def remove_device(mac):
    """Remove a device"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM devices WHERE mac_address=?", (mac,))
    conn.commit()
    conn.close()


def update_last_seen(mac):
    """Update device last seen timestamp"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE devices SET last_seen=? WHERE mac_address=?
    """, (datetime.now(), mac))

    conn.commit()
    conn.close()


def rename_device(mac, new_name):
    """Rename a device"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE devices SET device_name=? WHERE mac_address=?
    """, (new_name, mac))

    conn.commit()
    conn.close()


def get_device_status(mac):
    """
    Get device online/offline status
    
    Returns:
        dict with device info and status
        If last_seen > 60 seconds → offline
        If last_seen ≤ 60 seconds → online
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, user_id, device_name, mac_address, last_seen, created_at
    FROM devices WHERE mac_address=?
    """, (mac,))

    device = cur.fetchone()
    conn.close()

    if not device:
        return None

    # Determine online/offline status
    status = "offline"
    if device[4]:  # last_seen exists
        try:
            last_seen_time = datetime.strptime(device[4], "%Y-%m-%d %H:%M:%S.%f")
            time_diff = (datetime.now() - last_seen_time).total_seconds()
            if time_diff <= 60:  # 60 seconds threshold
                status = "online"
        except:
            # Try alternative format
            try:
                last_seen_time = datetime.strptime(device[4], "%Y-%m-%d %H:%M:%S")
                time_diff = (datetime.now() - last_seen_time).total_seconds()
                if time_diff <= 60:
                    status = "online"
            except:
                pass

    return {
        "id": device[0],
        "user_id": device[1],
        "device_name": device[2],
        "mac_address": device[3],
        "last_seen": device[4],
        "created_at": device[5],
        "status": status
    }


def get_device_by_mac(mac):
    """Get device by MAC address"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, user_id, device_name, mac_address, last_seen, created_at
    FROM devices WHERE mac_address=?
    """, (mac,))

    device = cur.fetchone()
    conn.close()

    return device


# ==================== Energy Log Operations ====================

def insert_energy_log(mac, voltage, current, power, energy_kwh=0, relay_state=0):
    """Insert energy reading (supports energy_kwh and relay_state)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO energy_logs(mac_address, voltage, current, power, energy_kwh, relay_state, timestamp)
    VALUES(?, ?, ?, ?, ?, ?, ?)
    """, (mac, voltage, current, power, energy_kwh or 0, 1 if relay_state else 0, datetime.now()))

    conn.commit()
    conn.close()


def get_device_logs(mac, limit=100):
    """Get energy logs for a device"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT voltage, current, power, timestamp
    FROM energy_logs
    WHERE mac_address=?
    ORDER BY id DESC
    LIMIT ?
    """, (mac, limit))

    data = cur.fetchall()
    conn.close()

    return data


def get_device_logs_by_date(mac, start_date, end_date):
    """Get energy logs by date range"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT voltage, current, power, timestamp
    FROM energy_logs
    WHERE mac_address=? AND timestamp BETWEEN ? AND ?
    ORDER BY id DESC
    """, (mac, start_date, end_date))

    data = cur.fetchall()
    conn.close()

    return data


def get_total_energy_stats():
    """Get platform-wide energy statistics"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        COUNT(DISTINCT mac_address) as device_count,
        COUNT(*) as total_readings,
        AVG(power) as avg_power,
        MAX(power) as max_power,
        MIN(power) as min_power
    FROM energy_logs
    """)

    data = cur.fetchone()
    conn.close()

    return data


def get_device_last_seen(mac):
    """Get last seen timestamp for a device"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT timestamp FROM energy_logs
    WHERE mac_address=?
    ORDER BY id DESC
    LIMIT 1
    """, (mac,))

    data = cur.fetchone()
    conn.close()

    return data[0] if data else None


# ==================== Alert Operations ====================

def insert_alert(user_id, mac, alert_type, message, value, threshold):
    """Insert a new alert"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO alerts(user_id, mac_address, alert_type, message, value, threshold, created_at)
    VALUES(?, ?, ?, ?, ?, ?, ?)
    """, (user_id, mac, alert_type, message, value, threshold, datetime.now()))

    conn.commit()
    conn.close()


def get_user_alerts(user_id):
    """Get alerts for a user"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, mac_address, alert_type, message, value, threshold, created_at, acknowledged
    FROM alerts
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 50
    """, (user_id,))

    data = cur.fetchall()
    conn.close()

    return data


def acknowledge_alert(alert_id):
    """Mark alert as acknowledged"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE alerts SET acknowledged=1 WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()


def get_unacknowledged_alerts(user_id):
    """Get count of unacknowledged alerts"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*) FROM alerts
    WHERE user_id=? AND acknowledged=0
    """, (user_id,))

    data = cur.fetchone()
    conn.close()

    return data[0] if data else 0


if __name__ == "__main__":
    create_tables()
    create_admin()
    print("Database initialized successfully!")
