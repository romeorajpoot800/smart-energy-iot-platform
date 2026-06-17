"""
Admin Dashboard Page
System-wide administration and monitoring
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuration
API_URL = "http://localhost:5000"


def fetch_all_users():
    """Fetch all users (admin endpoint)"""
    try:
        response = requests.get(f"{API_URL}/api/users", timeout=5)
        if response.status_code == 200:
            return response.json().get("users", [])
        return []
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []


def fetch_all_devices():
    """Fetch all devices (admin endpoint)"""
    try:
        response = requests.get(f"{API_URL}/api/device/list/all", timeout=5)
        if response.status_code == 200:
            return response.json().get("devices", [])
        return []
    except Exception as e:
        st.error(f"Error fetching devices: {e}")
        return []


def fetch_all_alerts():
    """Fetch all alerts"""
    try:
        response = requests.get(f"{API_URL}/api/alerts/all", timeout=5)
        if response.status_code == 200:
            return response.json().get("alerts", [])
        return []
    except Exception as e:
        st.error(f"Error fetching alerts: {e}")
        return []


def fetch_global_energy_stats():
    """Fetch global energy statistics"""
    try:
        # Get all devices and sum up their readings
        devices = fetch_all_devices()
        
        total_readings = 0
        total_power = 0
        max_power = 0
        all_logs = []
        
        for device in devices:
            mac = device.get('mac_address')
            if mac:
                try:
                    response = requests.get(
                        f"{API_URL}/api/energy/logs/{mac}",
                        params={"limit": 1000},
                        timeout=5
                    )
                    if response.status_code == 200:
                        logs = response.json().get("logs", [])
                        all_logs.extend(logs)
                        
                        for log in logs:
                            power = log.get('power', 0)
                            total_power += power
                            if power > max_power:
                                max_power = power
                except:
                    pass
        
        total_readings = len(all_logs)
        
        # Calculate energy in kWh (assuming 5-second intervals)
        energy_kwh = (total_power * 5) / 3600000 if total_power > 0 else 0
        
        return {
            'total_readings': total_readings,
            'total_power': total_power,
            'max_power': max_power,
            'energy_kwh': energy_kwh,
            'device_count': len(devices)
        }
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return {
            'total_readings': 0,
            'total_power': 0,
            'max_power': 0,
            'energy_kwh': 0,
            'device_count': 0
        }


def main():
    """Main admin page"""
    
    st.title("⚙️ Admin Panel")
    st.markdown("---")
    
    # Get stats
    users = fetch_all_users()
    devices = fetch_all_devices()
    alerts = fetch_all_alerts()
    stats = fetch_global_energy_stats()
    
    # Overview metrics
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", len(users))
    
    with col2:
        st.metric("Total Devices", stats['device_count'])
    
    with col3:
        st.metric("Total Readings", stats['total_readings'])
    
    with col4:
        st.metric("Total Energy", f"{stats['energy_kwh']:.2f} kWh")
    
    st.markdown("---")
    
    # Tabs for different admin sections
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "📱 Devices", "⚡ Energy", "🚨 Alerts"])
    
    # === USERS TAB ===
    with tab1:
        st.subheader("All Users")
        
        if users:
            users_df = pd.DataFrame(users)
            st.dataframe(users_df, use_container_width=True)
            
            st.write(f"**Total Users: {len(users)}**")
        else:
            st.info("No users found")
    
    # === DEVICES TAB ===
    with tab2:
        st.subheader("All Devices")
        
        if devices:
            devices_df = pd.DataFrame(devices)
            st.dataframe(devices_df, use_container_width=True)
            
            st.write(f"**Total Devices: {len(devices)}**")
            
            # Device owners summary
            st.subheader("Devices by Owner")
            owner_counts = devices_df.groupby('owner').size()
            st.bar_chart(owner_counts)
        else:
            st.info("No devices found")
    
    # === ENERGY TAB ===
    with tab3:
        st.subheader("Global Energy Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Power Consumed", f"{stats['total_power']:.2f} W")
        
        with col2:
            st.metric("Max Power Recorded", f"{stats['max_power']:.2f} W")
        
        st.metric("Total Energy", f"{stats['energy_kwh']:.4f} kWh")
        
        st.info(f"Statistics based on {stats['total_readings']} sensor readings")
    
    # === ALERTS TAB ===
    with tab4:
        st.subheader("System Alerts")
        
        if alerts and len(alerts) > 0:
            alerts_df = pd.DataFrame(alerts)
            
            # Show alert counts by type
            st.write("### Alert Summary")
            
            if 'alert_type' in alerts_df.columns:
                alert_counts = alerts_df['alert_type'].value_counts()
                st.write("Alerts by Type:")
                for alert_type, count in alert_counts.items():
                    st.write(f"- {alert_type}: {count}")
            
            st.write("### All Alerts")
            st.dataframe(alerts_df, use_container_width=True)
            
            st.write(f"**Total Alerts: {len(alerts)}**")
        else:
            st.success("No alerts in the system")
    
    # Footer
    st.markdown("---")
    st.caption(f"Admin Panel | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
