import requests
import random
import time

SERVER_URL = "http://127.0.0.1:5000/energy/data"

MAC_ADDRESS = "AA:BB:CC:DD:11:22"


def generate_energy_data():

    voltage = round(random.uniform(220, 240), 2)
    current = round(random.uniform(1, 10), 2)
    power = round(voltage * current, 2)

    return voltage, current, power


def send_data():

    voltage, current, power = generate_energy_data()

    payload = {
        "mac_address": MAC_ADDRESS,
        "voltage": voltage,
        "current": current,
        "power": power
    }

    try:
        response = requests.post(SERVER_URL, json=payload)
        print("Sent:", payload)
        print("Server Response:", response.json())
        print("------------")

    except Exception as e:
        print("Error sending data:", e)


def start_simulator():

    print("Starting IoT Device Simulator")
    print("Device MAC:", MAC_ADDRESS)

    while True:
        send_data()
        time.sleep(5)


if __name__ == "__main__":
    start_simulator()
    