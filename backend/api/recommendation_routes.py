from flask import Blueprint, jsonify, request
from manager_agent import hybrid_input_workflow
from agents.stock_agent import EnhancedDatabaseManager
import json
import logging
from datetime import datetime

recommendation_routes = Blueprint('recommendation_routes', __name__)

@recommendation_routes.route('/api/analysis/recommendations', methods=['POST'])
def get_recommendations():
    """
    Endpoint to get investment recommendations based on user preferences
    """
    try:
        data = request.json
        user_input = data.get('user_input', {})
        user_id = data.get('user_id', 'demo_user')
        
        # Check if refresh is requested
        refresh_data = data.get('refresh_data', False)
        
        # Get recommendations from manager agent
        result = hybrid_input_workflow(user_input, '', user_id, refresh_data=refresh_data)
        
        # Try to store recommendations in database
        try:
            db_manager = EnhancedDatabaseManager()
            with db_manager.get_connection() as conn:
                for rec in result['recommendations']:
                    # Extract stock symbol from company field (format: "SYMBOL - Company Name")
                    company_parts = rec['company'].split(' - ', 1)
                    stock_symbol = company_parts[0] if len(company_parts) > 0 else ''
                    company_name = company_parts[1] if len(company_parts) > 1 else rec['company']
                    
                    # Parse allocation amount
                    allocation_text = rec.get('allocation_suggestion', '0 PKR')
                    allocation_amount = float(''.join(c for c in allocation_text if c.isdigit() or c == '.') or 0)
                    
                    conn.execute('''
                        INSERT INTO recommendations (
                            user_id, stock_symbol, company_name, recommendation_type,
                            reason, risk_level, expected_return, allocation_amount, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        stock_symbol,
                        company_name,
                        'BUY',  # Default to BUY for now
                        rec.get('recommendation_reason', ''),
                        rec.get('risk', 'Medium'),
                        rec.get('expected_return', '0%').replace('%', ''),
                        allocation_amount,
                        datetime.now().isoformat()
                    ))
                conn.commit()
        except Exception as db_error:
            # Log the database error but don't fail the request
            logging.error(f"Database error: {str(db_error)}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logging.error(f"Error generating recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error generating recommendations: {str(e)}'
        }), 500

@recommendation_routes.route('/api/analysis/recommendations/history', methods=['GET'])
def get_recommendation_history():
    """
    Endpoint to get user's recommendation history
    """
    try:
        user_id = request.args.get('user_id', 'demo_user')
        
        db_manager = EnhancedDatabaseManager()
        recommendations = []
        
        with db_manager.get_connection() as conn:
            results = conn.execute('''
                SELECT * FROM recommendations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (user_id,)).fetchall()
            
            if results:
                for row in results:
                    recommendations.append({
                        'id': row['id'],
                        'stock_symbol': row['stock_symbol'],
                        'company_name': row['company_name'],
                        'recommendation_type': row['recommendation_type'],
                        'reason': row['reason'],
                        'risk': row['risk_level'],
                        'expected_return': f"{row['expected_return']}%",
                        'allocation_suggestion': f"{row['allocation_amount']} PKR",
                        'timestamp': row['timestamp']
                    })
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching recommendation history: {str(e)}'
        }), 500