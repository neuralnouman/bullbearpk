#!/usr/bin/env python3
"""
Fix Specific User Cash Balance
==============================

This script fixes the cash balance for user_89e4b6e17e1ea088
"""

from database_config import db_config
import logging

logger = logging.getLogger(__name__)

def fix_specific_user_cash():
    """Fix cash balance for the specific user"""
    user_id = "user_89e4b6e17e1ea088"
    
    try:
        # Get user's current investments
        investments_query = """
            SELECT SUM(total_invested) as total_invested 
            FROM investments 
            WHERE user_id = %s AND status = 'active'
        """
        investments_result = db_config.execute_query(investments_query, (user_id,))
        total_invested = float(investments_result[0]['total_invested']) if investments_result and investments_result[0]['total_invested'] else 0
        
        # Get current cash balance
        user_query = "SELECT cash_balance FROM users WHERE user_id = %s"
        user_result = db_config.execute_query(user_query, (user_id,))
        current_cash = float(user_result[0]['cash_balance']) if user_result else 0
        
        print(f"=== Current State for {user_id} ===")
        print(f"Current Cash Balance: PKR {current_cash:,.2f}")
        print(f"Total Invested: PKR {total_invested:,.2f}")
        
        # Calculate correct cash balance (initial 10000 - total invested)
        initial_cash = 10000.00
        correct_cash_balance = initial_cash - total_invested
        
        print(f"Expected Cash Balance: PKR {correct_cash_balance:,.2f}")
        print(f"Difference: PKR {current_cash - correct_cash_balance:,.2f}")
        
        # Fix the cash balance
        update_query = """
            UPDATE users SET 
                cash_balance = %s,
                updated_at = NOW()
            WHERE user_id = %s
        """
        db_config.execute_query(update_query, (correct_cash_balance, user_id))
        
        print(f"✅ Fixed cash balance to: PKR {correct_cash_balance:,.2f}")
        
        # Verify the fix
        user_result = db_config.execute_query(user_query, (user_id,))
        new_cash = float(user_result[0]['cash_balance']) if user_result else 0
        print(f"✅ Verified new cash balance: PKR {new_cash:,.2f}")
        
    except Exception as e:
        logger.error(f"Error fixing cash balance: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Fixing specific user cash balance...")
    fix_specific_user_cash()
    print("Done!") 