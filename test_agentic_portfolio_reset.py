#!/usr/bin/env python3
"""
Test script to reproduce the portfolio reset issue when running agentic workflow
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_ID = "test_agentic_reset_user"

def test_agentic_workflow_portfolio_reset():
    """Test to reproduce the portfolio reset issue"""
    
    print("=== Testing Agentic Workflow Portfolio Reset Issue ===")
    
    # Step 1: Create a user and add some investments
    print("\n1. Creating test user and adding investments...")
    
    # Create user by calling portfolio endpoint
    portfolio_response = requests.get(f"{BASE_URL}/portfolio/{TEST_USER_ID}")
    if portfolio_response.status_code != 200:
        print(f"Failed to create/get user: {portfolio_response.text}")
        return
    
    print("✓ User created/retrieved successfully")
    
    # Add cash to portfolio
    cash_response = requests.post(f"{BASE_URL}/portfolio/{TEST_USER_ID}/add-cash", 
                                json={"amount": 5000})
    if cash_response.status_code == 200:
        print("✓ Added cash to portfolio")
    else:
        print(f"Failed to add cash: {cash_response.text}")
    
    # Buy some stocks
    buy_response = requests.post(f"{BASE_URL}/portfolio/{TEST_USER_ID}/investments",
                               json={
                                   "stock_code": "OGDC",
                                   "stock_name": "Oil & Gas Development Company",
                                   "quantity": 100,
                                   "buy_price": 85.50,
                                   "sector": "Energy"
                               })
    if buy_response.status_code == 200:
        print("✓ Bought OGDC stocks")
    else:
        print(f"Failed to buy stocks: {buy_response.text}")
    
    # Step 2: Check portfolio before agentic workflow
    print("\n2. Checking portfolio before agentic workflow...")
    portfolio_before = requests.get(f"{BASE_URL}/portfolio/{TEST_USER_ID}")
    if portfolio_before.status_code == 200:
        portfolio_data = portfolio_before.json()
        print(f"✓ Portfolio before workflow:")
        print(f"  - Total Value: {portfolio_data.get('portfolio_summary', {}).get('totalValue', 0)}")
        print(f"  - Cash Balance: {portfolio_data.get('portfolio_summary', {}).get('cashBalance', 0)}")
        print(f"  - Investments: {len(portfolio_data.get('investments', []))}")
    else:
        print(f"Failed to get portfolio: {portfolio_before.text}")
        return
    
    # Step 3: Run agentic workflow
    print("\n3. Running agentic workflow...")
    
    workflow_data = {
        "user_input": {
            "budget": 10000,
            "risk_tolerance": "moderate",
            "time_horizon": "medium",
            "target_profit": 15
        },
        "chat_message": "I want to invest 10000 PKR with moderate risk tolerance for medium term targeting 15% profit.",
        "user_id": TEST_USER_ID
    }
    
    workflow_response = requests.post(f"{BASE_URL}/hybrid", json=workflow_data)
    if workflow_response.status_code == 200:
        print("✓ Agentic workflow completed successfully")
        workflow_result = workflow_response.json()
        print(f"  - Workflow success: {workflow_result.get('success', False)}")
        print(f"  - User ID in result: {workflow_result.get('user_id', 'NOT_FOUND')}")
    else:
        print(f"Failed to run agentic workflow: {workflow_response.text}")
        return
    
    # Step 4: Check portfolio after agentic workflow
    print("\n4. Checking portfolio after agentic workflow...")
    portfolio_after = requests.get(f"{BASE_URL}/portfolio/{TEST_USER_ID}")
    if portfolio_after.status_code == 200:
        portfolio_data = portfolio_after.json()
        print(f"✓ Portfolio after workflow:")
        print(f"  - Total Value: {portfolio_data.get('portfolio_summary', {}).get('totalValue', 0)}")
        print(f"  - Cash Balance: {portfolio_data.get('portfolio_summary', {}).get('cashBalance', 0)}")
        print(f"  - Investments: {len(portfolio_data.get('investments', []))}")
        
        # Check if portfolio was reset
        before_value = portfolio_before.json().get('portfolio_summary', {}).get('totalValue', 0)
        after_value = portfolio_data.get('portfolio_summary', {}).get('totalValue', 0)
        
        if after_value < before_value:
            print("❌ PORTFOLIO WAS RESET!")
            print(f"  - Before: {before_value}")
            print(f"  - After: {after_value}")
            print(f"  - Difference: {before_value - after_value}")
        else:
            print("✓ Portfolio was not reset")
    else:
        print(f"Failed to get portfolio after workflow: {portfolio_after.text}")
    
    # Step 5: Check user table directly
    print("\n5. Checking user table directly...")
    try:
        import sys
        import os
        sys.path.append('backend')
        from database_config import db_config
        
        user_query = "SELECT user_id, portfolio_value, cash_balance FROM users WHERE user_id = %s"
        user_result = db_config.execute_query(user_query, (TEST_USER_ID,))
        
        if user_result:
            user_data = user_result[0]
            print(f"✓ User table data:")
            print(f"  - User ID: {user_data['user_id']}")
            print(f"  - Portfolio Value: {user_data['portfolio_value']}")
            print(f"  - Cash Balance: {user_data['cash_balance']}")
        else:
            print("❌ User not found in database")
    except Exception as e:
        print(f"Error checking user table: {e}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_agentic_workflow_portfolio_reset() 