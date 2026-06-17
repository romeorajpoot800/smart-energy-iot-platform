/**
 * ESP32 Energy Monitoring Firmware
 * Sends sensor data to Flask API every 5 seconds
 * 
 * Hardware:
 * - ESP32 DevKit
 * - Voltage Sensor (ZMPT101B) on GPIO34
 * - Current Sensor (ACS712) on GPIO35
 * - Relay Module on GPIO26
 * 
 * Connections:
 * ESP32 GPIO34 → Voltage Sensor Signal
 * ESP32 GPIO35 → Current Sensor Signal  
 * ESP32 GPIO26 → Relay IN
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============== CONFIGURATION ==============

// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// API Server
const char* serverUrl = "http://YOUR_SERVER_IP:5000/sensor_data";

// Device MAC Address (will be auto-detected)
String deviceMac = "";

// Pin Definitions
const int VOLTAGE_SENSOR_PIN = 34;  // ADC1_CH6
const int CURRENT_SENSOR_PIN = 35;   // ADC1_CH7
const int RELAY_PIN = 26;

// Timing
const unsigned long SEND_INTERVAL = 5000;  // 5 seconds

// ============== CALIBRATION ==============
// Adjust these values based on your sensors

// Voltage sensor calibration
const float VOLTAGE_DIVIDER_RATIO = 3.3 / 4095.0 * 75.0;  // For 75V:1V divider
const int VOLTAGE_SAMPLES = 100;

// Current sensor calibration (ACS712 5A version)
// 185mV per ampere (5A version)
const float CURRENT_SENSITIVITY = 0.185;  // V/A
const int CURRENT_SAMPLES = 100;

// ============== GLOBAL VARIABLES ==============
unsigned long lastSendTime = 0;

// ============== SETUP ==============
void setup() {
  Serial.begin(115200);
  
  // Configure ADC
  analogReadResolution(12);  // 0-4095
  analogSetAttenuation(ADC_0_6V);  // 0-3.3V range
  
  // Set pin modes
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Relay off initially
  
  // Connect to WiFi
  connectToWiFi();
  
  // Get device MAC address
  deviceMac = WiFi.macAddress();
  Serial.println("Device MAC: " + deviceMac);
  
  Serial.println("ESP32 Energy Monitor Ready!");
}

// ============== MAIN LOOP ==============
void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }
  
  // Send data every 5 seconds
  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = currentTime;
    
    // Read sensors
    float voltage = readVoltage();
    float current = readCurrent();
    float power = voltage * current;
    
    // Print to serial
    Serial.println("====================");
    Serial.print("Voltage: ");
    Serial.print(voltage);
    Serial.println(" V");
    Serial.print("Current: ");
    Serial.print(current);
    Serial.println(" A");
    Serial.print("Power: ");
    Serial.print(power);
    Serial.println(" W");
    Serial.println("====================");
    
    // Send to API
    sendSensorData(voltage, current, power);
  }
  
  delay(10);  // Small delay to prevent watchdog
}

// ============== FUNCTIONS ==============

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi Connection Failed!");
  }
}

float readVoltage() {
  long sum = 0;
  for (int i = 0; i < VOLTAGE_SAMPLES; i++) {
    sum += analogRead(VOLTAGE_SENSOR_PIN);
    delayMicroseconds(100);
  }
  
  float average = sum / (float)VOLTAGE_SAMPLES;
  float voltage = average * VOLTAGE_DIVIDER_RATIO;
  
  // Calibration offset (adjust as needed)
  voltage = voltage - 5.0;  // Remove zero offset
  
  return max(0, voltage);  // Ensure non-negative
}

float readCurrent() {
  long sum = 0;
  for (int i = 0; i < CURRENT_SAMPLES; i++) {
    sum += analogRead(CURRENT_SENSOR_PIN);
    delayMicroseconds(100);
  }
  
  float average = sum / (float)CURRENT_SAMPLES;
  
  // Convert ADC to voltage
  float voltage = average * 3.3 / 4095.0;
  
  // Convert to current (ACS712 5A version)
  // Current = (Vout - 2.5) / Sensitivity
  float current = (voltage - 2.5) / CURRENT_SENSITIVITY;
  
  return max(0, current);  // Ensure non-negative
}

void sendSensorData(float voltage, float current, float power) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON payload
    JsonDocument doc;
    doc["mac_address"] = deviceMac;
    doc["voltage"] = voltage;
    doc["current"] = current;
    doc["power"] = power;
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    // Send POST request
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response: " + String(httpResponseCode));
      Serial.println("Response: " + response);
      
      // Parse response for alerts
      parseApiResponse(response);
    } else {
      Serial.println("Error sending data: " + String(httpResponseCode));
    }
    
    http.end();
  } else {
    Serial.println("WiFi not connected!");
  }
}

void parseApiResponse(String response) {
  // Parse JSON response to check for alerts
  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, response);
  
  if (!error) {
    if (doc.containsKey("alert") && doc["alert"].is<JsonObject>()) {
      Serial.println("⚠️ ALERT DETECTED!");
      JsonObject alert = doc["alert"];
      Serial.println("Type: " + String(alert["type"].as<const char*>()));
      Serial.println("Message: " + String(alert["message"].as<const char*>()));
      
      // Optional: Trigger relay on overload
      if (String(alert["type"].as<const char*>()) == "OVERLOAD") {
        Serial.println("⚡ Triggering overload protection...");
        digitalWrite(RELAY_PIN, HIGH);  // Turn off load
        delay(1000);
        digitalWrite(RELAY_PIN, LOW);  // Reset
      }
    } else {
      Serial.println("✅ Data sent successfully - No alerts");
    }
  }
}

// ============== HELPER FUNCTIONS ==============

// Control relay (call from API or manually)
void setRelay(bool state) {
  digitalWrite(RELAY_PIN, state ? HIGH : LOW);
  Serial.println(state ? "Relay: ON" : "Relay: OFF");
}

// Get WiFi signal strength
int getSignalStrength() {
  return WiFi.RSSI();
}

// Get uptime in seconds
unsigned long getUptime() {
  return millis() / 1000;
}
