# ESP32 Energy Monitor Firmware

## Hardware Required
- ESP32 DevKit
- Voltage Sensor (ZMPT101B or similar)
- Current Sensor (ACS712 5A/20A/30A)
- Relay Module (optional)
- Power supply

## Pin Connections

| ESP32 Pin | Component |
|-----------|-----------|
| GPIO34 | Voltage Sensor Signal |
| GPIO35 | Current Sensor Signal |
| GPIO26 | Relay Module IN |

## Installation

1. **Install Arduino IDE** or **PlatformIO**

2. **Install ESP32 Board Package**
   - Arduino IDE: Add ESP32 board URL in preferences
   - PlatformIO: Already included

3. **Install Required Libraries**
   - ArduinoJson
   - HTTPClient (included with ESP32)
   - WiFi (included with ESP32)

4. **Configure WiFi**
   Edit these lines in the firmware:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```

5. **Configure API Server**
   ```cpp
   const char* serverUrl = "http://YOUR_SERVER_IP:5000/sensor_data";
   ```

## Calibration

Adjust these values based on your sensors:

```cpp
// Voltage sensor
const float VOLTAGE_DIVIDER_RATIO = 3.3 / 4095.0 * 75.0;

// Current sensor (ACS712 5A version)
const float CURRENT_SENSITIVITY = 0.185;
```

## Upload

1. Connect ESP32 to computer via USB
2. Select correct COM port
3. Upload sketch

## Serial Monitor

Open Serial Monitor at 115200 baud to see:
- Connection status
- Sensor readings
- API responses

## Features

- Reads voltage and current sensors
- Calculates power (P = V × I)
- Sends data to API every 5 seconds
- Receives alerts from API
- Optional relay control on overload
