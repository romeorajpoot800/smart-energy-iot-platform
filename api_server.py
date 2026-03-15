from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "database/energy.db"


def insert_sensor(mac, voltage, current, power):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac TEXT,
        voltage REAL,
        current REAL,
        power REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute(
        "INSERT INTO sensor_logs(mac, voltage, current, power) VALUES (?, ?, ?, ?)",
        (mac, voltage, current, power)
    )

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return "Energy Monitor API Running"


@app.route("/sensor", methods=["POST"])
def receive_sensor():

    data = request.json

    mac = data.get("mac")
    voltage = data.get("voltage")
    current = data.get("current")
    power = data.get("power")

    insert_sensor(mac, voltage, current, power)

    return jsonify({"status": "saved"})


if __name__ == "__main__":
    print("Starting Energy Monitor API...")
    app.run(host="0.0.0.0", port=5000, debug=True)