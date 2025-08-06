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
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
market_routes = Blueprint('market_routes', __name__)

@market_routes.route('/data', methods=['GET'])
def get_market_data() -> tuple:
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
        "stocks": [...],
        "market_summary": {...},
        "scrape_info": {
            "timestamp": "2025-01-23T10:30:00Z",
            "total_stocks": 269,
            "gainers": 150,
            "losers": 100,
            "unchanged": 19
        }
    }
    """
    try:
        limit: Optional[int] = request.args.get('limit', type=int)
        sector: Optional[str] = request.args.get('sector')
        sort_by: str = request.args.get('sort_by', 'code')
        order: str = request.args.get('order', 'asc')
        
        logger.info(f"Getting market data with filters: limit={limit}, sector={sector}")
        
        # Test database connection first
        if not db_config.test_connection():
            logger.error("Database connection failed")
            return jsonify({
                'success': False,
                'message': 'Database connection failed. Please check MySQL service and credentials.',
                'error': 'DATABASE_CONNECTION_ERROR'
            }), 503
        
        # Build query - by default, get ALL stocks (no limit unless specified)
        query: str = "SELECT * FROM stocks WHERE 1=1"
        params: List[Any] = []
        
        if sector:
            query += " AND sector = %s"
            params.append(sector)
        
        query += f" ORDER BY {sort_by} {order.upper()}"
        
        # Only apply limit if explicitly requested
        if limit and limit > 0:
            query += " LIMIT %s"
            params.append(limit)
        
        results: Optional[List[Dict[str, Any]]] = db_config.execute_query(query, params)
        
        if not results:
            return jsonify({
                'success': False,
                'message': 'No market data available. Database may be empty or table does not exist.',
                'error': 'NO_DATA_AVAILABLE'
            }), 404
        
        # Calculate market summary
        total_stocks: int = len(results)
        gainers: int = len([s for s in results if s.get('change_percent', 0) > 0])
        losers: int = len([s for s in results if s.get('change_percent', 0) < 0])
        unchanged: int = total_stocks - gainers - losers
        
        market_summary: Dict[str, Any] = {
            'total_stocks': total_stocks,
            'gainers': gainers,
            'losers': losers,
            'unchanged': unchanged,
            'top_gainer': max(results, key=lambda x: x.get('change_percent', 0)) if results else None,
            'top_loser': min(results, key=lambda x: x.get('change_percent', 0)) if results else None,
            'highest_volume': max(results, key=lambda x: x.get('volume', 0)) if results else None
        }
        
        # Get the most recent scrape timestamp from the database
        timestamp_query: str = "SELECT MAX(scraped_at) as last_scrape FROM stocks WHERE scraped_at IS NOT NULL"
        timestamp_result: Optional[List[Dict[str, Any]]] = db_config.execute_query(timestamp_query)
        
        # Use PKT timezone for consistency
        pkt_timezone = pytz.timezone('Asia/Karachi')
        current_time = datetime.now(pkt_timezone)
        
        last_scrape_time: str = timestamp_result[0].get('last_scrape') if timestamp_result and timestamp_result[0].get('last_scrape') else current_time.isoformat()
        
        return jsonify({
            'success': True,
            'stocks': results,
            'market_summary': market_summary,
            'scrape_info': {
                'timestamp': last_scrape_time,
                'total_stocks': total_stocks,
                'gainers': gainers,
                'losers': losers,
                'unchanged': unchanged
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching market data: {str(e)}',
            'error': 'INTERNAL_SERVER_ERROR'
        }), 500

@market_routes.route('/stocks/search', methods=['GET'])
def search_stocks() -> tuple:
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
        query: str = request.args.get('q', '').lower()
        limit: int = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Search query is required'
            }), 400
        
        logger.info(f"Searching stocks with query: {query}")
        
        # Search in code, name, and sector
        search_query: str = """
            SELECT * FROM stocks 
            WHERE LOWER(code) LIKE %s 
            OR LOWER(name) LIKE %s 
            OR LOWER(sector) LIKE %s
            ORDER BY code
            LIMIT %s
        """
        search_param: str = f"%{query}%"
        results: Optional[List[Dict[str, Any]]] = db_config.execute_query(search_query, (search_param, search_param, search_param, limit))
        
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

@market_routes.route('/stock/<symbol>', methods=['GET'])
def get_stock_details(symbol: str) -> tuple:
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
        stock_query: str = "SELECT * FROM stocks WHERE code = %s"
        stock_result: Optional[List[Dict[str, Any]]] = db_config.execute_query(stock_query, (symbol,))
        
        if not stock_result:
            return jsonify({
                'success': False,
                'message': f'Stock {symbol} not found'
            }), 404
        
        stock: Dict[str, Any] = stock_result[0]
        
        # Get stock analysis
        analysis_query: str = "SELECT * FROM stock_analysis WHERE stock_code = %s ORDER BY analysis_timestamp DESC LIMIT 1"
        analysis_result: Optional[List[Dict[str, Any]]] = db_config.execute_query(analysis_query, (symbol,))
        
        # Get recent news
        news_query: str = """
            SELECT * FROM news_analysis 
            WHERE stock_code = %s 
            ORDER BY analysis_timestamp DESC 
            LIMIT 5
        """
        news_result: Optional[List[Dict[str, Any]]] = db_config.execute_query(news_query, (symbol,))
        
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

@market_routes.route('/refresh', methods=['POST'])
def refresh_market_data() -> tuple:
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
        result: Dict[str, Any] = scrape_stocks_tool()
        
        if result.get('success', False):
            # Get the updated market data after scraping
            updated_data_query: str = "SELECT * FROM stocks ORDER BY code"
            updated_stocks: Optional[List[Dict[str, Any]]] = db_config.execute_query(updated_data_query)
            
            if updated_stocks:
                total_stocks: int = len(updated_stocks)
                gainers: int = len([s for s in updated_stocks if s.get('change_percent', 0) > 0])
                losers: int = len([s for s in updated_stocks if s.get('change_percent', 0) < 0])
                unchanged: int = total_stocks - gainers - losers
                
                market_summary: Dict[str, Any] = {
                    'total_stocks': total_stocks,
                    'gainers': gainers,
                    'losers': losers,
                    'unchanged': unchanged,
                    'top_gainer': max(updated_stocks, key=lambda x: x.get('change_percent', 0)) if updated_stocks else None,
                    'top_loser': min(updated_stocks, key=lambda x: x.get('change_percent', 0)) if updated_stocks else None,
                    'highest_volume': max(updated_stocks, key=lambda x: x.get('volume', 0)) if updated_stocks else None
                }
                
                # Get the most recent scrape timestamp
                timestamp_query: str = "SELECT MAX(scraped_at) as last_scrape FROM stocks WHERE scraped_at IS NOT NULL"
                timestamp_result: Optional[List[Dict[str, Any]]] = db_config.execute_query(timestamp_query)
                
                # Use PKT timezone for consistency
                pkt_timezone = pytz.timezone('Asia/Karachi')
                current_time = datetime.now(pkt_timezone)
                
                last_scrape_time: str = timestamp_result[0].get('last_scrape') if timestamp_result and timestamp_result[0].get('last_scrape') else current_time.isoformat()
                
                return jsonify({
                    'success': True,
                    'message': 'Market data refreshed successfully',
                    'stocks': updated_stocks,
                    'market_summary': market_summary,
                    'scrape_info': {
                        'timestamp': last_scrape_time,
                        'total_stocks': total_stocks,
                        'gainers': gainers,
                        'losers': losers,
                        'unchanged': unchanged
                    },
                    'scraped_stocks': len(result.get('data', [])),
                    'timestamp': current_time.isoformat()
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to retrieve updated market data'
                }), 500
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

@market_routes.route('/sectors', methods=['GET'])
def get_sectors() -> tuple:
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
        sector_query: str = """
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
        sector_results: Optional[List[Dict[str, Any]]] = db_config.execute_query(sector_query)
        
        sectors: List[Dict[str, Any]] = []
        for sector_data in sector_results:
            sector_name: str = sector_data.get('sector')
            
            # Get top stocks for this sector
            top_stocks_query: str = """
                SELECT code, name, close_price, change_percent 
                FROM stocks 
                WHERE sector = %s 
                ORDER BY change_percent DESC 
                LIMIT 3
            """
            top_stocks: Optional[List[Dict[str, Any]]] = db_config.execute_query(top_stocks_query, (sector_name,))
            
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

@market_routes.route('/top-movers', methods=['GET'])
def get_top_movers() -> tuple:
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
        limit: int = int(request.args.get('limit', 10))
        
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

@market_routes.route('/status', methods=['GET'])
def get_market_status() -> tuple:
    """
    Get current market status and summary
    
    Returns:
    {
        "success": true,
        "isOpen": true,
        "lastUpdated": "2025-01-23T10:30:00Z",
        "nextUpdate": "2025-01-23T10:35:00Z",
        "marketHours": "09:15 - 15:30"
    }
    """
    try:
        logger.info("Getting market status")
        
        # Get market summary
        summary_query: str = """
            SELECT 
                COUNT(*) as total_stocks,
                SUM(CASE WHEN change_percent > 0 THEN 1 ELSE 0 END) as gainers,
                SUM(CASE WHEN change_percent < 0 THEN 1 ELSE 0 END) as losers,
                SUM(CASE WHEN change_percent = 0 THEN 1 ELSE 0 END) as unchanged,
                AVG(change_percent) as avg_change
            FROM stocks
        """
        summary_result: Optional[List[Dict[str, Any]]] = db_config.execute_query(summary_query)
        
        if not summary_result:
            return jsonify({
                'success': False,
                'message': 'No market data available'
            }), 404
        
        summary: Dict[str, Any] = summary_result[0]
        avg_change: float = summary.get('avg_change', 0)
        
        # Determine market status (Pakistan Stock Exchange hours: 9:15 AM - 3:30 PM PKT)
        pkt_timezone = pytz.timezone('Asia/Karachi')
        current_time: datetime = datetime.now(pkt_timezone)
        current_hour: int = current_time.hour
        current_minute: int = current_time.minute
        current_time_minutes: int = current_hour * 60 + current_minute
        
        # PSX trading hours: 9:15 AM (555 minutes) to 3:30 PM (930 minutes) PKT
        market_open_minutes: int = 9 * 60 + 15  # 9:15 AM
        market_close_minutes: int = 15 * 60 + 30  # 3:30 PM
        
        is_open: bool = market_open_minutes <= current_time_minutes <= market_close_minutes
        
        # Get the most recent scrape timestamp from the database
        timestamp_query: str = "SELECT MAX(scraped_at) as last_scrape FROM stocks WHERE scraped_at IS NOT NULL"
        timestamp_result: Optional[List[Dict[str, Any]]] = db_config.execute_query(timestamp_query)
        last_scrape_time: str = timestamp_result[0].get('last_scrape') if timestamp_result and timestamp_result[0].get('last_scrape') else current_time.isoformat()
        
        # Calculate next update time (5 minutes from now) in PKT
        next_update: datetime = current_time.replace(second=0, microsecond=0)
        next_update = next_update.replace(minute=next_update.minute + 5)
        if next_update.minute >= 60:
            next_update = next_update.replace(hour=next_update.hour + 1, minute=next_update.minute - 60)
        
        return jsonify({
            'success': True,
            'isOpen': is_open,
            'lastUpdated': last_scrape_time,
            'nextUpdate': next_update.isoformat(),
            'marketHours': '09:15 - 15:30'
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting market status: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting market status: {str(e)}'
        }), 500

@market_routes.route('/news/top-companies', methods=['GET'])
def get_top_companies_news() -> tuple:
    """
    Get news for top performing companies
    
    Query Parameters:
    - limit: Number of companies to get news for (default: 5)
    
    Returns:
    {
        "success": true,
        "data": [
            {
                "id": "1",
                "title": "Company News Title",
                "content": "News content summary",
                "source": "News Source",
                "publishedAt": "2025-01-23T10:30:00Z",
                "sentiment": "positive",
                "sentimentScore": 0.8,
                "relevantCompanies": ["OGDC"],
                "url": "https://example.com/news",
                "link": "https://example.com/news",
                "imageUrl": ""
            }
        ]
    }
    """
    try:
        limit: int = int(request.args.get('limit', 5))
        
        logger.info(f"Getting news for top {limit} companies")
        
        # First, try to get companies that have news data
        top_companies_query: str = """
            SELECT DISTINCT s.code, s.name, s.sector, s.change_percent
            FROM stocks s
            INNER JOIN news_records n ON s.code = n.stock_code
            ORDER BY s.change_percent DESC 
            LIMIT %s
        """
        top_companies: Optional[List[Dict[str, Any]]] = db_config.execute_query(top_companies_query, (limit,))
        
        # If no companies with news found, fall back to top performing companies
        if not top_companies:
            logger.info("No companies with news found, falling back to top performing companies")
            fallback_query: str = """
                SELECT code, name, sector, change_percent
                FROM stocks 
                ORDER BY change_percent DESC 
                LIMIT %s
            """
            top_companies = db_config.execute_query(fallback_query, (limit,))
        
        if not top_companies:
            logger.warning("No stock data available")
            return jsonify({
                'success': False,
                'message': 'No stock data available'
            }), 404
        
        # Get news for each company
        flattened_news: List[Dict[str, Any]] = []
        
        for company in top_companies:
            company_code: str = company.get('code')
            company_name: str = company.get('name', '')
            
            try:
                # Get news for this company
                news_query: str = """
                    SELECT * FROM news_records 
                    WHERE stock_code = %s 
                    ORDER BY published_date DESC 
                    LIMIT 3
                """
                company_news: Optional[List[Dict[str, Any]]] = db_config.execute_query(news_query, (company_code,))
                
                # Get sentiment analysis
                sentiment_query: str = """
                    SELECT * FROM news_analysis 
                    WHERE stock_code = %s 
                    ORDER BY analysis_date DESC 
                    LIMIT 1
                """
                sentiment_result: Optional[List[Dict[str, Any]]] = db_config.execute_query(sentiment_query, (company_code,))
                
                sentiment: str = "neutral"
                sentiment_score: float = 0.0
                if sentiment_result:
                    sentiment_score = sentiment_result[0].get('sentiment_score', 0)
                    if sentiment_score > 0.1:
                        sentiment = "positive"
                    elif sentiment_score < -0.1:
                        sentiment = "negative"
                
                # If no news found for this company, create a placeholder
                if not company_news:
                    # Create a placeholder news article for companies without news
                    pkt_timezone = pytz.timezone('Asia/Karachi')
                    current_time = datetime.now(pkt_timezone)
                    
                    placeholder_article: Dict[str, Any] = {
                        'id': f'placeholder_{company_code}',
                        'title': f'Latest updates for {company_name} ({company_code})',
                        'content': f'Stay tuned for the latest news and updates about {company_name}. The company is currently showing a {company.get("change_percent", 0):.2f}% change in stock price.',
                        'source': 'BullBearPK',
                        'publishedAt': current_time.isoformat(),
                        'sentiment': sentiment,
                        'sentimentScore': sentiment_score,
                        'relevantCompanies': [company_code],
                        'url': '#',
                        'link': '#',
                        'imageUrl': ''
                    }
                    flattened_news.append(placeholder_article)
                else:
                    # Process actual news articles
                    for news_item in company_news:
                        # Clean and format the content to remove HTML tags
                        title = news_item.get('title', '')
                        summary = news_item.get('summary', '')
                        
                        # Remove HTML tags if present
                        if title and '<' in title and '>' in title:
                            from bs4 import BeautifulSoup
                            try:
                                soup = BeautifulSoup(title, 'html.parser')
                                title = soup.get_text().strip()
                            except:
                                pass
                        
                        if summary and '<' in summary and '>' in summary:
                            from bs4 import BeautifulSoup
                            try:
                                soup = BeautifulSoup(summary, 'html.parser')
                                summary = soup.get_text().strip()
                            except:
                                pass
                        
                        article: Dict[str, Any] = {
                            'id': str(news_item.get('id', '')),
                            'title': title,
                            'content': summary,
                            'source': news_item.get('source', 'Unknown'),
                            'publishedAt': news_item.get('published_date', ''),
                            'sentiment': sentiment,
                            'sentimentScore': float(news_item.get('sentiment_score', 0.0)),
                            'relevantCompanies': [company_code],
                            'url': news_item.get('link', ''),
                            'link': news_item.get('link', ''),
                            'imageUrl': ''
                        }
                        flattened_news.append(article)
                        
            except Exception as e:
                logger.warning(f"Error processing news for company {company_code}: {e}")
                # Create a fallback article for this company
                pkt_timezone = pytz.timezone('Asia/Karachi')
                current_time = datetime.now(pkt_timezone)
                
                fallback_article: Dict[str, Any] = {
                    'id': f'fallback_{company_code}',
                    'title': f'Company Update: {company_name}',
                    'content': f'Latest information about {company_name} ({company_code}). Stock performance: {company.get("change_percent", 0):.2f}% change.',
                    'source': 'BullBearPK',
                    'publishedAt': current_time.isoformat(),
                    'sentiment': 'neutral',
                    'sentimentScore': 0.0,
                    'relevantCompanies': [company_code],
                    'url': '#',
                    'link': '#',
                    'imageUrl': ''
                }
                flattened_news.append(fallback_article)
        
        return jsonify({
            'success': True,
            'data': flattened_news,
            'total_articles': len(flattened_news),
            'total_companies': len(top_companies)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting top companies news: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting top companies news: {str(e)}'
        }), 500