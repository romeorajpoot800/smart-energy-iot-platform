import numpy as np

def get_sensor_data():
    voltage = np.random.normal(220, 5)
    current = np.random.normal(2.5, 0.5)
    energy = np.random.normal(1000, 50)
    return voltage, current, energy