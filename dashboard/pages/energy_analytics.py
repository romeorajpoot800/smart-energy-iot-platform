"""
Energy Analytics Page
Daily, weekly, monthly energy consumption analysis
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import numpy as np

# Configuration
API_URL = "http://localhost:5000"


def fetch_energy_logs(mac_address, limit=1000):
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


def calculate_energy_kwh(power_values, time_interval_seconds=5):
    """
    Calculate energy consumption in kWh
    
    Formula: Energy (kWh) = sum(power) * time_interval / 1000 / 3600
    """
    if not power_values:
        return 0
    
    total_power = sum(power_values)
    # Convert to kWh: (watts * seconds) / (1000 * 3600)
    energy_kwh = (total_power * time_interval_seconds) / 3600000
    return energy_kwh


def get_daily_consumption(df):
    """Calculate daily energy consumption"""
    if df.empty:
        return pd.DataFrame()
    
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily = df.groupby('date')['power'].sum()
    
    # Convert to kWh (assuming 5-second intervals)
    daily_kwh = daily / 1000 / 720  # 720 intervals per hour
    
    return pd.DataFrame({
        'date': daily_kwh.index,
        'energy_kwh': daily_kwh.values
    })


def get_weekly_consumption(df):
    """Calculate weekly energy consumption"""
    if df.empty:
        return pd.DataFrame()
    
    df['week'] = pd.to_datetime(df['timestamp']).dt.isocalendar().week
    df['year'] = pd.to_datetime(df['timestamp']).dt.year
    df['week_label'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
    
    weekly = df.groupby('week_label')['power'].sum()
    weekly_kwh = weekly / 1000 / 720
    
    return pd.DataFrame({
        'week': weekly_kwh.index,
        'energy_kwh': weekly_kwh.values
    })


def get_monthly_consumption(df):
    """Calculate monthly energy consumption"""
    if df.empty:
        return pd.DataFrame()
    
    df['month'] = pd.to_datetime(df['timestamp']).dt.to_period('M')
    monthly = df.groupby('month')['power'].sum()
    monthly_kwh = monthly / 1000 / 720
    
    return pd.DataFrame({
        'month': monthly.astype(str),
        'energy_kwh': monthly_kwh.values
    })


def detect_peak_usage(df, top_n=5):
    """Detect peak usage periods"""
    if df.empty:
        return []
    
    # Get top power readings
    top_readings = df.nlargest(top_n, 'power')
    
    peaks = []
    for _, row in top_readings.iterrows():
        peaks.append({
            'timestamp': row['timestamp'],
            'power': row['power'],
            'voltage': row['voltage'],
            'current': row['current']
        })
    
    return peaks


def main():
    """Main analytics page"""
    
    st.title("📊 Energy Analytics")
    st.markdown("---")
    
    # Device selector
    st.sidebar.header("Select Device")
    
    try:
        response = requests.get(f"{API_URL}/api/device/list", timeout=5)
        if response.status_code == 200:
            devices = response.json().get("devices", [])
        else:
            devices = []
    except:
        devices = []
    
    if not devices:
        st.warning("No devices found. Please register a device first.")
        return
    
    device_options = {d["device_name"]: d["mac_address"] for d in devices}
    selected_device = st.sidebar.selectbox(
        "Select Device",
        options=list(device_options.keys())
    )
    mac_address = device_options[selected_device]
    
    # Fetch data
    logs = fetch_energy_logs(mac_address, limit=1000)
    
    if not logs:
        st.warning("No energy data available. Start the sensor simulator first.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(logs)
    df = df.iloc[::-1]  # Reverse to oldest first
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Total statistics
    st.header("📈 Overview")
    
    total_energy = calculate_energy_kwh(df['power'].tolist())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Readings", len(df))
    
    with col2:
        st.metric("Total Energy", f"{total_energy:.2f} kWh")
    
    with col3:
        st.metric("Avg Power", f"{df['power'].mean():.2f} W")
    
    with col4:
        st.metric("Max Power", f"{df['power'].max():.2f} W")
    
    # Charts section
    st.markdown("---")
    st.header("📅 Consumption Charts")
    
    tab1, tab2, tab3 = st.tabs(["Daily", "Weekly", "Monthly"])
    
    # Daily chart
    with tab1:
        st.subheader("Daily Energy Consumption")
        
        daily_df = get_daily_consumption(df)
        
        if not daily_df.empty:
            st.bar_chart(daily_df.set_index('date')['energy_kwh'])
            
            # Show data
            st.write("Daily Breakdown:")
            st.dataframe(daily_df, use_container_width=True)
        else:
            st.info("Not enough data for daily analysis")
    
    # Weekly chart
    with tab2:
        st.subheader("Weekly Energy Consumption")
        
        weekly_df = get_weekly_consumption(df)
        
        if not weekly_df.empty:
            st.line_chart(weekly_df.set_index('week')['energy_kwh'])
            
            # Show data
            st.write("Weekly Breakdown:")
            st.dataframe(weekly_df, use_container_width=True)
        else:
            st.info("Not enough data for weekly analysis")
    
    # Monthly chart
    with tab3:
        st.subheader("Monthly Energy Consumption")
        
        monthly_df = get_monthly_consumption(df)
        
        if not monthly_df.empty:
            st.bar_chart(monthly_df.set_index('month')['energy_kwh'])
            
            # Show data
            st.write("Monthly Breakdown:")
            st.dataframe(monthly_df, use_container_width=True)
        else:
            st.info("Not enough data for monthly analysis")
    
    # Peak usage section
    st.markdown("---")
    st.header("⚡ Peak Usage Detection")
    
    peaks = detect_peak_usage(df, top_n=5)
    
    if peaks:
        st.subheader("Top 5 Peak Power Readings")
        
        for i, peak in enumerate(peaks, 1):
            st.write(f"**#{i}** - {peak['timestamp']}")
            st.write(f"   Power: {peak['power']:.2f} W | Voltage: {peak['voltage']:.2f} V | Current: {peak['current']:.2f} A")
    else:
        st.info("No peak data available")
    
    # Footer
    st.markdown("---")
    st.caption("Energy Analytics | Data refresh on page reload")


if __name__ == "__main__":
    main()
