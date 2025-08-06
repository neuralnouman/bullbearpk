#!/usr/bin/env python3
"""
Test Portfolio Synchronization Fix
==================================

This script tests that the portfolio synchronization between users table and portfolio data works correctly.
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000"
USER_ID = "test_sync_user_123"

def test_portfolio_sync_fix():
    """Test that portfolio data is properly synchronized with user table"""
    
    print("🧪 Testing Portfolio Synchronization Fix")
    print("=" * 50)
    
    # Step 1: Create a test user and add investments
    print("\n1. Creating test user and adding investments...")
    
    # Add some test investments
    investments = [
        {"stock_code": "HBL", "quantity": 100, "price": 100.0, "transaction_type": "buy"},
        {"stock_code": "UBL", "quantity": 50, "price": 95.0, "transaction_type": "buy"},
    ]
    
    for inv in investments:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/{USER_ID}/investments",
            json=inv
        )
        print(f"   Added {inv['quantity']} shares of {inv['stock_code']} at ${inv['price']}")
    
    # Step 2: Check initial portfolio state
    print("\n2. Checking initial portfolio state...")
    response = requests.get(f"{BASE_URL}/api/portfolio/{USER_ID}")
    initial_portfolio = response.json()
    
    if initial_portfolio.get('success'):
        portfolio_summary = initial_portfolio.get('portfolio_summary', {})
        print(f"   Initial portfolio value: ${portfolio_summary.get('totalValue', 0)}")
        print(f"   Initial cash balance: ${portfolio_summary.get('cashBalance', 0)}")
        print(f"   Initial investments: {len(initial_portfolio.get('investments', []))}")
    else:
        print(f"   Error getting initial portfolio: {initial_portfolio.get('message')}")
        return False
    
    # Step 3: Simulate logout/login by calling portfolio endpoint again
    print("\n3. Simulating logout/login (calling portfolio endpoint again)...")
    response = requests.get(f"{BASE_URL}/api/portfolio/{USER_ID}")
    login_portfolio = response.json()
    
    if login_portfolio.get('success'):
        portfolio_summary = login_portfolio.get('portfolio_summary', {})
        print(f"   After login portfolio value: ${portfolio_summary.get('totalValue', 0)}")
        print(f"   After login cash balance: ${portfolio_summary.get('cashBalance', 0)}")
        print(f"   After login investments: {len(login_portfolio.get('investments', []))}")
        
        # Compare values
        initial_value = initial_portfolio.get('portfolio_summary', {}).get('totalValue', 0)
        login_value = login_portfolio.get('portfolio_summary', {}).get('totalValue', 0)
        
        if abs(initial_value - login_value) < 0.01:
            print(f"\n✅ SUCCESS: Portfolio values match after login!")
            print(f"   Initial: ${initial_value}")
            print(f"   After login: ${login_value}")
            return True
        else:
            print(f"\n❌ FAILURE: Portfolio values don't match after login!")
            print(f"   Initial: ${initial_value}")
            print(f"   After login: ${login_value}")
            return False
    else:
        print(f"   Error getting portfolio after login: {login_portfolio.get('message')}")
        return False

def test_user_table_sync():
    """Test that user table is properly synchronized"""
    
    print("\n🔍 Testing User Table Synchronization")
    print("=" * 40)
    
    # Get user data directly from database
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        from database_config import db_config
        
        # Get user data
        user_result = db_config.execute_query(
            "SELECT portfolio_value, cash_balance FROM users WHERE user_id = %s",
            (USER_ID,)
        )
        
        if user_result:
            user_data = user_result[0]
            portfolio_value = float(user_data['portfolio_value'])
            cash_balance = float(user_data['cash_balance'])
            
            print(f"   User table portfolio_value: ${portfolio_value}")
            print(f"   User table cash_balance: ${cash_balance}")
            
            # Get investments data
            investments_result = db_config.execute_query(
                """
                SELECT SUM(current_value) as total_value
                FROM investments 
                WHERE user_id = %s AND status = 'active'
                """,
                (USER_ID,)
            )
            
            if investments_result:
                total_investments = float(investments_result[0]['total_value']) if investments_result[0]['total_value'] else 0
                expected_portfolio_value = total_investments + cash_balance
                
                print(f"   Total investments value: ${total_investments}")
                print(f"   Expected portfolio value: ${expected_portfolio_value}")
                
                if abs(portfolio_value - expected_portfolio_value) < 0.01:
                    print("   ✅ User table is properly synchronized!")
                    return True
                else:
                    print("   ❌ User table is NOT synchronized!")
                    return False
            else:
                print("   ⚠️ No investments found")
                return False
        else:
            print("   ❌ User not found in database")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking user table: {e}")
        return False

if __name__ == "__main__":
    try:
        # Test portfolio sync
        portfolio_success = test_portfolio_sync_fix()
        
        # Test user table sync
        user_table_success = test_user_table_sync()
        
        if portfolio_success and user_table_success:
            print("\n🎉 All tests passed! Portfolio synchronization is working correctly.")
        else:
            print("\n💥 Some tests failed! Portfolio synchronization needs attention.")
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc() 