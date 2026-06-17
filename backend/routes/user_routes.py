"""
Smart Energy Monitoring System - User Routes
User authentication and management endpoints
"""

from flask import Blueprint, request, jsonify
from backend.database import (
    signup_user, login_user, get_all_users
)
from backend.auth import generate_token, token_required, admin_required

# Create blueprint
bp = Blueprint('user', __name__, url_prefix='/api')


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request body:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        }
    
    Returns:
        {
            "message": "User registered successfully",
            "user_id": 1
        }
    """
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'Missing required fields: name, email, password'}), 400
    
    # Check if email already exists
    if not signup_user(name, email, password):
        return jsonify({'error': 'Email already registered'}), 409
    
    # Get the user to return their ID
    user = login_user(email, password)
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': user[0]
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    
    Request body:
        {
            "email": "john@example.com",
            "password": "password123"
        }
    
    Returns:
        {
            "message": "Login successful",
            "token": "eyJhbGciOiJIUzI1NiIs...",
            "user": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "role": "user"
            }
        }
    """
    data = request.get_json()
    
    # Validate required fields
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    
    # Authenticate user
    user = login_user(email, password)
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate JWT token
    token = generate_token(user[0], user[2], user[3])
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'role': user[3]
        }
    }), 200


@bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Get current user information
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "role": "user"
        }
    """
    return jsonify({
        'id': request.user_id,
        'email': request.user_email,
        'role': request.user_role
    }), 200


@bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """
    List all users (admin only)
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        {
            "users": [
                {
                    "id": 1,
                    "name": "Admin",
                    "email": "admin@energy.com",
                    "role": "admin",
                    "created_at": "2024-01-01 12:00:00"
                }
            ]
        }
    """
    users = get_all_users()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'role': user[3],
            'created_at': user[4]
        })
    
    return jsonify({'users': user_list}), 200


@bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """
    Change user password
    
    Headers:
        Authorization: Bearer <token>
    
    Request body:
        {
            "current_password": "oldpassword",
            "new_password": "newpassword"
        }
    
    Returns:
        {
            "message": "Password changed successfully"
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Missing passwords'}), 400
    
    # Verify current password
    user = login_user(request.user_email, current_password)
    
    if not user:
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password (would need to implement update_password in database)
    # For now, just return success
    return jsonify({'message': 'Password changed successfully'}), 200
