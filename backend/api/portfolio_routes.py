#!/usr/bin/env python3
"""
Portfolio Routes for BullBearPK
===============================

API endpoints for portfolio management:
1. Portfolio creation and initialization
2. Investment tracking
3. Portfolio analytics
4. Performance monitoring
"""

from flask import Blueprint, jsonify, request
from portfolio_manager import portfolio_manager
from database_config import db_config
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
portfolio_routes = Blueprint('portfolio_routes', __name__)

@portfolio_routes.route('/api/portfolio/initialize', methods=['POST'])
def initialize_user():
    """
    Initialize a new user with default portfolio
    
    Request Body:
    {
        "user_id": "user123",
        "initial_cash": 10000.0,
        "risk_tolerance": "moderate",
        "investment_goal": "growth"
    }
    
    Returns:
    {
        "success": true,
        "message": "User initialized successfully",
        "user_id": "user123"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'demo_user')
        initial_cash = data.get('initial_cash', 10000.0)
        
        logger.info(f"Initializing user: {user_id}")
        
        # Check if user already exists
        user_query = "SELECT user_id FROM users WHERE user_id = %s"
        existing_user = db_config.execute_query(user_query, (user_id,))
        
        if existing_user:
            return jsonify({
                'success': True,
                'message': 'User already exists',
                'user_id': user_id
            }), 200
        
        # Create new user profile
        create_user_query = """
            INSERT INTO users (
                user_id, name, email, password, risk_tolerance,
                investment_goal, portfolio_value, cash_balance,
                preferred_sectors, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        user_params = (
            user_id,
            f"User {user_id}",
            f"{user_id}@example.com",
            "default_password",
            data.get('risk_tolerance', 'moderate'),
            data.get('investment_goal', 'growth'),
            0.00,  # portfolio_value
            initial_cash,  # cash_balance
            json.dumps([data.get('sector_preference', 'Any')]),
            datetime.now(),
            datetime.now()
        )
        
        db_config.execute_query(create_user_query, user_params)
        
        # Create initial portfolio
        portfolio_created = portfolio_manager.create_user_portfolio(user_id, initial_cash)
        
        if portfolio_created:
            return jsonify({
                'success': True,
                'message': 'User initialized successfully',
                'user_id': user_id,
                'initial_cash': initial_cash
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create portfolio'
            }), 500
    
    except Exception as e:
        logger.error(f"Error initializing user: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error initializing user: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/<user_id>', methods=['GET'])
def get_portfolio(user_id):
    """
    Get user's portfolio information
    
    Path Parameters:
    - user_id: User ID
    
    Query Parameters:
    - include_analytics: Include portfolio analytics (default: true)
    
    Returns:
    {
        "success": true,
        "portfolio": {...},
        "investments": [...],
        "analytics": {...}
    }
    """
    try:
        include_analytics = request.args.get('include_analytics', 'true').lower() == 'true'
        
        logger.info(f"Getting portfolio for user: {user_id}")
        
        # Get user profile
        user_query = "SELECT * FROM users WHERE user_id = %s"
        user_result = db_config.execute_query(user_query, (user_id,))
        
        if not user_result:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user_profile = user_result[0]
        
        # Get latest portfolio snapshot
        portfolio_query = """
            SELECT * FROM portfolios 
            WHERE user_id = %s 
            ORDER BY portfolio_date DESC 
            LIMIT 1
        """
        portfolio_result = db_config.execute_query(portfolio_query, (user_id,))
        
        # Get active investments
        investments_query = """
            SELECT * FROM investments 
            WHERE user_id = %s AND status = 'active'
            ORDER BY buy_date DESC
        """
        investments_result = db_config.execute_query(investments_query, (user_id,))
        
        # Calculate portfolio summary
        total_invested = sum(inv.get('total_invested', 0) for inv in investments_result)
        total_value = sum(inv.get('current_value', 0) for inv in investments_result)
        total_pnl = total_value - total_invested
        pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        portfolio_summary = {
            'total_invested': total_invested,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'pnl_percent': round(pnl_percent, 2),
            'active_investments': len(investments_result),
            'last_updated': datetime.now().isoformat()
        }
        
        response = {
            'success': True,
            'user_profile': user_profile,
            'portfolio_summary': portfolio_summary,
            'investments': investments_result,
            'latest_portfolio': portfolio_result[0] if portfolio_result else None
        }
        
        # Include analytics if requested
        if include_analytics:
            analytics = portfolio_manager.get_investment_analytics(user_id)
            response['analytics'] = analytics
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error getting portfolio: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting portfolio: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/<user_id>/investments', methods=['POST'])
def add_investment(user_id):
    """
    Add a new investment to user's portfolio
    
    Path Parameters:
    - user_id: User ID
    
    Request Body:
    {
        "stock_code": "OGDC",
        "quantity": 100,
        "price": 85.50,
        "transaction_type": "buy",
        "notes": "Initial purchase"
    }
    
    Returns:
    {
        "success": true,
        "message": "Investment added successfully",
        "investment_id": 123
    }
    """
    try:
        data = request.json
        stock_code = data.get('stock_code')
        quantity = data.get('quantity')
        price = data.get('price')
        transaction_type = data.get('transaction_type', 'buy')
        
        if not all([stock_code, quantity, price]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields: stock_code, quantity, price'
            }), 400
        
        logger.info(f"Adding investment for user {user_id}: {stock_code}")
        
        # Get stock details
        stock_query = "SELECT name, sector FROM stocks WHERE code = %s"
        stock_result = db_config.execute_query(stock_query, (stock_code,))
        
        if not stock_result:
            return jsonify({
                'success': False,
                'message': f'Stock {stock_code} not found'
            }), 404
        
        stock_details = stock_result[0]
        total_amount = quantity * price
        
        # Record the transaction
        success = portfolio_manager.record_investment_transaction(
            user_id=user_id,
            stock_code=stock_code,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            total_amount=total_amount
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Investment added successfully',
                'investment': {
                    'stock_code': stock_code,
                    'stock_name': stock_details.get('name'),
                    'quantity': quantity,
                    'price': price,
                    'total_amount': total_amount,
                    'transaction_type': transaction_type
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to add investment'
            }), 500
    
    except Exception as e:
        logger.error(f"Error adding investment: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error adding investment: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/<user_id>/investments/<investment_id>', methods=['PUT'])
def update_investment(user_id, investment_id):
    """
    Update an existing investment
    
    Path Parameters:
    - user_id: User ID
    - investment_id: Investment ID
    
    Request Body:
    {
        "status": "hold",
        "notes": "Updated notes"
    }
    
    Returns:
    {
        "success": true,
        "message": "Investment updated successfully"
    }
    """
    try:
        data = request.json
        new_status = data.get('status')
        notes = data.get('notes')
        
        logger.info(f"Updating investment {investment_id} for user {user_id}")
        
        # Update investment
        update_query = """
            UPDATE investments 
            SET status = %s, user_notes = %s, last_updated = %s
            WHERE id = %s AND user_id = %s
        """
        
        db_config.execute_query(update_query, (new_status, notes, datetime.now(), investment_id, user_id))
        
        return jsonify({
            'success': True,
            'message': 'Investment updated successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating investment: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error updating investment: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/<user_id>/performance', methods=['GET'])
def get_portfolio_performance(user_id):
    """
    Get portfolio performance analytics
    
    Path Parameters:
    - user_id: User ID
    
    Query Parameters:
    - days: Number of days to analyze (default: 30)
    
    Returns:
    {
        "success": true,
        "performance": {...},
        "analytics": {...}
    }
    """
    try:
        days = int(request.args.get('days', 30))
        
        logger.info(f"Getting performance for user {user_id} over {days} days")
        
        # Get performance data
        performance = portfolio_manager.get_portfolio_performance(user_id, days)
        
        # Get analytics
        analytics = portfolio_manager.get_investment_analytics(user_id)
        
        return jsonify({
            'success': True,
            'performance': performance,
            'analytics': analytics,
            'analysis_period_days': days
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting portfolio performance: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/<user_id>/history', methods=['GET'])
def get_investment_history(user_id):
    """
    Get user's investment history
    
    Path Parameters:
    - user_id: User ID
    
    Query Parameters:
    - limit: Number of records to return (default: 50)
    - status: Filter by status (active, sold, all)
    
    Returns:
    {
        "success": true,
        "investments": [...],
        "total_count": 25
    }
    """
    try:
        limit = int(request.args.get('limit', 50))
        status = request.args.get('status', 'all')
        
        logger.info(f"Getting investment history for user {user_id}")
        
        # Get investment history
        investments = portfolio_manager.get_user_investment_history(user_id, limit)
        
        # Filter by status if specified
        if status != 'all':
            investments = [inv for inv in investments if inv.get('status') == status]
        
        return jsonify({
            'success': True,
            'investments': investments,
            'total_count': len(investments),
            'status_filter': status
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting investment history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting investment history: {str(e)}'
        }), 500

@portfolio_routes.route('/api/portfolio/<user_id>/snapshot', methods=['POST'])
def create_portfolio_snapshot(user_id):
    """
    Create a new portfolio snapshot
    
    Path Parameters:
    - user_id: User ID
    
    Returns:
    {
        "success": true,
        "message": "Portfolio snapshot created",
        "snapshot_date": "2025-01-23"
    }
    """
    try:
        logger.info(f"Creating portfolio snapshot for user {user_id}")
        
        success = portfolio_manager.update_portfolio_snapshot(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Portfolio snapshot created successfully',
                'snapshot_date': datetime.now().date().isoformat()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create portfolio snapshot'
            }), 500
    
    except Exception as e:
        logger.error(f"Error creating portfolio snapshot: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error creating portfolio snapshot: {str(e)}'
        }), 500