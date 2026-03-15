import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression

print("Loading dataset...")

# Load dataset
data = pd.read_csv("data/energy_data.csv")

print("Dataset loaded successfully")

# Select features
X = data[["Voltage", "Current", "Energy"]]
y = data["Power"]

print("Training model...")

# Train model
model = LinearRegression()
model.fit(X, y)

print("Saving model...")

# Save model
joblib.dump(model, "models/power_model.pkl")

print("Model trained and saved successfully")