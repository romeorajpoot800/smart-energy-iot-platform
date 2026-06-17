"""
IoT Sensor Simulator
Generates random sensor data and sends to the API
"""

import requests
import random
import time
import uuid
from datetime import datetime

# Configuration
API_URL = "http://localhost:5000/api/sensor_data"
INTERVAL = 5  # seconds

# Device MAC address
MAC_ADDRESS = "AA:BB:CC:DD:EE:FF"


def generate_sensor_data():
    """
    Generate random sensor values
    
    Returns:
        dict with voltage, current, power
    """
    # Generate random values
    voltage = random.uniform(210, 240)  # 210-240V
    current = random.uniform(0, 10)        # 0-10A
    power = voltage * current             # power = voltage * current
    
    return {
        "mac_address": MAC_ADDRESS,
        "voltage": round(voltage, 2),
        "current": round(current, 2),
        "power": round(power, 2)
    }


def send_sensor_data(data):
    """
    Send sensor data to API
    
    Args:
        data: Dictionary with sensor readings
        
    Returns:
        Response from API
    """
    try:
        response = requests.post(API_URL, json=data)
        return response
    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now()}] ❌ Failed to connect to API at {API_URL}")
        return None
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error: {e}")
        return None


def main():
    """Main loop - generate and send sensor data every 5 seconds"""
    
    print("=" * 50)
    print("IoT Sensor Simulator")
    print("=" * 50)
    print(f"MAC Address: {MAC_ADDRESS}")
    print(f"API URL: {API_URL}")
    print(f"Interval: {INTERVAL} seconds")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    while True:
        # Generate sensor data
        data = generate_sensor_data()
        
        # Print to console
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] 📊 Sensor Data:")
        print(f"    Voltage: {data['voltage']} V")
        print(f"    Current: {data['current']} A")
        print(f"    Power:   {data['power']} W")
        
        # Send to API
        response = send_sensor_data(data)
        
        if response:
            if response.status_code == 201:
                result = response.json()
                print(f"    ✅ Sent successfully!")
                
                # Check for alerts
                if result.get('alert'):
                    alert = result['alert']
                    print(f"    ⚠️  ALERT: {alert['message']}")
            else:
                print(f"    ❌ Failed with status: {response.status_code}")
        else:
            print(f"    ❌ Could not connect to API")
        
        print("-" * 50)
        
        # Wait for next reading
        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Simulator stopped by user")
