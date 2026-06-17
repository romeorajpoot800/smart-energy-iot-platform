"""
core/anomaly_detector.py
Simple threshold-based anomaly detection for power readings.
"""

POWER_THRESHOLD_W = 1200


def is_anomaly(power_w: float) -> bool:
    """Returns True if the predicted power exceeds the threshold (1200W)."""
    return power_w > POWER_THRESHOLD_W
