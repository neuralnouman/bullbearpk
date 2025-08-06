#!/usr/bin/env python3
"""
Check if user exists and create if needed
"""

from database_config import db_config
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_create_user():
    """Check if user exists and create if needed"""
    user_id = "user_100518b1be17902e"
    
    try:
        # Check if user exists
        check_query = "SELECT * FROM users WHERE user_id = %s"
        result = db_config.execute_query(check_query, (user_id,))
        
        if not result:
            logger.info(f"User {user_id} doesn't exist. Creating...")
            
            # Create the user
            create_user_query = """
            INSERT INTO users (user_id, name, email, password, risk_tolerance, 
                             investment_goal, preferred_sectors, portfolio_value, 
                             cash_balance, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            now = datetime.now()
            user_data = (
                user_id,
                "Test User",
                "test@example.com",
                "password123",
                "moderate",
                "Growth",
                '["Technology", "Banking"]',
                10000.00,
                10000.00,
                now,
                now
            )
            
            db_config.execute_query(create_user_query, user_data)
            logger.info(f"User {user_id} created successfully!")
            
            # Also create a portfolio entry
            portfolio_query = """
            INSERT INTO portfolios (user_id, total_value, total_invested, 
                                  total_profit_loss, profit_loss_percent, portfolio_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            portfolio_data = (
                user_id,
                10000.00,
                0.00,
                0.00,
                0.00,
                now
            )
            
            db_config.execute_query(portfolio_query, portfolio_data)
            logger.info(f"Portfolio for user {user_id} created successfully!")
            
        else:
            logger.info(f"User {user_id} already exists.")
            user = result[0]
            logger.info(f"User details: {user}")
            
    except Exception as e:
        logger.error(f"Error checking/creating user: {e}")
        raise

if __name__ == "__main__":
    check_and_create_user() 