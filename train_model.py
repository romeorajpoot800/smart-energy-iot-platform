"""
train_model.py
Trains a LinearRegression model to predict Power from Voltage and Current.
Features: Voltage, Current (NOT Energy — that would be data leakage).
Target: Power
Saves trained model to models/power_model.pkl
"""

import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def train():
    # Load data
    data_path = os.path.join("data", "energy_data.csv")
    if not os.path.exists(data_path):
        print(f"ERROR: {data_path} not found. Run generate_data.py first.")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} rows from {data_path}")

    # Features: ONLY Voltage and Current (no Energy — that's derived from Power)
    X = df[["Voltage", "Current"]]
    y = df["Power"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Model trained successfully.")
    print(f"  MAE:  {mae:.4f}")
    print(f"  R²:   {r2:.4f}")

    # Save model
    os.makedirs("models", exist_ok=True)
    model_path = os.path.join("models", "power_model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
