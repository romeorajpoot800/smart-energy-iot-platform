"""
ML Insights Page
Energy prediction and anomaly detection using ML
"""

import streamlit as st
import pandas as pd
import requests
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.energy_ml import (
    train_power_prediction_model,
    predict_power,
    predict_next_power,
    train_anomaly_detector,
    detect_anomalies,
    get_anomaly_summary
)

# Configuration
API_URL = "http://localhost:5000"


def fetch_energy_logs(mac_address, limit=200):
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
    """Main ML insights page"""
    
    st.title("🤖 ML Insights")
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
    
    # Number of readings for training
    num_readings = st.sidebar.slider("Training data size", 50, 200, 100)
    
    # Fetch data
    logs = fetch_energy_logs(mac_address, limit=num_readings)
    
    if not logs or len(logs) < 20:
        st.warning("Not enough data for ML analysis. Need at least 20 readings.")
        st.info("💡 Start the sensor simulator to generate more data.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(logs)
    df = df.iloc[::-1]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # ML Section
    st.header("🧠 Machine Learning Analysis")
    
    # Train models
    with st.spinner("Training ML models..."):
        # Power Prediction Model
        prediction_model, prediction_scaler = train_power_prediction_model(df)
        
        # Anomaly Detection Model
        anomaly_model, anomaly_scaler = train_anomaly_detector(df)
    
    # Tabs for different ML features
    tab1, tab2 = st.tabs(["⚡ Power Prediction", "🔍 Anomaly Detection"])
    
    # === POWER PREDICTION TAB ===
    with tab1:
        st.subheader("Energy Usage Prediction (Linear Regression)")
        
        if prediction_model is not None:
            # Get predictions
            predictions = predict_power(df, prediction_model, prediction_scaler)
            next_prediction = predict_next_power(df, prediction_model, prediction_scaler)
            
            # Display current and predicted
            col1, col2 = st.columns(2)
            
            with col1:
                current_power = df['power'].iloc[-1]
                st.metric(
                    "Current Power",
                    f"{current_power:.2f} W"
                )
            
            with col2:
                if next_prediction:
                    st.metric(
                        "Predicted Next Power",
                        f"{next_prediction:.2f} W",
                        delta=f"{next_prediction - current_power:.2f} W"
                    )
            
            # Show prediction chart
            st.subheader("Predicted vs Actual Power")
            
            # Create chart data
            chart_df = pd.DataFrame({
                'Actual': df['power'].values[-len(predictions):],
                'Predicted': predictions
            })
            
            st.line_chart(chart_df)
            
            # Model info
            st.info(f"Model trained on {len(df)} readings")
            
        else:
            st.warning("Not enough data to train prediction model")
    
    # === ANOMALY DETECTION TAB ===
    with tab2:
        st.subheader("Anomaly Detection (Isolation Forest)")
        
        if anomaly_model is not None:
            # Get anomalies
            anomalies = detect_anomalies(df, anomaly_model, anomaly_scaler)
            summary = get_anomaly_summary(df, anomaly_model, anomaly_scaler)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Readings", len(df))
            
            with col2:
                st.metric("Anomalies Detected", summary['total_anomalies'])
            
            with col3:
                st.metric("Anomaly Rate", f"{summary['anomaly_percentage']:.1f}%")
            
            # Show anomaly chart
            st.subheader("Power Readings with Anomalies")
            
            # Mark anomalies
            df['is_anomaly'] = False
            if not anomalies.empty:
                anomaly_indices = anomalies.index
                df.loc[anomaly_indices, 'is_anomaly'] = True
            
            # Color-coded chart
            chart_data = df[['power', 'is_anomaly']].copy()
            chart_data['Normal'] = chart_data['power'].where(~chart_data['is_anomaly'])
            chart_data['Anomaly'] = chart_data['power'].where(chart_data['is_anomaly'])
            
            st.line_chart(chart_data[['Normal', 'Anomaly']])
            
            # Show anomalies table
            if not anomalies.empty:
                st.subheader("Detected Anomalies")
                st.dataframe(
                    anomalies[['timestamp', 'power', 'voltage', 'current']].head(10),
                    use_container_width=True
                )
            else:
                st.success("No anomalies detected - all readings are within normal range!")
                
        else:
            st.warning("Not enough data to train anomaly detection model")
    
    # Footer
    st.markdown("---")
    st.caption("ML Insights | Powered by scikit-learn")


if __name__ == "__main__":
    main()
