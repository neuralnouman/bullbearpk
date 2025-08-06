#!/usr/bin/env python3
"""
Test script to verify frontend re-rendering fix
Tests that adding cash properly updates the portfolio values and they are correctly reflected in the API response.
"""

import requests
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database_config import DatabaseConfig

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_ID = "test_user_frontend_fix"

def test_frontend_rerender_fix():
    """Test that frontend re-rendering fix is working correctly"""
    
    print("🧪 Testing Frontend Re-rendering Fix")
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
    print(f"   Initial total value: ${initial_summary['totalValue']:.2f}")
    print(f"   Initial cash balance: ${initial_summary['cashBalance']:.2f}")
    print(f"   Initial total invested: ${initial_summary['totalInvested']:.2f}")
    
    # Test 2: Add cash and verify no double-counting
    print("\n💰 Test 2: Add Cash and Verify No Double-Counting")
    print("-" * 40)
    
    cash_amount = 5000
    add_cash_result = add_cash_to_portfolio(TEST_USER_ID, cash_amount)
    
    if not add_cash_result['success']:
        print("❌ Failed to add cash to portfolio")
        return False
    
    print(f"   Added cash: ${cash_amount:.2f}")
    print(f"   Response message: {add_cash_result['message']}")
    
    # Get updated portfolio
    updated_portfolio = get_portfolio(TEST_USER_ID)
    if not updated_portfolio['success']:
        print("❌ Failed to get updated portfolio")
        return False
    
    updated_summary = updated_portfolio['portfolio_summary']
    print(f"   Updated total value: ${updated_summary['totalValue']:.2f}")
    print(f"   Updated cash balance: ${updated_summary['cashBalance']:.2f}")
    print(f"   Updated total invested: ${updated_summary['totalInvested']:.2f}")
    
    # Verify the values are correct (no double-counting)
    expected_cash_balance = 10000 + cash_amount  # Initial 10000 + added 5000
    expected_total_value = expected_cash_balance  # Only cash, no investments
    
    print(f"\n🔍 Verification:")
    print(f"   Expected cash balance: ${expected_cash_balance:.2f}")
    print(f"   Expected total value: ${expected_total_value:.2f}")
    print(f"   Actual cash balance: ${updated_summary['cashBalance']:.2f}")
    print(f"   Actual total value: ${updated_summary['totalValue']:.2f}")
    
    # Check if values match expectations
    cash_balance_correct = abs(updated_summary['cashBalance'] - expected_cash_balance) < 0.01
    total_value_correct = abs(updated_summary['totalValue'] - expected_total_value) < 0.01
    
    if cash_balance_correct and total_value_correct:
        print("   ✅ Cash balance and total value are correct (no double-counting)")
        return True
    else:
        print("   ❌ Values are incorrect - double-counting detected")
        if not cash_balance_correct:
            print(f"      Cash balance mismatch: expected {expected_cash_balance}, got {updated_summary['cashBalance']}")
        if not total_value_correct:
            print(f"      Total value mismatch: expected {expected_total_value}, got {updated_summary['totalValue']}")
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
            INSERT INTO users (user_id, name, email, risk_tolerance, investment_goal, initial_cash, cash_balance, portfolio_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (TEST_USER_ID, "Test User", "test@example.com", "moderate", "growth", 10000, 10000, 10000)
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

def add_cash_to_portfolio(user_id, amount):
    """Add cash to portfolio"""
    try:
        response = requests.post(
            f"{BASE_URL}/portfolio/{user_id}/add-cash",
            json={"amount": amount},
            headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        print(f"❌ Error adding cash: {e}")
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    try:
        success = test_frontend_rerender_fix()
        if success:
            print("\n🎉 Frontend re-rendering fix test PASSED!")
            print("✅ The frontend should now correctly display updated values without double-counting")
        else:
            print("\n💥 Frontend re-rendering fix test FAILED!")
            print("❌ There may still be issues with value calculation or display")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 