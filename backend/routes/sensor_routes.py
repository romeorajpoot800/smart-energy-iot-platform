"""
Smart Energy Monitoring System - Sensor Routes
Energy data ingestion endpoints
"""

from flask import Blueprint, request, jsonify
from backend.database import insert_energy_log, get_device_logs, update_last_seen, insert_alert, get_device_by_mac, add_device
from backend.auth import token_required

# Create blueprint
bp = Blueprint('sensor', __name__, url_prefix='/api')

# Power threshold for overload detection
POWER_THRESHOLD = 650  # Watts


@bp.route('/sensor_data', methods=['POST'])
def receive_sensor_data():
    """
    Receive IoT sensor data endpoint
    
    Request body:
        {
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "voltage": 220.5,
            "current": 2.5,
            "power": 550.0
        }
    
    Returns:
        {
            "status": "success",
            "message": "Sensor data stored",
            "alert": null  // or {"type": "OVERLOAD", "message": "..."}
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    mac = data.get('mac_address')
    voltage = data.get('voltage')
    current = data.get('current')
    power = data.get('power')
    
    if not mac:
        return jsonify({'error': 'mac_address is required'}), 400
    
    # Auto-create device if it doesn't exist
    device = get_device_by_mac(mac)
    if not device:
        # Create device with default admin user (user_id=1)
        device_name = f"Device_{mac.replace(':', '')[-6:]}"
        add_device(1, device_name, mac)
    
    # Insert energy log
    insert_energy_log(mac, voltage, current, power)
    
    # Update device last_seen timestamp
    update_last_seen(mac)
    
    # Check for overload condition
    alert = None
    if power and power > POWER_THRESHOLD:
        # Get device to find user_id for alert
        device = get_device_by_mac(mac)
        
        if device:
            user_id = device[1]
            message = f"Power {power}W exceeded threshold {POWER_THRESHOLD}W"
            
            # Insert alert
            insert_alert(
                user_id=user_id,
                mac=mac,
                alert_type='OVERLOAD',
                message=message,
                value=power,
                threshold=POWER_THRESHOLD
            )
            
            alert = {
                'type': 'OVERLOAD',
                'message': message,
                'value': power,
                'threshold': POWER_THRESHOLD
            }
    
    return jsonify({
        'status': 'success',
        'message': 'Sensor data stored',
        'alert': alert
    }), 201


@bp.route('/energy/data', methods=['POST'])
def receive_energy_data():
    """
    Receive energy sensor data from IoT devices
    
    Request body:
        {
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "voltage": 220.5,
            "current": 2.5,
            "power": 550.0
        }
    
    Returns:
        {
            "status": "success",
            "message": "Energy data logged"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    mac = data.get('mac_address')
    voltage = data.get('voltage')
    current = data.get('current')
    power = data.get('power')
    
    if not mac:
        return jsonify({'error': 'mac_address is required'}), 400
    
    # Auto-create device if it doesn't exist
    device = get_device_by_mac(mac)
    if not device:
        # Create device with default admin user (user_id=1)
        device_name = f"Device_{mac.replace(':', '')[-6:]}"
        add_device(1, device_name, mac)
    
    # Insert energy log
    insert_energy_log(mac, voltage, current, power)
    
    # Update device last_seen timestamp
    update_last_seen(mac)
    
    return jsonify({
        'status': 'success',
        'message': 'Energy data logged'
    }), 201


@bp.route('/readings', methods=['POST'])
def create_reading():
    """Generic endpoint to accept full reading payload and store in DB.

    Expected JSON:
        {
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "voltage": 220.5,
            "current": 2.5,
            "power": 550.0,
            "energy_kwh": 0.0015,
            "relay_state": 0
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    mac = data.get('mac_address')
    voltage = data.get('voltage')
    current = data.get('current')
    power = data.get('power')
    energy_kwh = data.get('energy_kwh', 0)
    relay_state = data.get('relay_state', 0)

    if not mac:
        return jsonify({'error': 'mac_address is required'}), 400

    # Auto-create device if it doesn't exist
    device = get_device_by_mac(mac)
    if not device:
        device_name = f"Device_{mac.replace(':', '')[-6:]}"
        add_device(1, device_name, mac)

    # Insert energy log (supports energy_kwh and relay_state)
    insert_energy_log(mac, voltage, current, power, energy_kwh, relay_state)

    # Update device last_seen timestamp
    update_last_seen(mac)

    return jsonify({'status': 'success', 'message': 'Reading stored'}), 201


@bp.route('/energy/logs/<mac_address>', methods=['GET'])
def get_logs(mac_address):
    """
    Get energy logs for a specific device
    
    Query parameters:
        limit: Number of logs to return (default: 100)
    
    Returns:
        {
            "logs": [
                {
                    "voltage": 220.5,
                    "current": 2.5,
                    "power": 550.0,
                    "timestamp": "2024-01-01 12:00:00"
                }
            ]
        }
    """
    limit = request.args.get('limit', 100, type=int)
    
    logs = get_device_logs(mac_address, limit)
    
    result = []
    for log in logs:
        result.append({
            'voltage': log[0],
            'current': log[1],
            'power': log[2],
            'timestamp': log[3]
        })
    
    return jsonify({'logs': result}), 200


@bp.route('/energy/latest/<mac_address>', methods=['GET'])
def get_latest(mac_address):
    """
    Get latest energy reading for a device
    
    Returns:
        {
            "voltage": 220.5,
            "current": 2.5,
            "power": 550.0,
            "timestamp": "2024-01-01 12:00:00"
        }
    """
    logs = get_device_logs(mac_address, 1)
    
    if not logs:
        return jsonify({'error': 'No data found'}), 404
    
    log = logs[0]
    return jsonify({
        'voltage': log[0],
        'current': log[1],
        'power': log[2],
        'timestamp': log[3]
    }), 200
