#!/usr/bin/env python3
"""
Recommendation Routes for BullBearPK
===================================

API endpoints for recommendation generation and history:
1. Generate recommendations using agentic framework
2. Get recommendation history
3. Get recommendation analytics
"""

from flask import Blueprint, jsonify, request
from agentic_framework import AgenticFramework
from database_config import db_config
import json
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)
recommendation_routes = Blueprint('recommendation_routes', __name__)

@recommendation_routes.route('/recommendations', methods=['POST'])
def get_recommendations():
    """
    Generate investment recommendations using the agentic framework
    
    Request Body:
    {
        "user_id": "user123",
        "user_input": {
            "budget": 10000,
            "risk_tolerance": "moderate",
            "investment_goal": "growth",
            "time_horizon": "medium",
            "sector_preference": "technology",
            "target_profit": 15
        },
        "refresh_data": false
    }
    
    Returns:
    {
        "success": true,
        "recommendations": [...],
        "analysis_summary": {...},
        "timestamp": "2025-01-23T10:30:00Z"
    }
    """
    try:
        data = request.json
        user_input = data.get('user_input', {})
        user_id = data.get('user_id', 'demo_user')
        refresh_data = data.get('refresh_data', False)
        
        logger.info(f"Generating recommendations for user {user_id}")
        
        # Initialize agentic framework
        framework = AgenticFramework()
        
        # Run the complete workflow
        result = asyncio.run(framework.run_workflow(
            user_input=user_input,
            chat_message=data.get('chat_message', ''),
            user_id=user_id
        ))
        
        if result.get('success', False):
            return jsonify({
                'success': True,
                'message': 'Recommendations generated successfully',
                'recommendations': result.get('recommendations', []),
                'analysis_summary': {
                    'stock_analysis_count': len(result.get('stock_analysis', [])),
                    'news_analysis_count': len(result.get('news_analysis', {})),
                    'risk_profile': result.get('risk_profile', {}),
                    'portfolio_status': result.get('portfolio_update', {}),
                    'user_history': result.get('user_history', {})
                },
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Failed to generate recommendations'),
                'error': result.get('error', 'Unknown error')
            }), 400
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error generating recommendations: {str(e)}'
        }), 500

@recommendation_routes.route('/recommendations/history', methods=['GET'])
def get_recommendation_history():
    """
    Get user's recommendation history
    
    Query Parameters:
    - user_id: User ID
    - limit: Number of recommendations to return (default: 10)
    - days: Number of days to look back (default: 30)
    
    Returns:
    {
        "success": true,
        "recommendations": [...],
        "total_count": 25,
        "user_id": "user123"
    }
    """
    try:
        user_id = request.args.get('user_id', 'demo_user')
        limit = int(request.args.get('limit', 10))
        days = int(request.args.get('days', 30))
        
        logger.info(f"Getting recommendation history for user {user_id}")
        
        # Get recommendations from the recommendations table
        query = """
            SELECT * FROM recommendations 
            WHERE user_id = %s 
            AND analysis_timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ORDER BY analysis_timestamp DESC
            LIMIT %s
        """
        results = db_config.execute_query(query, (user_id, days, limit))
        
        recommendations = []
        if results:
            for row in results:
                recommendations.append({
                    'id': row.get('id'),
                    'stock_code': row.get('stock_code'),
                    'stock_name': row.get('stock_name'),
                    'recommendation_type': row.get('recommendation_type'),
                    'reasoning_summary': row.get('reasoning_summary'),
                    'risk_level': row.get('risk_level'),
                    'expected_return': f"{row.get('expected_return', 0)}%",
                    'confidence_score': f"{row.get('confidence_score', 0)}%",
                    'allocation_percent': f"{row.get('allocation_percent', 0)}%",
                    'key_factors': json.loads(row.get('key_factors', '[]')),
                    'risk_factors': json.loads(row.get('risk_factors', '[]')),
                    'technical_analysis': json.loads(row.get('technical_analysis', '{}')),
                    'news_sentiment': json.loads(row.get('news_sentiment', '{}')),
                    'timestamp': row.get('analysis_timestamp')
                })
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total_count': len(recommendations),
            'user_id': user_id,
            'days_back': days
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recommendation history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting recommendation history: {str(e)}'
        }), 500

@recommendation_routes.route('/recommendations/<stock_code>', methods=['GET'])
def get_stock_recommendation(stock_code):
    """
    Get specific recommendation for a stock
    
    Path Parameters:
    - stock_code: Stock symbol
    
    Query Parameters:
    - user_id: User ID
    
    Returns:
    {
        "success": true,
        "recommendation": {...},
        "stock_code": "OGDC"
    }
    """
    try:
        user_id = request.args.get('user_id', 'demo_user')
        
        logger.info(f"Getting recommendation for stock {stock_code} for user {user_id}")
        
        # Get specific recommendation
        query = """
            SELECT * FROM recommendations 
            WHERE user_id = %s AND stock_code = %s
            ORDER BY analysis_timestamp DESC
            LIMIT 1
        """
        results = db_config.execute_query(query, (user_id, stock_code))
        
        if not results:
            return jsonify({
                'success': False,
                'message': f'No recommendation found for {stock_code}'
            }), 404
        
        recommendation = results[0]
        
        return jsonify({
            'success': True,
            'recommendation': {
                'id': recommendation.get('id'),
                'stock_code': recommendation.get('stock_code'),
                'stock_name': recommendation.get('stock_name'),
                'recommendation_type': recommendation.get('recommendation_type'),
                'reasoning_summary': recommendation.get('reasoning_summary'),
                'risk_level': recommendation.get('risk_level'),
                'expected_return': f"{recommendation.get('expected_return', 0)}%",
                'confidence_score': f"{recommendation.get('confidence_score', 0)}%",
                'allocation_percent': f"{recommendation.get('allocation_percent', 0)}%",
                'key_factors': json.loads(recommendation.get('key_factors', '[]')),
                'risk_factors': json.loads(recommendation.get('risk_factors', '[]')),
                'technical_analysis': json.loads(recommendation.get('technical_analysis', '{}')),
                'news_sentiment': json.loads(recommendation.get('news_sentiment', '{}')),
                'timestamp': recommendation.get('analysis_timestamp')
            },
            'stock_code': stock_code,
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stock recommendation: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting stock recommendation: {str(e)}'
        }), 500

@recommendation_routes.route('/recommendations/analytics', methods=['GET'])
def get_recommendation_analytics():
    """
    Get recommendation analytics and statistics
    
    Query Parameters:
    - user_id: User ID
    - days: Number of days to analyze (default: 30)
    
    Returns:
    {
        "success": true,
        "analytics": {
            "total_recommendations": 25,
            "buy_recommendations": 15,
            "hold_recommendations": 8,
            "sell_recommendations": 2,
            "average_confidence": 75.5,
            "top_sectors": [...],
            "performance_trend": {...}
        }
    }
    """
    try:
        user_id = request.args.get('user_id', 'demo_user')
        days = int(request.args.get('days', 30))
        
        logger.info(f"Getting recommendation analytics for user {user_id}")
        
        # Get analytics data
        analytics_query = """
            SELECT 
                COUNT(*) as total_recommendations,
                COUNT(CASE WHEN recommendation_type = 'buy' THEN 1 END) as buy_count,
                COUNT(CASE WHEN recommendation_type = 'hold' THEN 1 END) as hold_count,
                COUNT(CASE WHEN recommendation_type = 'sell' THEN 1 END) as sell_count,
                AVG(confidence_score) as avg_confidence
            FROM recommendations 
            WHERE user_id = %s 
            AND analysis_timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        analytics_result = db_config.execute_query(analytics_query, (user_id, days))
        
        if not analytics_result:
            return jsonify({
                'success': False,
                'message': 'No analytics data available'
            }), 404
        
        analytics_data = analytics_result[0]
        
        # Get top sectors
        sectors_query = """
            SELECT sector, COUNT(*) as count
            FROM recommendations 
            WHERE user_id = %s 
            AND analysis_timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY sector
            ORDER BY count DESC
            LIMIT 5
        """
        sectors_result = db_config.execute_query(sectors_query, (user_id, days))
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_recommendations': analytics_data.get('total_recommendations', 0),
                'buy_recommendations': analytics_data.get('buy_count', 0),
                'hold_recommendations': analytics_data.get('hold_count', 0),
                'sell_recommendations': analytics_data.get('sell_count', 0),
                'average_confidence': round(analytics_data.get('avg_confidence', 0), 2),
                'top_sectors': [{'sector': row.get('sector'), 'count': row.get('count')} 
                               for row in sectors_result],
                'analysis_period_days': days
            },
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recommendation analytics: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error getting recommendation analytics: {str(e)}'
        }), 500