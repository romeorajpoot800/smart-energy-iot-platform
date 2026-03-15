import pandas as pd
import numpy as np

# Generate 3 days of minute-level data
minutes = 3 * 24 * 60

timestamps = pd.date_range(start="2026-02-01", periods=minutes, freq="min")

voltage = np.random.normal(220, 5, minutes)
current = np.random.normal(2, 0.4, minutes)

power = voltage * current
energy = np.cumsum(power) / 1000

data = pd.DataFrame({
    "Timestamp": timestamps,
    "Voltage": voltage,
    "Current": current,
    "Power": power,
    "Energy": energy
})

data.to_csv("data/energy_data.csv", index=False)

print("Dataset generated successfully")