#!/usr/bin/env python3
"""
Fix User Portfolio Synchronization
==================================

This script fixes the synchronization between users table and portfolio data.
It updates the portfolio_value field in the users table based on current investments.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_config import db_config
from portfolio_manager import portfolio_manager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_user_portfolio_sync(user_id: str = None):
    """Fix portfolio synchronization for a specific user or all users"""
    try:
        if user_id:
            # Fix specific user
            users = [{'user_id': user_id}]
            logger.info(f"Fixing portfolio sync for user: {user_id}")
        else:
            # Fix all users
            users_result = db_config.execute_query("SELECT user_id FROM users")
            users = users_result if users_result else []
            logger.info(f"Fixing portfolio sync for {len(users)} users")
        
        fixed_count = 0
        for user in users:
            user_id = user['user_id']
            
            try:
                # Get current portfolio data
                investments = db_config.execute_query(
                    """
                    SELECT SUM(current_value) as total_value, SUM(total_invested) as total_invested
                    FROM investments 
                    WHERE user_id = %s AND status = 'active'
                    """,
                    (user_id,)
                )
                
                # Get user's current cash balance
                user_result = db_config.execute_query(
                    "SELECT cash_balance, portfolio_value FROM users WHERE user_id = %s",
                    (user_id,)
                )
                
                if not user_result:
                    logger.warning(f"User {user_id} not found, skipping")
                    continue
                
                # Calculate portfolio values
                total_value = float(investments[0]['total_value']) if investments and investments[0]['total_value'] else 0
                total_invested = float(investments[0]['total_invested']) if investments and investments[0]['total_invested'] else 0
                cash_balance = float(user_result[0]['cash_balance'])
                old_portfolio_value = float(user_result[0]['portfolio_value'])
                
                # Total portfolio value includes cash balance
                new_portfolio_value = total_value + cash_balance
                
                # Update user table with current portfolio data
                update_query = """
                    UPDATE users SET 
                        portfolio_value = %s,
                        updated_at = NOW()
                    WHERE user_id = %s
                """
                
                db_config.execute_query(update_query, (new_portfolio_value, user_id))
                
                logger.info(f"Fixed user {user_id}: portfolio_value {old_portfolio_value} -> {new_portfolio_value}")
                fixed_count += 1
                
            except Exception as e:
                logger.error(f"Error fixing user {user_id}: {e}")
                continue
        
        logger.info(f"Successfully fixed {fixed_count} users")
        return True
        
    except Exception as e:
        logger.error(f"Error in fix_user_portfolio_sync: {e}")
        return False

def verify_portfolio_sync(user_id: str = None):
    """Verify that portfolio synchronization is working correctly"""
    try:
        if user_id:
            users = [{'user_id': user_id}]
        else:
            users_result = db_config.execute_query("SELECT user_id FROM users")
            users = users_result if users_result else []
        
        logger.info(f"Verifying portfolio sync for {len(users)} users")
        
        for user in users:
            user_id = user['user_id']
            
            # Get current portfolio data
            investments = db_config.execute_query(
                """
                SELECT SUM(current_value) as total_value, SUM(total_invested) as total_invested
                FROM investments 
                WHERE user_id = %s AND status = 'active'
                """,
                (user_id,)
            )
            
            # Get user's current data
            user_result = db_config.execute_query(
                "SELECT cash_balance, portfolio_value FROM users WHERE user_id = %s",
                (user_id,)
            )
            
            if not user_result:
                continue
            
            # Calculate expected values
            total_value = float(investments[0]['total_value']) if investments and investments[0]['total_value'] else 0
            cash_balance = float(user_result[0]['cash_balance'])
            stored_portfolio_value = float(user_result[0]['portfolio_value'])
            
            expected_portfolio_value = total_value + cash_balance
            
            # Check if values match
            if abs(stored_portfolio_value - expected_portfolio_value) > 0.01:
                logger.warning(f"User {user_id}: portfolio_value mismatch - stored: {stored_portfolio_value}, expected: {expected_portfolio_value}")
            else:
                logger.info(f"User {user_id}: portfolio sync OK - value: {stored_portfolio_value}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in verify_portfolio_sync: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix user portfolio synchronization')
    parser.add_argument('--user-id', help='Specific user ID to fix')
    parser.add_argument('--verify', action='store_true', help='Verify portfolio sync instead of fixing')
    
    args = parser.parse_args()
    
    if args.verify:
        success = verify_portfolio_sync(args.user_id)
    else:
        success = fix_user_portfolio_sync(args.user_id)
    
    if success:
        print("✅ Operation completed successfully")
    else:
        print("❌ Operation failed")
        sys.exit(1) 