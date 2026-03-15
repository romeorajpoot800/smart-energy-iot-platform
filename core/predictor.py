import joblib
import numpy as np


class PowerPredictor:

    def __init__(self, model_path):
        print("Loading ML Prediction Model...")
        self.model = joblib.load(model_path)
        print("Model Loaded Successfully")

    def predict(self, voltage, current, energy):
        input_data = np.array([[voltage, current, energy]])
        prediction = self.model.predict(input_data)
        return prediction[0]