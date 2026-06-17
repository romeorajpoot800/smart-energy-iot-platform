"""
ML Module for Smart Energy Monitoring
- Energy prediction using Linear Regression
- Anomaly detection using Isolation Forest
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import pickle
import os

# Model storage
MODEL_DIR = "models"


def prepare_features(df):
    """
    Prepare features for ML models
    
    Creates time-based features from timestamps
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Lag features (previous readings)
    df['power_lag1'] = df['power'].shift(1)
    df['power_lag2'] = df['power'].shift(2)
    df['power_lag3'] = df['power'].shift(3)
    
    # Rolling averages
    df['power_rolling_mean'] = df['power'].rolling(window=5).mean()
    df['power_rolling_std'] = df['power'].rolling(window=5).std()
    
    # Drop rows with NaN
    df = df.dropna()
    
    return df


def train_power_prediction_model(df):
    """
    Train Linear Regression model to predict power usage
    
    Args:
        df: DataFrame with power readings and timestamps
        
    Returns:
        Trained model and scaler
    """
    # Prepare features
    df_features = prepare_features(df)
    
    if len(df_features) < 10:
        return None, None
    
    # Feature columns
    feature_cols = ['hour', 'minute', 'day_of_week', 'is_weekend', 
                   'power_lag1', 'power_lag2', 'power_lag3',
                   'power_rolling_mean', 'power_rolling_std']
    
    # Target
    X = df_features[feature_cols].values
    y = df_features['power'].values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = LinearRegression()
    model.fit(X_scaled, y)
    
    return model, scaler


def predict_power(df, model, scaler):
    """
    Predict power usage
    
    Args:
        df: DataFrame with recent readings
        model: Trained Linear Regression model
        scaler: Feature scaler
        
    Returns:
        Array of predictions
    """
    df_features = prepare_features(df)
    
    if len(df_features) < 1 or model is None:
        return []
    
    feature_cols = ['hour', 'minute', 'day_of_week', 'is_weekend', 
                   'power_lag1', 'power_lag2', 'power_lag3',
                   'power_rolling_mean', 'power_rolling_std']
    
    X = df_features[feature_cols].values
    X_scaled = scaler.transform(X)
    
    predictions = model.predict(X_scaled)
    return predictions.tolist()


def predict_next_power(df, model, scaler):
    """
    Predict next power reading
    
    Args:
        df: DataFrame with recent readings
        model: Trained model
        scaler: Feature scaler
        
    Returns:
        Predicted power value
    """
    predictions = predict_power(df, model, scaler)
    
    if predictions:
        return predictions[-1]
    
    return None


def train_anomaly_detector(df):
    """
    Train Isolation Forest model for anomaly detection
    
    Args:
        df: DataFrame with sensor readings
        
    Returns:
        Trained model and scaler
    """
    if len(df) < 20:
        return None, None
    
    # Use power, voltage, current for anomaly detection
    features = df[['power', 'voltage', 'current']].copy()
    
    # Handle any missing values
    features = features.dropna()
    
    if len(features) < 20:
        return None, None
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    # Train Isolation Forest
    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,  # Expect ~10% anomalies
        random_state=42
    )
    model.fit(X_scaled)
    
    return model, scaler


def detect_anomalies(df, model, scaler):
    """
    Detect anomalies using Isolation Forest
    
    Args:
        df: DataFrame with sensor readings
        model: Trained Isolation Forest model
        scaler: Feature scaler
        
    Returns:
        DataFrame with anomaly predictions
    """
    if model is None or len(df) < 20:
        return pd.DataFrame()
    
    features = df[['power', 'voltage', 'current']].copy()
    features = features.dropna()
    
    if len(features) < 20:
        return pd.DataFrame()
    
    X_scaled = scaler.transform(features)
    
    # Predict (-1 = anomaly, 1 = normal)
    predictions = model.predict(X_scaled)
    
    # Get anomaly scores
    scores = model.decision_function(X_scaled)
    
    # Create results DataFrame
    results = df.copy()
    results['is_anomaly'] = predictions == -1
    results['anomaly_score'] = scores
    
    # Filter anomalies
    anomalies = results[results['is_anomaly'] == True]
    
    return anomalies


def get_anomaly_summary(df, model, scaler):
    """
    Get summary of anomalies
    
    Args:
        df: DataFrame with sensor readings
        model: Trained model
        scaler: Feature scaler
        
    Returns:
        Dictionary with summary statistics
    """
    anomalies = detect_anomalies(df, model, scaler)
    
    if len(anomalies) == 0:
        return {
            'total_anomalies': 0,
            'anomaly_percentage': 0,
            'avg_anomaly_power': None,
            'max_anomaly_power': None
        }
    
    return {
        'total_anomalies': len(anomalies),
        'anomaly_percentage': (len(anomalies) / len(df)) * 100,
        'avg_anomaly_power': anomalies['power'].mean(),
        'max_anomaly_power': anomalies['power'].max()
    }


# Save/Load functions
def save_model(model, scaler, device_mac, model_type='prediction'):
    """Save trained model to disk"""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    filename = f"{MODEL_DIR}/{device_mac}_{model_type}.pkl"
    
    with open(filename, 'wb') as f:
        pickle.dump({'model': model, 'scaler': scaler}, f)


def load_model(device_mac, model_type='prediction'):
    """Load trained model from disk"""
    filename = f"{MODEL_DIR}/{device_mac}_{model_type}.pkl"
    
    if not os.path.exists(filename):
        return None, None
    
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    
    return data['model'], data['scaler']


if __name__ == "__main__":
    # Test the module
    print("ML Module for Smart Energy Monitoring")
    print("=" * 50)
    print("Functions available:")
    print("- train_power_prediction_model(df)")
    print("- predict_power(df, model, scaler)")
    print("- train_anomaly_detector(df)")
    print("- detect_anomalies(df, model, scaler)")
    print("- get_anomaly_summary(df, model, scaler)")
