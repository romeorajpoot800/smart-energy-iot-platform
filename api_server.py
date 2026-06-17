"""
api_server.py
Flask REST API for the Smart Energy IoT Monitor.
Routes:
  POST /sensor   - Accept sensor data, predict power, detect anomalies, store in DB
  GET  /readings - Return last 50 readings from DB
  GET  /health   - Health check
"""

import sys
import os

# Ensure project root is on the path so core/ and database/ imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from core.prediction_engine import predict
from core.anomaly_detector import is_anomaly
from database.db_handler import SQLiteHandler

app = Flask(__name__)
CORS(app)

# Initialize database
db = SQLiteHandler()
db.init_db()

# Try loading the model at startup to give a clear error message
try:
    from core.prediction_engine import _load_model
    _load_model()
    print("Model loaded successfully at startup.")
except FileNotFoundError as e:
    print(f"WARNING: {e}")
    print("The API will start, but POST /sensor will fail until the model exists.")
    print("Run: python train_model.py")


@app.route("/sensor", methods=["POST"])
def sensor():
    """Accept sensor JSON {mac, voltage, current}, predict power, detect anomaly, store."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    mac = data.get("mac")
    voltage = data.get("voltage")
    current = data.get("current")

    if mac is None or voltage is None or current is None:
        return jsonify({"error": "Missing required fields: mac, voltage, current"}), 400

    try:
        voltage = float(voltage)
        current = float(current)
    except (ValueError, TypeError):
        return jsonify({"error": "voltage and current must be numbers"}), 400

    # Predict power using the ML model
    try:
        predicted_power = predict(voltage, current)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500

    # Detect anomaly
    anomaly = is_anomaly(predicted_power)

    # Save to database
    db.insert_reading(
        mac=mac,
        voltage=voltage,
        current=current,
        predicted_power=predicted_power,
        anomaly=anomaly,
    )

    return jsonify({
        "predicted_power": predicted_power,
        "anomaly": anomaly,
        "status": "ok",
    })


@app.route("/readings", methods=["GET"])
def readings():
    """Return the last 50 readings from the database."""
    rows = db.get_last_n(50)
    return jsonify(rows)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("Starting Smart Energy IoT API on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
