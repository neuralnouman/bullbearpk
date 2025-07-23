from flask import Blueprint, jsonify
from agents.stock_agent import get_latest_stock_data

market_routes = Blueprint('market_routes', __name__)

@market_routes.route('/api/market/data', methods=['GET'])
def get_market_data():
    """
    Endpoint to fetch the latest market data
    Returns a JSON object with stocks, market summary, and scrape info
    """
    try:
        # Get the latest stock data
        data = get_latest_stock_data()
        
        if not data or not data.get('stocks'):
            return jsonify({
                'success': False,
                'message': 'No stock data available'
            }), 404
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching market data: {str(e)}'
        }), 500

@market_routes.route('/api/market/stock/<symbol>', methods=['GET'])
def get_stock_details(symbol):
    """
    Endpoint to fetch details for a specific stock
    Returns a JSON object with the stock details
    """
    try:
        # Get the latest stock data
        data = get_latest_stock_data()
        
        # Find the stock with the matching symbol
        stock = next((s for s in data.get('stocks', []) if s.get('code') == symbol), None)
        
        if not stock:
            return jsonify({
                'success': False,
                'message': f'Stock with symbol {symbol} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': stock
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching stock details: {str(e)}'
        }), 500