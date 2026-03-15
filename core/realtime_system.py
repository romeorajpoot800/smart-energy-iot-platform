import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.predictor import PowerPredictor
from core.anomaly_detector import AnomalyDetector
from core.decision_engine import DecisionEngine
from interfaces.simulator import get_sensor_data

import time

print("===== SMART ENERGY MONITOR SYSTEM STARTED =====")

predictor = PowerPredictor("models/power_model.pkl")
anomaly_detector = AnomalyDetector()
decision_engine = DecisionEngine(power_threshold=600)

for step in range(200):

    # 1️⃣ Get sensor data (currently simulated)
    voltage, current, energy = get_sensor_data()

    # 2️⃣ Predict power using ML model
    predicted_power = predictor.predict(voltage, current, energy)

    # 3️⃣ Detect anomaly
    is_anomaly = anomaly_detector.detect(voltage, current, predicted_power)

    # 4️⃣ Decision making
    decision_engine.evaluate(predicted_power, is_anomaly)

    time.sleep(0.2)

print("===== MONITORING COMPLETE =====")