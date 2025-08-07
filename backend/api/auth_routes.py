#!/usr/bin/env python3
"""
Authentication Routes for BullBearPK
===================================

API endpoints for user authentication and management:
1. User registration with investment preferences
2. User login with email/password
3. User profile management
4. Password validation and security
5. Session management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import hashlib
import secrets
import logging
from database_config import db_config
import json

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"user_{secrets.token_hex(8)}"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        name = data.get('name').strip()
        email = data.get('email').strip().lower()
        password = data.get('password')
        risk_tolerance = data.get('risk_tolerance', 'moderate')
        investment_goal = data.get('investment_goal', 'growth')
        preferred_sectors = data.get('preferred_sectors', [])
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        existing_user = db_config.execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )
        
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Generate user ID and hash password
        user_id = generate_user_id()
        hashed_password = hash_password(password)
        
        # Create user in database
        insert_query = """
            INSERT INTO users (
                user_id, name, email, password, risk_tolerance,
                investment_goal, preferred_sectors, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        user_params = (
            user_id,
            name,
            email,
            hashed_password,
            risk_tolerance,
            investment_goal,
            json.dumps(preferred_sectors),
            datetime.now(),
            datetime.now()
        )
        
        db_config.execute_query(insert_query, user_params)
        
        # Create initial portfolio for user
        portfolio_query = """
            INSERT INTO portfolios (
                user_id, total_value, total_invested, cash_balance,
                available_cash, portfolio_date, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        portfolio_params = (
            user_id,
            0.00,  # total_value
            0.00,  # total_invested
            0.00,  # cash_balance (starting cash - changed from 10000 to 0)
            0.00,  # available_cash (changed from 10000 to 0)
            datetime.now().date(),
            datetime.now()
        )
        
        db_config.execute_query(portfolio_query, portfolio_params)
        
        # Get created user data
        user_data = db_config.execute_query(
            "SELECT user_id, name, email, risk_tolerance, investment_goal, preferred_sectors, created_at FROM users WHERE user_id = %s",
            (user_id,)
        )
        
        if user_data:
            user = user_data[0]
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user['user_id'],
                    'name': user['name'],
                    'email': user['email'],
                    'risk_tolerance': user['risk_tolerance'],
                    'investment_goal': user['investment_goal'],
                    'preferred_sectors': json.loads(user['preferred_sectors']) if user['preferred_sectors'] else [],
                    'created_at': user['created_at'].isoformat() if user['created_at'] else datetime.now().isoformat(),
                    'portfolio': {
                        'total_value': 0.00,
                        'total_invested': 0.00,
                        'cash_balance': 0.00,
                        'available_cash': 0.00
                    }
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        logger.error(f"Error in user registration: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data.get('email').strip().lower()
        password = data.get('password')
        
        # Get user from database
        user_data = db_config.execute_query(
            "SELECT user_id, name, email, password, risk_tolerance, investment_goal, preferred_sectors, created_at FROM users WHERE email = %s",
            (email,)
        )
        
        if not user_data:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = user_data[0]
        
        # Verify password
        if not verify_password(password, user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Get user portfolio
        portfolio_data = db_config.execute_query(
            "SELECT total_value, total_invested, cash_balance, available_cash FROM portfolios WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
            (user['user_id'],)
        )
        
        portfolio = {
            'total_value': 0.00,
            'total_invested': 0.00,
            'cash_balance': 10000.00,
            'available_cash': 10000.00
        }
        
        if portfolio_data:
            portfolio = portfolio_data[0]
        
        # Return user data
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'risk_tolerance': user['risk_tolerance'],
                'investment_goal': user['investment_goal'],
                'preferred_sectors': json.loads(user['preferred_sectors']) if user['preferred_sectors'] else [],
                'created_at': user['created_at'].isoformat() if user['created_at'] else datetime.now().isoformat(),
                'portfolio': portfolio
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in user login: {e}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        # Get user ID from query parameter or header
        user_id = request.args.get('user_id') or request.headers.get('X-User-ID')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Get user data
        user_data = db_config.execute_query(
            "SELECT user_id, name, email, risk_tolerance, investment_goal, preferred_sectors, created_at FROM users WHERE user_id = %s",
            (user_id,)
        )
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        user = user_data[0]
        
        # Get user portfolio
        portfolio_data = db_config.execute_query(
            "SELECT total_value, total_invested, cash_balance, available_cash FROM portfolios WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        
        portfolio = {
            'total_value': 0.00,
            'total_invested': 0.00,
            'cash_balance': 10000.00,
            'available_cash': 10000.00
        }
        
        if portfolio_data:
            portfolio = portfolio_data[0]
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'risk_tolerance': user['risk_tolerance'],
                'investment_goal': user['investment_goal'],
                'preferred_sectors': json.loads(user['preferred_sectors']) if user['preferred_sectors'] else [],
                'created_at': user['created_at'].isoformat() if user['created_at'] else datetime.now().isoformat(),
                'portfolio': portfolio
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # Check if user exists
        existing_user = db_config.execute_query(
            "SELECT user_id FROM users WHERE user_id = %s",
            (user_id,)
        )
        
        if not existing_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields
        update_fields = []
        update_params = []
        
        if data.get('name'):
            update_fields.append('name = %s')
            update_params.append(data['name'])
        
        if data.get('risk_tolerance'):
            update_fields.append('risk_tolerance = %s')
            update_params.append(data['risk_tolerance'])
        
        if data.get('investment_goal'):
            update_fields.append('investment_goal = %s')
            update_params.append(data['investment_goal'])
        
        if data.get('preferred_sectors'):
            update_fields.append('preferred_sectors = %s')
            update_params.append(json.dumps(data['preferred_sectors']))
        
        if update_fields:
            update_fields.append('updated_at = %s')
            update_params.append(datetime.now())
            update_params.append(user_id)
            
            update_query = f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE user_id = %s
            """
            
            db_config.execute_query(update_query, update_params)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (client-side session management)"""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200 