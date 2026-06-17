import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "database/energy.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        device_name TEXT,
        mac_address TEXT UNIQUE,
        last_seen TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor_logs(
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

    conn.commit()
    conn.close()

    # Run migrations to add missing columns
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

    conn.close()


def create_admin():

    conn = get_connection()
    cur = conn.cursor()

    email = "admin@energy.com"
    password = hash_password("admin123")

    cur.execute("SELECT * FROM users WHERE email=?", (email,))
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO users(name,email,password,role,created_at)
        VALUES(?,?,?,?,?)
        """, ("Admin", email, password, "admin", datetime.now()))

    conn.commit()
    conn.close()


def signup_user(name,email,password):

    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    try:
        cur.execute("""
        INSERT INTO users(name,email,password,role,created_at)
        VALUES(?,?,?,?,?)
        """,(name,email,hashed,"user",datetime.now()))

        conn.commit()
        conn.close()
        return True

    except:
        conn.close()
        return False


def login_user(email,password):

    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    cur.execute("""
    SELECT id,name,email,role FROM users
    WHERE email=? AND password=?
    """,(email,hashed))

    user = cur.fetchone()
    conn.close()

    return user


def add_device(user_id,name,mac):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
        INSERT INTO devices(user_id,device_name,mac_address,last_seen,created_at)
        VALUES(?,?,?,?,?)
        """,(user_id,name,mac,datetime.now(),datetime.now()))

        conn.commit()
        conn.close()
        return True

    except:
        conn.close()
        return False


def update_last_seen(mac):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE devices
    SET last_seen=?
    WHERE mac_address=?
    """,(datetime.now(),mac))

    conn.commit()
    conn.close()


def get_user_devices(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT device_name,mac_address,last_seen
    FROM devices
    WHERE user_id=?
    """,(user_id,))

    data = cur.fetchall()
    conn.close()

    return data


def remove_device(mac):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM devices WHERE mac_address=?", (mac,))
    conn.commit()
    conn.close()


def insert_sensor(mac,voltage,current,power,energy_kwh=0,relay_state=0):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO sensor_logs(mac_address,voltage,current,power,energy_kwh,relay_state,timestamp)
    VALUES(?,?,?,?,?,?,?)
    """,(mac,voltage,current,power,energy_kwh or 0,1 if relay_state else 0,datetime.now()))

    conn.commit()
    conn.close()


def get_device_logs(mac):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT voltage,current,power,timestamp
    FROM sensor_logs
    WHERE mac_address=?
    ORDER BY id DESC
    LIMIT 100
    """,(mac,))

    data = cur.fetchall()
    conn.close()

    return data


def get_device_logs_by_date(mac, start_date, end_date):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT voltage,current,power,timestamp
    FROM sensor_logs
    WHERE mac_address=? AND timestamp BETWEEN ? AND ?
    ORDER BY id DESC
    """, (mac, start_date, end_date))

    data = cur.fetchall()
    conn.close()

    return data


def get_all_users():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id,name,email,role,created_at
    FROM users
    """)

    data = cur.fetchall()
    conn.close()

    return data


def get_all_devices():

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


def get_total_energy_stats():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
        COUNT(DISTINCT mac_address) as device_count,
        COUNT(*) as total_readings,
        AVG(power) as avg_power,
        MAX(power) as max_power,
        MIN(power) as min_power
    FROM sensor_logs
    """)

    data = cur.fetchone()
    conn.close()

    return data


def get_device_last_seen(mac):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT timestamp
    FROM sensor_logs
    WHERE mac_address=?
    ORDER BY id DESC
    LIMIT 1
    """, (mac,))

    data = cur.fetchone()
    conn.close()

    return data[0] if data else None


def create_alerts_table():
    """Create alerts table if it doesn't exist"""
    conn = get_connection()
    cur = conn.cursor()

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
        acknowledged INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def insert_alert(user_id, mac, alert_type, message, value, threshold):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO alerts(user_id, mac_address, alert_type, message, value, threshold, created_at)
    VALUES(?,?,?,?,?,?,?)
    """, (user_id, mac, alert_type, message, value, threshold, datetime.now()))

    conn.commit()
    conn.close()


def get_user_alerts(user_id):
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
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE alerts SET acknowledged=1 WHERE id=?
    """, (alert_id,))

    conn.commit()
    conn.close()


def get_unacknowledged_alerts(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*) FROM alerts
    WHERE user_id=? AND acknowledged=0
    """, (user_id,))

    data = cur.fetchone()
    conn.close()

    return data[0] if data else 0
