#!/usr/bin/env python3
"""
Test script to verify cash balance updates when buying and selling stocks
Tests that the cash balance component updates correctly in the frontend.
"""

import requests
import json
import sys
import os
import time

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database_config import DatabaseConfig

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_ID = "test_user_cash_balance"

def test_cash_balance_updates():
    """Test that cash balance updates correctly when buying and selling stocks"""
    
    print("🧪 Testing Cash Balance Updates")
    print("=" * 50)
    
    # Initialize database connection
    db_config = DatabaseConfig()
    
    # Clean up any existing test data
    cleanup_test_data(db_config)
    
    # Create test user
    create_test_user(db_config)
    
    # Test 1: Check initial portfolio state
    print("\n📊 Test 1: Initial Portfolio State")
    print("-" * 40)
    
    initial_portfolio = get_portfolio(TEST_USER_ID)
    if not initial_portfolio['success']:
        print("❌ Failed to get initial portfolio")
        return False
    
    initial_summary = initial_portfolio['portfolio_summary']
    initial_cash = initial_summary['cashBalance']
    initial_total_value = initial_summary['totalValue']
    
    print(f"   Initial cash balance: ${initial_cash:.2f}")
    print(f"   Initial total value: ${initial_total_value:.2f}")
    
    # Test 2: Buy stock and verify cash balance decreases
    print("\n💰 Test 2: Buy Stock - Cash Balance Should Decrease")
    print("-" * 40)
    
    buy_result = buy_stock(TEST_USER_ID, "OGDC", 10, 85.50)
    if not buy_result['success']:
        print("❌ Failed to buy stock")
        return False
    
    print(f"   Bought 10 shares of OGDC at $85.50")
    print(f"   Total cost: ${10 * 85.50:.2f}")
    
    # Wait a moment for database to update
    time.sleep(1)
    
    # Get updated portfolio after buy
    after_buy_portfolio = get_portfolio(TEST_USER_ID)
    if not after_buy_portfolio['success']:
        print("❌ Failed to get portfolio after buy")
        return False
    
    after_buy_summary = after_buy_portfolio['portfolio_summary']
    after_buy_cash = after_buy_summary['cashBalance']
    after_buy_total_value = after_buy_summary['totalValue']
    
    print(f"   Cash balance after buy: ${after_buy_cash:.2f}")
    print(f"   Total value after buy: ${after_buy_total_value:.2f}")
    
    expected_cash_after_buy = initial_cash - (10 * 85.50)
    cash_decreased = abs(after_buy_cash - expected_cash_after_buy) < 0.01
    
    if cash_decreased:
        print("   ✅ Cash balance correctly decreased after buying stock")
    else:
        print(f"   ❌ Cash balance not updated correctly. Expected: ${expected_cash_after_buy:.2f}, Got: ${after_buy_cash:.2f}")
        return False
    
    # Test 3: Sell stock and verify cash balance increases
    print("\n💸 Test 3: Sell Stock - Cash Balance Should Increase")
    print("-" * 40)
    
    sell_result = sell_stock(TEST_USER_ID, "OGDC", 5, 90.00)
    if not sell_result['success']:
        print("❌ Failed to sell stock")
        return False
    
    print(f"   Sold 5 shares of OGDC at $90.00")
    print(f"   Total proceeds: ${5 * 90.00:.2f}")
    
    # Wait a moment for database to update
    time.sleep(1)
    
    # Get updated portfolio after sell
    after_sell_portfolio = get_portfolio(TEST_USER_ID)
    if not after_sell_portfolio['success']:
        print("❌ Failed to get portfolio after sell")
        return False
    
    after_sell_summary = after_sell_portfolio['portfolio_summary']
    after_sell_cash = after_sell_summary['cashBalance']
    after_sell_total_value = after_sell_summary['totalValue']
    
    print(f"   Cash balance after sell: ${after_sell_cash:.2f}")
    print(f"   Total value after sell: ${after_sell_total_value:.2f}")
    
    expected_cash_after_sell = after_buy_cash + (5 * 90.00)
    cash_increased = abs(after_sell_cash - expected_cash_after_sell) < 0.01
    
    if cash_increased:
        print("   ✅ Cash balance correctly increased after selling stock")
    else:
        print(f"   ❌ Cash balance not updated correctly. Expected: ${expected_cash_after_sell:.2f}, Got: ${after_sell_cash:.2f}")
        return False
    
    # Test 4: Verify frontend would receive correct data
    print("\n🖥️  Test 4: Frontend Data Verification")
    print("-" * 40)
    
    final_portfolio = get_portfolio(TEST_USER_ID)
    final_summary = final_portfolio['portfolio_summary']
    
    print(f"   Final cash balance: ${final_summary['cashBalance']:.2f}")
    print(f"   Final total value: ${final_summary['totalValue']:.2f}")
    print(f"   Final total invested: ${final_summary['totalInvested']:.2f}")
    print(f"   Active investments: {final_summary['activeInvestments']}")
    
    # Verify the data makes sense
    cash_balance = final_summary['cashBalance']
    total_value = final_summary['totalValue']
    total_invested = final_summary['totalInvested']
    
    # Total value should be cash balance + investment value
    investment_value = total_value - cash_balance
    print(f"   Investment value: ${investment_value:.2f}")
    
    if investment_value >= 0:
        print("   ✅ Portfolio data is consistent")
        return True
    else:
        print("   ❌ Portfolio data is inconsistent")
        return False

def cleanup_test_data(db_config):
    """Clean up test data"""
    try:
        # Delete test user's investments
        db_config.execute_query(
            "DELETE FROM investments WHERE user_id = %s",
            (TEST_USER_ID,)
        )
        
        # Delete test user
        db_config.execute_query(
            "DELETE FROM users WHERE user_id = %s",
            (TEST_USER_ID,)
        )
        
        print("🧹 Cleaned up test data")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up test data: {e}")

def create_test_user(db_config):
    """Create test user"""
    try:
        db_config.execute_query(
            """
            INSERT INTO users (user_id, name, email, risk_tolerance, investment_goal, cash_balance, portfolio_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (TEST_USER_ID, "Test User", "test@example.com", "moderate", "growth", 10000, 10000)
        )
        print("👤 Created test user")
    except Exception as e:
        print(f"⚠️  Warning: Could not create test user: {e}")

def get_portfolio(user_id):
    """Get portfolio data"""
    try:
        response = requests.get(f"{BASE_URL}/portfolio/{user_id}")
        return response.json()
    except Exception as e:
        print(f"❌ Error getting portfolio: {e}")
        return {"success": False, "message": str(e)}

def buy_stock(user_id, stock_code, quantity, price):
    """Buy stock"""
    try:
        response = requests.post(
            f"{BASE_URL}/portfolio/{user_id}/investments",
            json={
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price,
                "transaction_type": "buy"
            },
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        print(f"❌ Error buying stock: {e}")
        return {"success": False, "message": str(e)}

def sell_stock(user_id, stock_code, quantity, price):
    """Sell stock"""
    try:
        response = requests.post(
            f"{BASE_URL}/portfolio/{user_id}/investments",
            json={
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price,
                "transaction_type": "sell"
            },
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        print(f"❌ Error selling stock: {e}")
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    try:
        success = test_cash_balance_updates()
        if success:
            print("\n🎉 Cash balance update test PASSED!")
            print("✅ The backend is correctly updating cash balance during buy/sell transactions")
            print("✅ The frontend should receive the correct updated data")
        else:
            print("\n💥 Cash balance update test FAILED!")
            print("❌ There are issues with cash balance updates during transactions")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 