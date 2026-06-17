"""
generate_data.py
Generates 3 days of minute-level synthetic energy data.
Columns: Timestamp, Voltage (~220V), Current (~2A), Power, Energy
Saves to data/energy_data.csv
"""

import os
import numpy as np
import pandas as pd

def generate_energy_data():
    # 3 days of minute-level data = 3 * 24 * 60 = 4320 rows
    num_minutes = 3 * 24 * 60
    timestamps = pd.date_range(start="2026-01-01", periods=num_minutes, freq="min")

    np.random.seed(42)

    # Voltage centered around 220V with small noise
    voltage = np.random.normal(loc=220.0, scale=5.0, size=num_minutes)

    # Current centered around 2A with small noise
    current = np.random.normal(loc=2.0, scale=0.5, size=num_minutes)

    # Power = Voltage * Current
    power = voltage * current

    # Energy = cumulative sum of Power (in kWh approximation)
    energy = np.cumsum(power) / 1000.0

    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Voltage": np.round(voltage, 2),
        "Current": np.round(current, 2),
        "Power": np.round(power, 2),
        "Energy": np.round(energy, 4),
    })

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "energy_data.csv")
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows of energy data.")
    print(f"Saved to {output_path}")
    print(df.head())

if __name__ == "__main__":
    generate_energy_data()
