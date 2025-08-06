import time
import json
from flask import Blueprint, jsonify, request
from database_config import DatabaseConfig
import mysql.connector
from datetime import datetime, timedelta

# Initialize database config
db_config = DatabaseConfig()

portfolio_history_bp = Blueprint('portfolio_history', __name__)

@portfolio_history_bp.route('/<user_id>/history/performance/<timeframe>', methods=['GET'])
def get_portfolio_performance_history(user_id, timeframe):
    """
    Get portfolio performance history by timeframe
    Timeframes: 1D, 1W, 1M, 3M, 6M, 1Y, ALL
    """
    try:
        # For now, return empty data since portfolio_history table doesn't exist
        # This can be implemented later when the table is created
        return jsonify({
            'success': True,
            'message': 'No performance history data available yet',
            'data': []
        })
        
    except Exception as e:
        print(f"Error getting portfolio performance history: {e}")
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500


@portfolio_history_bp.route('/<user_id>/history/value/<timeframe>', methods=['GET'])
def get_portfolio_value_history(user_id, timeframe):
    """
    Get portfolio value and invested amount history by timeframe
    Timeframes: 1D, 1W, 1M, 3M, 6M, 1Y, ALL
    """
    try:
        # For now, return empty data since portfolio_history table doesn't exist
        # This can be implemented later when the table is created
        return jsonify({
            'success': True,
            'message': 'No value history data available yet',
            'data': []
        })
        
    except Exception as e:
        print(f"Error getting portfolio value history: {e}")
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500



