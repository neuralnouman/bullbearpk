#!/usr/bin/env python3
"""
Investment Routes for BullBearPK
===============================

API endpoints for portfolio management and investment tracking:
1. Portfolio creation and management
2. Investment transaction recording
3. Portfolio performance analytics
4. Investment history tracking
5. User investment decisions after recommendations
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from portfolio_manager import portfolio_manager
from agents.manager_record_agent import handle_user_investment_decision

logger = logging.getLogger(__name__)

investment_bp = Blueprint('investment', __name__)

@investment_bp.route('/portfolio/create', methods=['POST'])
def create_portfolio():
    """Create a new portfolio for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        initial_cash = data.get('initial_cash', 10000.0)
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        success = portfolio_manager.create_user_portfolio(user_id, initial_cash)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Portfolio created for user {user_id}',
                'user_id': user_id,
                'initial_cash': initial_cash
            }), 201
        else:
            return jsonify({'error': 'Failed to create portfolio'}), 500
            
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/transaction/record', methods=['POST'])
def record_transaction():
    """Record an investment transaction"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        stock_code = data.get('stock_code')
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')
        price = data.get('price')
        
        if not all([user_id, stock_code, transaction_type, quantity, price]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        total_amount = quantity * price
        
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
                'message': f'Transaction recorded successfully',
                'transaction': {
                    'user_id': user_id,
                    'stock_code': stock_code,
                    'transaction_type': transaction_type,
                    'quantity': quantity,
                    'price': price,
                    'total_amount': total_amount,
                    'timestamp': datetime.now().isoformat()
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to record transaction'}), 500
            
    except Exception as e:
        logger.error(f"Error recording transaction: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/portfolio/<user_id>/status', methods=['GET'])
def get_portfolio_status(user_id):
    """Get current portfolio status"""
    try:
        # Get portfolio performance
        performance = portfolio_manager.get_portfolio_performance(user_id, days=30)
        
        # Get investment analytics
        analytics = portfolio_manager.get_investment_analytics(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'performance': performance,
            'analytics': analytics,
            'last_updated': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting portfolio status: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/portfolio/<user_id>/history', methods=['GET'])
def get_investment_history(user_id):
    """Get investment history for a user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        investments = portfolio_manager.get_user_investment_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'investments': investments,
            'total_investments': len(investments)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting investment history: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/portfolio/<user_id>/performance', methods=['GET'])
def get_portfolio_performance(user_id):
    """Get portfolio performance analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        performance = portfolio_manager.get_portfolio_performance(user_id, days)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'performance': performance,
            'period_days': days
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/portfolio/<user_id>/analytics', methods=['GET'])
def get_investment_analytics(user_id):
    """Get detailed investment analytics"""
    try:
        analytics = portfolio_manager.get_investment_analytics(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting investment analytics: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/investment/<user_id>/<stock_code>/update', methods=['PUT'])
def update_investment_status(user_id, stock_code):
    """Update investment status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        success = portfolio_manager.update_investment_status(user_id, stock_code)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Investment status updated for {stock_code}',
                'user_id': user_id,
                'stock_code': stock_code,
                'new_status': new_status
            }), 200
        else:
            return jsonify({'error': 'Failed to update investment status'}), 500
            
    except Exception as e:
        logger.error(f"Error updating investment status: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/portfolio/<user_id>/snapshot', methods=['POST'])
def create_portfolio_snapshot(user_id):
    """Create a portfolio snapshot"""
    try:
        success = portfolio_manager.update_portfolio_snapshot(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Portfolio snapshot created for user {user_id}',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Failed to create portfolio snapshot'}), 500
            
    except Exception as e:
        logger.error(f"Error creating portfolio snapshot: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/portfolio/<user_id>/holdings', methods=['GET'])
def get_portfolio_holdings(user_id):
    """Get current portfolio holdings"""
    try:
        # Get active investments
        investments = portfolio_manager.get_user_investment_history(user_id, limit=100)
        active_holdings = [inv for inv in investments if inv.get('status') == 'active']
        
        total_value = sum(inv.get('current_value', 0) for inv in active_holdings)
        total_invested = sum(inv.get('total_invested', 0) for inv in active_holdings)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'holdings': active_holdings,
            'summary': {
                'total_holdings': len(active_holdings),
                'total_value': total_value,
                'total_invested': total_invested,
                'unrealized_pnl': total_value - total_invested
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting portfolio holdings: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/portfolio/<user_id>/sector-allocation', methods=['GET'])
def get_sector_allocation(user_id):
    """Get portfolio sector allocation"""
    try:
        investments = portfolio_manager.get_user_investment_history(user_id, limit=100)
        active_holdings = [inv for inv in investments if inv.get('status') == 'active']
        
        sector_allocation = {}
        for holding in active_holdings:
            sector = holding.get('sector', 'Unknown')
            value = holding.get('current_value', 0)
            
            if sector in sector_allocation:
                sector_allocation[sector] += value
            else:
                sector_allocation[sector] = value
        
        total_value = sum(sector_allocation.values())
        
        # Calculate percentages
        sector_percentages = {}
        for sector, value in sector_allocation.items():
            sector_percentages[sector] = (value / total_value * 100) if total_value > 0 else 0
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'sector_allocation': sector_allocation,
            'sector_percentages': sector_percentages,
            'total_value': total_value
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting sector allocation: {e}")
        return jsonify({'error': str(e)}), 500

@investment_bp.route('/portfolio/<user_id>/top-holdings', methods=['GET'])
def get_top_holdings(user_id):
    """Get top holdings by value"""
    try:
        limit = request.args.get('limit', 10, type=int)
        investments = portfolio_manager.get_user_investment_history(user_id, limit=100)
        active_holdings = [inv for inv in investments if inv.get('status') == 'active']
        
        # Sort by current value
        sorted_holdings = sorted(active_holdings, key=lambda x: x.get('current_value', 0), reverse=True)
        top_holdings = sorted_holdings[:limit]
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'top_holdings': top_holdings,
            'limit': limit
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting top holdings: {e}")
        return jsonify({'error': str(e)}), 500

# New endpoint for handling user investment decisions after recommendations
@investment_bp.route('/user-decision', methods=['POST'])
async def handle_user_decision():
    """Handle user investment decisions after recommendations"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        decision_type = data.get('decision_type')
        stock_code = data.get('stock_code')
        quantity = data.get('quantity')
        price = data.get('price')
        recommendation_id = data.get('recommendation_id')
        
        if not all([user_id, decision_type, stock_code]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Call the manager record agent
        result = await handle_user_investment_decision(
            user_id=user_id,
            decision_type=decision_type,
            stock_code=stock_code,
            quantity=quantity,
            price=price,
            recommendation_id=recommendation_id
        )
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': result.get('message'),
                'transaction_id': result.get('transaction_id'),
                'transaction_type': result.get('transaction_type'),
                'portfolio_updated': result.get('portfolio_updated'),
                'portfolio_summary': result.get('portfolio_summary'),
                'timestamp': result.get('timestamp')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('message'),
                'status': result.get('status')
            }), 400
            
    except Exception as e:
        logger.error(f"Error handling user decision: {e}")
        return jsonify({'error': str(e)}), 500

# Batch decision processing endpoint
@investment_bp.route('/user-decisions/batch', methods=['POST'])
async def handle_batch_decisions():
    """Handle multiple user investment decisions at once"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        decisions = data.get('decisions', [])
        
        if not user_id or not decisions:
            return jsonify({'error': 'User ID and decisions are required'}), 400
        
        results = []
        
        for decision in decisions:
            try:
                decision_type = decision.get('decision_type')
                stock_code = decision.get('stock_code')
                quantity = decision.get('quantity')
                price = decision.get('price')
                recommendation_id = decision.get('recommendation_id')
                
                if not all([decision_type, stock_code]):
                    results.append({
                        'decision': decision,
                        'status': 'error',
                        'message': 'Missing required fields'
                    })
                    continue
                
                # Call the manager record agent
                result = await handle_user_investment_decision(
                    user_id=user_id,
                    decision_type=decision_type,
                    stock_code=stock_code,
                    quantity=quantity,
                    price=price,
                    recommendation_id=recommendation_id
                )
                
                results.append({
                    'decision': decision,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Error processing decision {decision}: {e}")
                results.append({
                    'decision': decision,
                    'status': 'error',
                    'message': str(e)
                })
        
        successful_decisions = len([r for r in results if r.get('result', {}).get('status') == 'success'])
        failed_decisions = len(results) - successful_decisions
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'total_decisions': len(results),
            'successful_decisions': successful_decisions,
            'failed_decisions': failed_decisions,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error handling batch decisions: {e}")
        return jsonify({'error': str(e)}), 500 