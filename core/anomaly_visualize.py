import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

print("Loading dataset...")

# Load dataset
data = pd.read_csv("data/energy_data.csv")

print("Training anomaly detection model...")

# Train Isolation Forest
iso = IsolationForest(contamination=0.02, random_state=42)
data["anomaly"] = iso.fit_predict(data[["Power"]])

print("Anomaly detection completed")

# Separate normal and anomaly points
normal_data = data[data["anomaly"] == 1]
anomaly_data = data[data["anomaly"] == -1]

anomaly_count = len(anomaly_data)

print("Total anomalies detected:", anomaly_count)

# Auto cut-off simulation
if anomaly_count > 0:
    print("\n⚠ WARNING: Overload detected!")
    print("🚨 Triggering Auto Cut-Off System...")
else:
    print("\nSystem running normally.")

# Plot graph
print("\nGenerating visualization...")

plt.figure(figsize=(12,6))

# Plot normal power usage
plt.plot(normal_data["Power"].values, label="Normal Usage")

# Plot anomalies in red
plt.scatter(anomaly_data.index,
            anomaly_data["Power"],
            color="red",
            label="Anomaly (Overload)")

plt.title("Power Consumption with Anomaly Detection")
plt.xlabel("Time Index")
plt.ylabel("Power")
plt.legend()

plt.show()