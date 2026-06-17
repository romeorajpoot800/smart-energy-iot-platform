"""
test_sensor.py
Sends 10 simulated sensor readings to the API server.
Sends only mac, voltage, current (NOT power — the API predicts that).
Runs for exactly 10 iterations then stops.
"""

import sys
import os
import time
import requests

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interfaces.sensor_simulator import generate_reading

API_URL = "http://127.0.0.1:5000/sensor"
NUM_ITERATIONS = 10


def main():
    print(f"Sending {NUM_ITERATIONS} sensor readings to {API_URL}")
    print("-" * 60)

    for i in range(1, NUM_ITERATIONS + 1):
        reading = generate_reading()

        print(f"\n[{i}/{NUM_ITERATIONS}] Sending: {reading}")

        try:
            response = requests.post(API_URL, json=reading, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"  Response: predicted_power={result['predicted_power']}W, "
                      f"anomaly={result['anomaly']}, status={result['status']}")
            else:
                print(f"  Error: HTTP {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"  ERROR: Cannot connect to API at {API_URL}")
            print(f"  Make sure the API server is running: python api_server.py")
            break
        except requests.exceptions.Timeout:
            print(f"  ERROR: Request timed out.")
        except Exception as e:
            print(f"  ERROR: {e}")

        time.sleep(1)

    print("\n" + "-" * 60)
    print("Done! All readings sent.")


if __name__ == "__main__":
    main()
