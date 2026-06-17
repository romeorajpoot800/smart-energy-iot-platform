import requests
import random
import time

API_URL = "http://127.0.0.1:5000/energy/data"

MAC_ADDRESS = "AA:BB:CC:DD:33:44"

print("Starting IoT Device Simulator 2")
print("Device MAC:", MAC_ADDRESS)

while True:

    voltage = random.uniform(220,240)
    current = random.uniform(2,8)
    power = voltage * current

    data = {
        "mac_address": MAC_ADDRESS,
        "voltage": voltage,
        "current": current,
        "power": power
    }

    try:

        r = requests.post(API_URL,json=data)

        print("Data sent:",data)

    except Exception as e:

        print("Error sending data:",e)

    time.sleep(5)