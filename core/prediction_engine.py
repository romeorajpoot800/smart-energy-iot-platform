
"""
core/prediction_engine.py
Loads the trained power model and exposes a predict(voltage, current) function.
"""

import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = os.path.join("models", "power_model.pkl")

_model = None


def _load_model():
    """Load the model from disk (cached after first call)."""
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model file not found at '{MODEL_PATH}'. "
                "Run train_model.py first to generate it."
            )
        _model = joblib.load(MODEL_PATH)
        print(f"Model loaded from {MODEL_PATH}")
    return _model


def predict(voltage: float, current: float) -> float:
    """Predict power (W) from voltage and current using the trained model."""
    model = _load_model()
    X = pd.DataFrame([[voltage, current]], columns=["Voltage", "Current"])
    prediction = model.predict(X)[0]
    return round(float(prediction), 2)
