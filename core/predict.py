import joblib
import numpy as np

print("Loading trained model...")

# Load saved model
model = joblib.load("models/power_model.pkl")

print("Model loaded successfully")

# Example new input (Voltage, Current, Energy)
new_data = np.array([[230, 2.5, 1200]])

print("Making prediction...")

prediction = model.predict(new_data)

print("Predicted Power Consumption:", prediction[0])