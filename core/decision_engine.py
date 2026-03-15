class DecisionEngine:

    def __init__(self, power_threshold=600):
        self.power_threshold = power_threshold

    def evaluate(self, power, is_anomaly):

        if power > self.power_threshold or is_anomaly:
            print(f"⚠ OVERLOAD DETECTED | Power = {power:.2f}")
            print("🚨 Auto Cut-Off Triggered\n")
        else:
            print(f"Power Normal | {power:.2f}")