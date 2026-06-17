# ⚡ Smart Energy IoT Monitor

An IoT energy monitoring system with ML-based power prediction, anomaly detection, and a real-time dashboard.

## Setup & Run

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Generate synthetic training data
```bash
python generate_data.py
```

### Step 3: Train the ML model
```bash
python train_model.py
```

### Step 4: Start the API server (keep this terminal open)
```bash
python api_server.py
```

### Step 5: Start the dashboard (open a new terminal)
```bash
streamlit run dashboard.py
```

### Step 6: Send test sensor data (open another terminal)
```bash
python test_sensor.py
```

## Project Structure

```
├── api_server.py              # Flask REST API (port 5000)
├── dashboard.py               # Streamlit real-time dashboard
├── generate_data.py           # Synthetic data generator
├── train_model.py             # ML model training (LinearRegression)
├── test_sensor.py             # Simulated sensor client (10 readings)
├── requirements.txt           # Python dependencies
├── core/
│   ├── anomaly_detector.py    # Threshold-based anomaly detection
│   ├── prediction_engine.py   # ML model loader & predict function
│   └── realtime_monitor.py    # Stub for future use
├── interfaces/
│   └── sensor_simulator.py    # Random sensor reading generator
├── database/
│   └── db_handler.py          # SQLite database handler
├── data/
│   └── energy_data.csv        # Generated training data
└── models/
    └── power_model.pkl        # Trained model file
```

## API Endpoints

| Method | Route      | Description                          |
|--------|------------|--------------------------------------|
| POST   | /sensor    | Submit sensor reading (mac, voltage, current) |
| POST   | /api/readings | Submit full reading payload (mac_address, voltage, current, power, energy_kwh, relay_state) |
| GET    | /readings  | Get last 50 readings                 |
| GET    | /health    | Health check                         |
