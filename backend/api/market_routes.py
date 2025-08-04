#!/usr/bin/env python3
"""
Market Routes for BullBearPK
============================

API endpoints for market data and stock information:
1. Get latest market data
2. Search stocks
3. Get stock details
4. Refresh market data
"""

from flask import Blueprint, jsonify, request
from agents.fin_scraper import scrape_stocks_tool
from database_config import db_config
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
market_routes = Blueprint('market_routes', __name__)

@market_routes.route('/api/market/data', methods=['GET'])
def get_market_data():
    """
    Get the latest market data from the database
    
    Query Parameters:
    - limit: Number of stocks to return (default: all)
    - sector: Filter by sector
    - sort_by: Sort field (code, name, close_price, change_percent)
    - order: Sort order (asc, desc)
    
    Returns:
    {
        "success": true,
        "market_data": {
            "stocks": [...],
            "market_summary": {...},
            "last_updated": "2025-01-23T10:30:00Z"
        }
    }
    """
    try:
        limit = request.args.get('limit', type=int)
        sector = request.args.get('sector')
        sort_by = request.args.get('sort_by', 'code')
        order = request.args.get('order', 'asc')
        
        logger.info(f"Getting market data with filters: limit={limit}, sector={sector}")
        
        # Build query
        query = "SELECT * FROM stocks WHERE 1=1"
        params = []
        
        if sector:
            query += " AND sector = %s"
            params.append(sector)
        
        query += f" ORDER BY {sort_by} {order.upper()}"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        results = db_config.execute_query(query, params)
        
        if not results:
            return jsonify({
                'success': False,
                'message': 'No market data available'
            }), 404
        
        # Calculate market summary
        total_stocks = len(results)
        gainers = len([s for s in results if s.get('change_percent', 0) > 0])
        losers = len([s for s in results if s.get('change_percent', 0) < 0])
        unchanged = total_stocks - gainers - losers
        
        market_summary = {
            'total_stocks': total_stocks,
            'gainers': gainers,
            'losers': losers,
            'unchanged': unchanged,
            'top_gainer': max(results, key=lambda x: x.get('change_percent', 0)) if results else None,
            'top_loser': min(results, key=lambda x: x.get('change_percent', 0)) if results else None
        }
        
        return jsonify({
            'success': True,
            'market_data': {
                'stocks': results,
                'market_summary': market_summary,
                'last_updated': datetime.now().isoformat()
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching market data: {str(e)}'
        }), 500

@market_routes.route('/api/market/stocks/search', methods=['GET'])
def search_stocks():
    """
    Search stocks by query
    
    Query Parameters:
    - q: Search query
    - limit: Number of results (default: 20)
    
    Returns:
    {
        "success": true,
        "stocks": [...],
        "total_results": 15,
        "query": "OGDC"
    }
    """
    try:
        query = request.args.get('q', '').lower()
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Search query is required'
            }), 400
        
        logger.info(f"Searching stocks with query: {query}")
        
        # Search in code, name, and sector
        search_query = """
            SELECT * FROM stocks 
            WHERE LOWER(code) LIKE %s 
            OR LOWER(name) LIKE %s 
            OR LOWER(sector) LIKE %s
            ORDER BY code
            LIMIT %s
        """
        search_param = f"%{query}%"
        results = db_config.execute_query(search_query, (search_param, search_param, search_param, limit))
        
        return jsonify({
            'success': True,
            'stocks': results,
            'total_results': len(results),
            'query': query
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching stocks: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error searching stocks: {str(e)}'
        }), 500

@market_routes.route('/api/market/stock/<symbol>', methods=['GET'])
def get_stock_details(symbol):
    """
    Get detailed information for a specific stock
    
    Path Parameters:
    - symbol: Stock symbol
    
    Returns:
    {
        "success": true,
        "stock": {...},
        "analysis": {...},
        "news": [...]
    }
    """
    try:
        logger.info(f"Getting details for stock: {symbol}")
        
        # Get stock data
        stock_query = "SELECT * FROM stocks WHERE code = %s"
        stock_result = db_config.execute_query(stock_query, (symbol,))
        
        if not stock_result:
            return jsonify({
                'success': False,
                'message': f'Stock {symbol} not found'
            }), 404
        
        stock = stock_result[0]
        
        # Get stock analysis
        analysis_query = "SELECT * FROM stock_analysis WHERE stock_code = %s ORDER BY analysis_timestamp DESC LIMIT 1"
        analysis_result = db_config.execute_query(analysis_query, (symbol,))
        
        # Get recent news
        news_query = """
            SELECT * FROM news_analysis 
            WHERE stock_code = %s 
            ORDER BY analysis_timestamp DESC 
            LIMIT 5
        """
        news_result = db_config.execute_query(news_query, (symbol,))
        
        return jsonify({
            'success': True,
            'stock': stock,
            'analysis': analysis_result[0] if analysis_result else None,
            'news': news_result,
            'last_updated': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching stock details: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching stock details: {str(e)}'
        }), 500

@market_routes.route('/api/market/refresh', methods=['POST'])
def refresh_market_data():
    """
    Trigger market data refresh by running the stock scraper
    
    Returns:
    {
        "success": true,
        "message": "Market data refreshed successfully",
        "scraped_stocks": 150,
        "timestamp": "2025-01-23T10:30:00Z"
    }
    """
    try:
        logger.info("Triggering market data refresh")
        
        # Run the stock scraper
        result = scrape_stocks_tool()
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': 'Market data refreshed successfully',
                'scraped_stocks': len(result.get('data', [])),
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Failed to refresh market data')
            }), 500
    
    except Exception as e:
        logger.error(f"Error refreshing market data: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error refreshing market data: {str(e)}'
        }), 500

@market_routes.route('/api/market/sectors', methods=['GET'])
def get_sectors():
    """
    Get all available sectors and their statistics
    
    Returns:
    {
        "success": true,
        "sectors": [
            {
                "sector": "Banking",
                "stock_count": 25,
                "avg_change": 2.5,
                "top_stocks": [...]
            }
        ]
    }
    """
    try:
        logger.info("Getting sector statistics")
        
        # Get sector statistics
        sector_query = """
            SELECT 
                sector,
                COUNT(*) as stock_count,
                AVG(change_percent) as avg_change,
                SUM(CASE WHEN change_percent > 0 THEN 1 ELSE 0 END) as gainers,
                SUM(CASE WHEN change_percent < 0 THEN 1 ELSE 0 END) as losers
            FROM stocks 
            WHERE sector IS NOT NULL AND sector != ''
            GROUP BY sector
            ORDER BY stock_count DESC
        """
        sector_results = db_config.execute_query(sector_query)
        
        sectors = []
        for sector_data in sector_results:
            sector_name = sector_data.get('sector')
            
            # Get top stocks for this sector
            top_stocks_query = """
                SELECT code, name, close_price, change_percent 
                FROM stocks 
                WHERE sector = %s 
                ORDER BY change_percent DESC 
                LIMIT 3
            """
            top_stocks = db_config.execute_query(top_stocks_query, (sector_name,))
            
            sectors.append({
                'sector': sector_name,
                'stock_count': sector_data.get('stock_count', 0),
                'avg_change': round(sector_data.get('avg_change', 0), 2),
                'gainers': sector_data.get('gainers', 0),
                'losers': sector_data.get('losers', 0),
                'top_stocks': top_stocks
            })
        
        return jsonify({
            'success': True,
            'sectors': sectors,
            'total_sectors': len(sectors)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting sectors: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting sectors: {str(e)}'
        }), 500

@market_routes.route('/api/market/top-movers', methods=['GET'])
def get_top_movers():
    """
    Get top gainers and losers
    
    Query Parameters:
    - limit: Number of stocks to return (default: 10)
    
    Returns:
    {
        "success": true,
        "top_gainers": [...],
        "top_losers": [...],
        "limit": 10
    }
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        logger.info(f"Getting top movers with limit: {limit}")
        
        # Get top gainers
        gainers_query = """
            SELECT * FROM stocks 
            ORDER BY change_percent DESC 
            LIMIT %s
        """
        top_gainers = db_config.execute_query(gainers_query, (limit,))
        
        # Get top losers
        losers_query = """
            SELECT * FROM stocks 
            ORDER BY change_percent ASC 
            LIMIT %s
        """
        top_losers = db_config.execute_query(losers_query, (limit,))
        
        return jsonify({
            'success': True,
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting top movers: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting top movers: {str(e)}'
        }), 500