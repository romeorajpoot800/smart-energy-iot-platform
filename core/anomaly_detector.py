class AnomalyDetector:

    def __init__(self, voltage_threshold=250, current_threshold=5):
        self.voltage_threshold = voltage_threshold
        self.current_threshold = current_threshold

    def detect(self, voltage, current, power):
        if voltage > self.voltage_threshold:
            return True
        if current > self.current_threshold:
            return True
        if power > 650:
            return True
        return False