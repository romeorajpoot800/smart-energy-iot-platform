import pandas as pd
from sklearn.ensemble import IsolationForest

print("Loading dataset...")

data = pd.read_csv("data/energy_data.csv")

print("Training anomaly detection model...")

# Use Power column for anomaly detection
iso = IsolationForest(contamination=0.02, random_state=42)
data["anomaly"] = iso.fit_predict(data[["Power"]])

print("Anomaly detection completed")

# Count anomalies
anomaly_count = (data["anomaly"] == -1).sum()

print("Total anomalies detected:", anomaly_count)

# Show first few anomalies
print("\nSample anomaly rows:")
print(data[data["anomaly"] == -1].head())