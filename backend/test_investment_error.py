#!/usr/bin/env python3
"""
Test script to reproduce the investment error
"""

from portfolio_manager import portfolio_manager
from database_config import db_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_investment_transaction():
    """Test the investment transaction that's failing"""
    try:
        user_id = "user_89e4b6e17e1ea088"
        stock_code = "ATRL"
        quantity = 10
        price = 85.50
        total_amount = quantity * price
        
        print(f"Testing investment transaction:")
        print(f"  User ID: {user_id}")
        print(f"  Stock Code: {stock_code}")
        print(f"  Quantity: {quantity}")
        print(f"  Price: {price}")
        print(f"  Total Amount: {total_amount}")
        
        # Check if user exists
        print("\n1. Checking if user exists...")
        user_result = db_config.execute_query("SELECT * FROM users WHERE user_id = %s", (user_id,))
        if user_result:
            user = user_result[0]
            print(f"✓ User found: {user['user_id']}")
            print(f"  Cash balance: {user['cash_balance']}")
        else:
            print("✗ User not found")
            return False
        
        # Check if stock exists
        print("\n2. Checking if stock exists...")
        stock_result = db_config.execute_query(
            "SELECT name, sector, close_price FROM stocks WHERE code = %s ORDER BY scraped_at DESC LIMIT 1",
            (stock_code,)
        )
        if stock_result:
            stock = stock_result[0]
            print(f"✓ Stock found: {stock['name']}")
            print(f"  Sector: {stock['sector']}")
            print(f"  Current price: {stock['close_price']}")
        else:
            print("✗ Stock not found")
            return False
        
        # Check current cash balance
        print("\n3. Checking current cash balance...")
        current_cash_result = db_config.execute_query("SELECT cash_balance FROM users WHERE user_id = %s", (user_id,))
        current_cash = float(current_cash_result[0]['cash_balance']) if current_cash_result else 0
        print(f"Current cash balance: {current_cash}")
        print(f"Required amount: {total_amount}")
        print(f"Sufficient funds: {'Yes' if current_cash >= total_amount else 'No'}")
        
        # Test the transaction
        print("\n4. Testing investment transaction...")
        success = portfolio_manager.record_investment_transaction(
            user_id=user_id,
            stock_code=stock_code,
            transaction_type='buy',
            quantity=quantity,
            price=price,
            total_amount=total_amount
        )
        
        if success:
            print("✓ Investment transaction successful")
            
            # Check updated cash balance
            updated_cash_result = db_config.execute_query("SELECT cash_balance FROM users WHERE user_id = %s", (user_id,))
            updated_cash = float(updated_cash_result[0]['cash_balance']) if updated_cash_result else 0
            print(f"Updated cash balance: {updated_cash}")
            
            # Check if investment was recorded
            investment_result = db_config.execute_query(
                "SELECT * FROM investments WHERE user_id = %s AND stock_code = %s ORDER BY buy_date DESC LIMIT 1",
                (user_id, stock_code)
            )
            if investment_result:
                investment = investment_result[0]
                print(f"✓ Investment recorded: ID {investment['id']}")
                print(f"  Quantity: {investment['quantity']}")
                print(f"  Buy price: {investment['buy_price']}")
                print(f"  Total invested: {investment['total_invested']}")
            else:
                print("✗ Investment not recorded")
        else:
            print("✗ Investment transaction failed")
        
        return success
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_investment_transaction() 