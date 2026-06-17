"""
interfaces/sensor_simulator.py
Generates a single random sensor reading dict with keys: mac, voltage, current.
"""

import random


def generate_reading() -> dict:
    """Generate one random sensor reading."""
    return {
        "mac": "AA:BB:CC:DD:EE:FF",
        "voltage": round(random.uniform(210.0, 230.0), 2),
        "current": round(random.uniform(1.0, 3.0), 2),
    }
