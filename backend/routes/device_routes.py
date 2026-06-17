"""
Smart Energy Monitoring System - Device Routes
Device management endpoints
"""

from flask import Blueprint, request, jsonify
from backend.database import (
    add_device, get_user_devices, get_all_devices, remove_device,
    rename_device, get_device_status, get_device_by_mac
)
from backend.auth import token_required, admin_required

# Create blueprint
bp = Blueprint('device', __name__, url_prefix='/api')


@bp.route('/register_device', methods=['POST'])
@token_required
def register_device():
    """
    Register a new device for the authenticated user
    
    Headers:
        Authorization: Bearer <token>
    
    Request body:
        {
            "device_name": "Living Room",
            "mac_address": "AA:BB:CC:DD:EE:FF"
        }
    
    Returns:
        {
            "status": "success",
            "message": "Device registered successfully"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    device_name = data.get('device_name')
    mac_address = data.get('mac_address')
    
    if not device_name or not mac_address:
        return jsonify({'error': 'device_name and mac_address are required'}), 400
    
    # Add device for the current user
    if add_device(request.user_id, device_name, mac_address):
        return jsonify({
            'status': 'success',
            'message': 'Device registered successfully'
        }), 201
    else:
        return jsonify({'error': 'Device with this MAC address already exists'}), 409


@bp.route('/device/<mac>/rename', methods=['PUT'])
@token_required
def rename_device_endpoint(mac):
    """
    Rename a device
    
    Headers:
        Authorization: Bearer <token>
    
    Request body:
        {
            "device_name": "New Name"
        }
    
    Returns:
        {
            "status": "success",
            "message": "Device renamed successfully"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    new_name = data.get('device_name')
    
    if not new_name:
        return jsonify({'error': 'device_name is required'}), 400
    
    # Check if device exists and belongs to user
    device = get_device_by_mac(mac)
    
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    # Check if device belongs to the user
    if device[1] != request.user_id and request.user_role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Rename device
    rename_device(mac, new_name)
    
    return jsonify({
        'status': 'success',
        'message': 'Device renamed successfully'
    }), 200


@bp.route('/devices/<int:user_id>', methods=['GET'])
@token_required
def get_devices(user_id):
    """
    Get all devices for a user with online/offline status
    
    Headers:
        Authorization: Bearer <token>
    
    URL Parameters:
        user_id: ID of the user
    
    Returns:
        {
            "devices": [
                {
                    "id": 1,
                    "device_name": "Living Room",
                    "mac_address": "AA:BB:CC:DD:EE:FF",
                    "last_seen": "2024-01-01 12:00:00",
                    "created_at": "2024-01-01 10:00:00",
                    "status": "online"
                }
            ]
        }
    
    Status logic:
        - If last_seen > 60 seconds → "offline"
        - If last_seen ≤ 60 seconds → "online"
    """
    # Check authorization - users can only view their own devices
    if user_id != request.user_id and request.user_role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    devices = get_user_devices(user_id)
    
    device_list = []
    for device in devices:
        # Get detailed status for each device
        status_info = get_device_status(device[1])
        
        device_list.append({
            'id': status_info['id'],
            'device_name': status_info['device_name'],
            'mac_address': status_info['mac_address'],
            'last_seen': status_info['last_seen'],
            'created_at': status_info['created_at'],
            'status': status_info['status']
        })
    
    return jsonify({'devices': device_list}), 200


@bp.route('/device/<mac>/status', methods=['GET'])
@token_required
def get_device_status_endpoint(mac):
    """
    Get device status (online/offline)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "id": 1,
            "device_name": "Living Room",
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "last_seen": "2024-01-01 12:00:00",
            "status": "online"
        }
    """
    status_info = get_device_status(mac)
    
    if not status_info:
        return jsonify({'error': 'Device not found'}), 404
    
    # Check authorization
    device = get_device_by_mac(mac)
    if device[1] != request.user_id and request.user_role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(status_info), 200


@bp.route('/device/list', methods=['GET'])
def list_user_devices():
    """
    List all devices for the default user (no auth required for dashboard)
    
    Returns:
        {
            "devices": [
                {
                    "device_name": "Living Room",
                    "mac_address": "AA:BB:CC:DD:EE:FF",
                    "last_seen": "2024-01-01 12:00:00"
                }
            ]
        }
    """
    # Get devices for admin user (user_id=1) by default
    devices = get_user_devices(1)
    
    device_list = []
    for device in devices:
        device_list.append({
            'device_name': device[0],
            'mac_address': device[1],
            'last_seen': device[2]
        })
    
    return jsonify({'devices': device_list}), 200


@bp.route('/device/list/auth', methods=['GET'])
@token_required
def list_user_devices_auth():
    """
    List all devices for the authenticated user
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "devices": [
                {
                    "device_name": "Living Room",
                    "mac_address": "AA:BB:CC:DD:EE:FF",
                    "last_seen": "2024-01-01 12:00:00"
                }
            ]
        }
    """
    devices = get_user_devices(request.user_id)
    
    device_list = []
    for device in devices:
        device_list.append({
            'device_name': device[0],
            'mac_address': device[1],
            'last_seen': device[2]
        })
    
    return jsonify({'devices': device_list}), 200


@bp.route('/device/list/all', methods=['GET'])
@admin_required
def list_all_devices():
    """
    List all devices on the platform (admin only)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "devices": [
                {
                    "id": 1,
                    "device_name": "Living Room",
                    "mac_address": "AA:BB:CC:DD:EE:FF",
                    "owner": "John Doe",
                    "created_at": "2024-01-01 12:00:00"
                }
            ]
        }
    """
    devices = get_all_devices()
    
    device_list = []
    for device in devices:
        device_list.append({
            'id': device[0],
            'device_name': device[1],
            'mac_address': device[2],
            'owner': device[3],
            'created_at': device[4]
        })
    
    return jsonify({'devices': device_list}), 200


@bp.route('/device/remove', methods=['DELETE'])
@token_required
def delete_device():
    """
    Remove a device
    
    Headers:
        Authorization: Bearer <token>
    
    Request body:
        {
            "mac_address": "AA:BB:CC:DD:EE:FF"
        }
    
    Returns:
        {
            "status": "success",
            "message": "Device removed successfully"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    mac_address = data.get('mac_address')
    
    if not mac_address:
        return jsonify({'error': 'mac_address is required'}), 400
    
    # Check if device belongs to user
    device = get_device_by_mac(mac_address)
    if device and device[1] != request.user_id and request.user_role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    remove_device(mac_address)
    
    return jsonify({
        'status': 'success',
        'message': 'Device removed successfully'
    }), 200
