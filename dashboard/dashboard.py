"""
Smart Energy Monitoring Dashboard
Streamlit dashboard for real-time energy monitoring
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

from streamlit_autorefresh import st_autorefresh

# Configuration
API_URL = "http://localhost:5000"
REFRESH_INTERVAL = 5000  # 5 seconds

# Page configuration
st.set_page_config(
    page_title="Smart Energy Monitor",
    page_icon="⚡",
    layout="wide"
)

# Auto-refresh every 5 seconds
st_autorefresh(interval=REFRESH_INTERVAL, key="refresh")


def fetch_devices():
    """Fetch user's devices from API"""
    try:
        response = requests.get(f"{API_URL}/api/device/list", timeout=5)
        if response.status_code == 200:
            return response.json().get("devices", [])
        return []
    except Exception as e:
        st.error(f"Error fetching devices: {e}")
        return []


def fetch_energy_logs(mac_address, limit=50):
    """Fetch energy logs for a device"""
    try:
        response = requests.get(
            f"{API_URL}/api/energy/logs/{mac_address}",
            params={"limit": limit},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("logs", [])
        return []
    except Exception as e:
        st.error(f"Error fetching logs: {e}")
        return []


def main():
    """Main dashboard"""
    
    # Title
    st.title("⚡ Smart Energy Monitor")
    st.markdown("---")
    
    # Fetch devices
    devices = fetch_devices()
    
    if not devices:
        st.warning("No devices found. Please register a device first.")
        st.info("💡 Tip: Use the API to register a device, then run the sensor simulator.")
        return
    
    # Device selector
    st.sidebar.header("Device Selection")
    
    # Create device options for dropdown
    device_options = {d["device_name"]: d["mac_address"] for d in devices}
    
    selected_device = st.sidebar.selectbox(
        "Select Device",
        options=list(device_options.keys())
    )
    
    mac_address = device_options[selected_device]
    
    # Show selected device info
    st.sidebar.info(f"MAC: {mac_address}")
    
    # Fetch energy logs
    logs = fetch_energy_logs(mac_address)
    
    if not logs:
        st.warning("No sensor data yet. Start the sensor simulator to see data.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(logs)
    
    # Reverse to show oldest first
    df = df.iloc[::-1]
    
    # Display metrics
    st.header("📊 Real-Time Power Usage")
    
    # Get latest values
    latest = df.iloc[-1]
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Voltage",
            f"{latest['voltage']:.2f} V",
            delta=None
        )
    
    with col2:
        st.metric(
            "Current",
            f"{latest['current']:.2f} A",
            delta=None
        )
    
    with col3:
        st.metric(
            "Power",
            f"{latest['power']:.2f} W",
            delta=None
        )
    
    # Graphs section
    st.markdown("---")
    st.header("📈 Energy Graphs")
    
    # Power vs Time
    st.subheader("Power vs Time")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.line_chart(df.set_index("timestamp")["power"])
    
    # Voltage vs Time
    st.subheader("Voltage vs Time")
    st.line_chart(df.set_index("timestamp")["voltage"])
    
    # Current vs Time
    st.subheader("Current vs Time")
    st.line_chart(df.set_index("timestamp")["current"])
    
    # Statistics section
    st.markdown("---")
    st.header("📉 Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Power", f"{df['power'].mean():.2f} W")
    
    with col2:
        st.metric("Max Power", f"{df['power'].max():.2f} W")
    
    with col3:
        st.metric("Min Power", f"{df['power'].min():.2f} W")
    
    # Data table
    st.markdown("---")
    st.header("📋 Recent Data")
    
    # Show last 20 readings
    st.dataframe(df.tail(20), use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Auto-refresh every 5 seconds")


if __name__ == "__main__":
    main()
