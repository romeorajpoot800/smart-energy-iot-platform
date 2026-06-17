"""
dashboard.py
Streamlit dashboard for the Smart Energy IoT Monitor.
Run with: streamlit run dashboard.py
"""

import time
import requests
import streamlit as st
import pandas as pd

API_URL = "http://127.0.0.1:5000/readings"

st.set_page_config(page_title="Smart Energy IoT Monitor", page_icon="⚡", layout="wide")
st.title("⚡ Smart Energy IoT Monitor")

# Fetch data from API
try:
    response = requests.get(API_URL, timeout=5)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.ConnectionError:
    st.warning("⚠️ Cannot connect to the API server. Make sure `python api_server.py` is running on port 5000.")
    st.stop()
except requests.exceptions.Timeout:
    st.warning("⚠️ API request timed out. The server might be overloaded.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error fetching data: {e}")
    st.stop()

if not data:
    st.info("No readings yet. Run `python test_sensor.py` to send some sensor data.")
    # Non-blocking refresh: use session state + time to trigger a rerun
    REFRESH_INTERVAL = 5  # seconds
    if 'last_refresh' not in st.session_state:
        st.session_state['last_refresh'] = 0
    if time.time() - st.session_state['last_refresh'] > REFRESH_INTERVAL:
        st.session_state['last_refresh'] = time.time()
        st.experimental_rerun()

# Convert to DataFrame
df = pd.DataFrame(data)

# --- Metric Cards ---
col1, col2, col3 = st.columns(3)

latest_power = df["predicted_power"].iloc[-1] if len(df) > 0 else 0
total_readings = len(df)
anomaly_count = df["anomaly"].sum() if len(df) > 0 else 0

col1.metric("Latest Power (W)", f"{latest_power:.2f}")
col2.metric("Total Readings", total_readings)
col3.metric("Anomaly Count", int(anomaly_count))

# --- Line Chart ---
st.subheader("📈 Predicted Power Over Time")
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    chart_df = df.set_index("timestamp")[["predicted_power"]]
    st.line_chart(chart_df)
else:
    st.line_chart(df["predicted_power"])

# --- Data Table with Anomaly Highlighting ---
st.subheader("📋 Recent Readings")


def highlight_anomaly(row):
    """Highlight anomaly rows in red."""
    if row["anomaly"]:
        return ["background-color: #ffcccc"] * len(row)
    return [""] * len(row)


styled_df = df.style.apply(highlight_anomaly, axis=1)
st.dataframe(styled_df, use_container_width=True)

# --- Auto-refresh (non-blocking) ---
REFRESH_INTERVAL = 5  # seconds
if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = 0
if time.time() - st.session_state['last_refresh'] > REFRESH_INTERVAL:
    st.session_state['last_refresh'] = time.time()
    st.experimental_rerun()
