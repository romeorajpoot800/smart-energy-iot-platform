"""
Smart Energy Monitoring System - Alert Routes
Alert management endpoints
"""

from flask import Blueprint, request, jsonify
from backend.database import get_user_alerts, acknowledge_alert, get_unacknowledged_alerts
from backend.auth import token_required, admin_required

# Create blueprint
bp = Blueprint('alert', __name__, url_prefix='/api')


@bp.route('/alerts', methods=['GET'])
@token_required
def list_alerts():
    """
    List all alerts for the authenticated user
    
    Headers:
        Authorization: Bearer <token>
    
    Query parameters:
        acknowledged: Filter by acknowledged status (true/false)
    
    Returns:
        {
            "alerts": [
                {
                    "id": 1,
                    "mac_address": "AA:BB:CC:DD:EE:FF",
                    "alert_type": "OVERLOAD",
                    "message": "Power exceeded threshold",
                    "value": 750.0,
                    "threshold": 650.0,
                    "created_at": "2024-01-01 12:00:00",
                    "acknowledged": false
                }
            ]
        }
    """
    alerts = get_user_alerts(request.user_id)
    
    # Filter by acknowledged status if provided
    acknowledged_filter = request.args.get('acknowledged')
    
    alert_list = []
    for alert in alerts:
        if acknowledged_filter is not None:
            ack = acknowledged_filter.lower() == 'true'
            if alert[7] != ack:
                continue
        
        alert_list.append({
            'id': alert[0],
            'mac_address': alert[1],
            'alert_type': alert[2],
            'message': alert[3],
            'value': alert[4],
            'threshold': alert[5],
            'created_at': alert[6],
            'acknowledged': bool(alert[7])
        })
    
    return jsonify({'alerts': alert_list}), 200


@bp.route('/alerts/count', methods=['GET'])
@token_required
def get_alert_count():
    """
    Get count of unacknowledged alerts
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "unacknowledged_count": 5
        }
    """
    count = get_unacknowledged_alerts(request.user_id)
    
    return jsonify({'unacknowledged_count': count}), 200


@bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@token_required
def acknowledge_user_alert(alert_id):
    """
    Acknowledge an alert
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "status": "success",
            "message": "Alert acknowledged"
        }
    """
    acknowledge_alert(alert_id)
    
    return jsonify({
        'status': 'success',
        'message': 'Alert acknowledged'
    }), 200


@bp.route('/alerts/all', methods=['GET'])
@admin_required
def list_all_alerts():
    """
    List all alerts on the platform (admin only)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "alerts": [...]
        }
    """
    # This would need a get_all_alerts function in database
    # For now, return a placeholder
    return jsonify({
        'alerts': [],
        'message': 'Admin alerts view - requires database function'
    }), 200
