from flask import Blueprint, jsonify, request
from agents.stock_agent import get_latest_stock_data
from agents.fin_scraper import scrape_stocks_tool
import json
from datetime import datetime

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

@market_routes.route('/api/stocks/search', methods=['GET'])
def search_stocks():
    """
    Endpoint to search for stocks by query
    Returns a JSON object with matching stocks
    """
    try:
        query = request.args.get('q', '').lower()
        
        # Get the latest stock data
        data = get_latest_stock_data()
        
        if not query:
            return jsonify(data), 200
        
        # Filter stocks by query
        filtered_stocks = [s for s in data.get('stocks', []) if 
                          query in (s.get('name') or '').lower() or 
                          query in (s.get('code') or '').lower() or
                          query in (s.get('sector') or '').lower()]
        
        # Return filtered data
        filtered_data = {
            'scrape_info': data.get('scrape_info', {}),
            'market_summary': data.get('market_summary', {}),
            'stocks': filtered_stocks
        }
        
        return jsonify(filtered_data), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching stocks: {str(e)}'
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

@market_routes.route('/api/market/refresh', methods=['POST'])
def refresh_market_data():
    """
    Endpoint to refresh market data by triggering a new scrape
    Returns a JSON object with the new market data
    """
    try:
        # Trigger a new scrape
        stock_data_path = scrape_stocks_tool()
        
        # Read the scraped data
        with open(stock_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add refresh timestamp
        data['refresh_info'] = {
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error refreshing market data: {str(e)}'
        }), 500