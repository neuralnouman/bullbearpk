#!/usr/bin/env python3
"""
Test Add Cash Fix
==================

This script tests that adding cash properly updates the portfolio value in the users table.
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000"
USER_ID = "test_add_cash_user_123"

def test_add_cash_fix():
    """Test that adding cash properly updates portfolio value"""
    
    print("🧪 Testing Add Cash Fix")
    print("=" * 40)
    
    # Step 1: Get initial portfolio state
    print("\n1. Getting initial portfolio state...")
    response = requests.get(f"{BASE_URL}/api/portfolio/{USER_ID}")
    initial_portfolio = response.json()
    
    if initial_portfolio.get('success'):
        portfolio_summary = initial_portfolio.get('portfolio_summary', {})
        initial_cash = portfolio_summary.get('cashBalance', 0)
        initial_portfolio_value = portfolio_summary.get('totalValue', 0)
        print(f"   Initial cash balance: ${initial_cash}")
        print(f"   Initial portfolio value: ${initial_portfolio_value}")
    else:
        print(f"   Error getting initial portfolio: {initial_portfolio.get('message')}")
        return False
    
    # Step 2: Add cash
    print("\n2. Adding cash to portfolio...")
    cash_amount = 5000.0
    response = requests.post(
        f"{BASE_URL}/api/portfolio/{USER_ID}/add-cash",
        json={"amount": cash_amount}
    )
    add_cash_result = response.json()
    
    if add_cash_result.get('success'):
        print(f"   Successfully added ${cash_amount}")
        print(f"   New cash balance: ${add_cash_result.get('new_cash_balance', 0)}")
    else:
        print(f"   Error adding cash: {add_cash_result.get('message')}")
        return False
    
    # Step 3: Check updated portfolio state
    print("\n3. Checking updated portfolio state...")
    response = requests.get(f"{BASE_URL}/api/portfolio/{USER_ID}")
    updated_portfolio = response.json()
    
    if updated_portfolio.get('success'):
        portfolio_summary = updated_portfolio.get('portfolio_summary', {})
        updated_cash = portfolio_summary.get('cashBalance', 0)
        updated_portfolio_value = portfolio_summary.get('totalValue', 0)
        print(f"   Updated cash balance: ${updated_cash}")
        print(f"   Updated portfolio value: ${updated_portfolio_value}")
        
        # Verify the values are correct
        expected_cash = initial_cash + cash_amount
        expected_portfolio_value = initial_portfolio_value + cash_amount
        
        if abs(updated_cash - expected_cash) < 0.01:
            print(f"   ✅ Cash balance updated correctly!")
        else:
            print(f"   ❌ Cash balance not updated correctly!")
            print(f"      Expected: ${expected_cash}, Got: ${updated_cash}")
            return False
        
        if abs(updated_portfolio_value - expected_portfolio_value) < 0.01:
            print(f"   ✅ Portfolio value updated correctly!")
        else:
            print(f"   ❌ Portfolio value not updated correctly!")
            print(f"      Expected: ${expected_portfolio_value}, Got: ${updated_portfolio_value}")
            return False
        
        return True
    else:
        print(f"   Error getting updated portfolio: {updated_portfolio.get('message')}")
        return False

def test_user_table_sync():
    """Test that user table is properly synchronized after adding cash"""
    
    print("\n🔍 Testing User Table Synchronization After Adding Cash")
    print("=" * 60)
    
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
                    print("   ✅ User table is properly synchronized after adding cash!")
                    return True
                else:
                    print("   ❌ User table is NOT synchronized after adding cash!")
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
        # Test add cash functionality
        add_cash_success = test_add_cash_fix()
        
        # Test user table sync
        user_table_success = test_user_table_sync()
        
        if add_cash_success and user_table_success:
            print("\n🎉 All tests passed! Add cash functionality is working correctly.")
        else:
            print("\n💥 Some tests failed! Add cash functionality needs attention.")
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc() 