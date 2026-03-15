import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import time

print("========== REAL-TIME SMART ENERGY MONITOR ==========")

# Load trained prediction model
model = joblib.load("models/power_model.pkl")
print("ML Prediction Model Loaded Successfully")

# Initialize anomaly detector
iso = IsolationForest(contamination=0.02, random_state=42)

# Store live data
live_data = []

plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()

for i in range(200):  # simulate 200 time steps
    
    # Simulate live sensor readings
    voltage = np.random.normal(220, 5)
    current = np.random.normal(2, 0.4)
    
    energy = voltage * current  # simple approximation
    
    # Predict power using ML model
    input_df = pd.DataFrame([[voltage, current, energy]],
                            columns=["Voltage", "Current", "Energy"])
    
    predicted_power = model.predict(input_df)[0]
    
    # Store data
    live_data.append(predicted_power)
    
    # Convert to DataFrame for anomaly detection
    df_live = pd.DataFrame(live_data, columns=["Power"])
    
    if len(df_live) > 10:
        df_live["anomaly"] = iso.fit_predict(df_live[["Power"]])
        latest_status = df_live["anomaly"].iloc[-1]
    else:
        latest_status = 1
    
    # Auto cut-off simulation
    if latest_status == -1:
        print(f"⚠ OVERLOAD DETECTED at step {i} | Power = {predicted_power:.2f}")
        print("🚨 Auto Cut-Off Triggered\n")
    
    # Live Graph Update
    ax.clear()
    ax.plot(df_live["Power"], label="Predicted Power")
    
    if len(df_live) > 10:
        anomalies = df_live[df_live["anomaly"] == -1]
        ax.scatter(anomalies.index, anomalies["Power"], color="red")
    
    ax.set_title("Real-Time Power Monitoring")
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Power")
    ax.legend()
    
    plt.pause(0.1)
    time.sleep(0.1)

plt.ioff()
plt.show()

print("========== MONITORING SESSION COMPLETE ==========")