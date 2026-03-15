import requests
import random
import time

url = "http://127.0.0.1:5000/sensor"

mac = "A4CF12F3B9D2"

while True:

    voltage = round(random.uniform(220,240),2)
    current = round(random.uniform(1,5),2)
    power = round(voltage * current,2)

    data = {
        "mac": mac,
        "voltage": voltage,
        "current": current,
        "power": power
    }

    r = requests.post(url,json=data)

    print("Sent:",data)

    time.sleep(3)