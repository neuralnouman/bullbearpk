#!/usr/bin/env python3
"""
Test script to simulate the exact frontend flow and check for portfolio reset
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_ID = "test_frontend_reset_user"

def test_frontend_agentic_reset():
    """Test to simulate the exact frontend flow"""
    
    print("=== Testing Frontend Agentic Reset Issue ===")
    
    # Step 1: Simulate user login and portfolio setup
    print("\n1. Setting up user portfolio (simulating login)...")
    
    # Create user by calling portfolio endpoint (simulates frontend login)
    portfolio_response = requests.get(f"{BASE_URL}/portfolio/{TEST_USER_ID}")
    if portfolio_response.status_code != 200:
        print(f"Failed to create/get user: {portfolio_response.text}")
        return
    
    print("✓ User created/retrieved successfully")
    
    # Add cash to portfolio
    cash_response = requests.post(f"{BASE_URL}/portfolio/{TEST_USER_ID}/add-cash", 
                                json={"amount": 10000})
    if cash_response.status_code == 200:
        print("✓ Added cash to portfolio")
    else:
        print(f"Failed to add cash: {cash_response.text}")
    
    # Buy some stocks (using correct field names)
    buy_response = requests.post(f"{BASE_URL}/portfolio/{TEST_USER_ID}/investments",
                               json={
                                   "stock_code": "OGDC",
                                   "stock_name": "Oil & Gas Development Company",
                                   "quantity": 100,
                                   "price": 85.50,
                                   "transaction_type": "buy"
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
        
        # Store the before values
        before_total_value = portfolio_data.get('portfolio_summary', {}).get('totalValue', 0)
        before_cash_balance = portfolio_data.get('portfolio_summary', {}).get('cashBalance', 0)
        before_investments = len(portfolio_data.get('investments', []))
    else:
        print(f"Failed to get portfolio: {portfolio_before.text}")
        return
    
    # Step 3: Simulate the exact agentic workflow call from frontend
    print("\n3. Running agentic workflow (simulating frontend refresh analysis)...")
    
    # This is the exact call that the frontend makes
    workflow_data = {
        "user_input": {
            "budget": 10000,
            "risk_tolerance": "moderate",
            "time_horizon": "medium",
            "target_profit": 15
        },
        "chat_message": "I want to invest 10000 PKR with moderate risk tolerance for medium term targeting 15% profit.",
        "user_id": TEST_USER_ID,
        "refresh_data": True  # This is what the frontend sends
    }
    
    workflow_response = requests.post(f"{BASE_URL}/hybrid", json=workflow_data)
    if workflow_response.status_code == 200:
        print("✓ Agentic workflow completed successfully")
        workflow_result = workflow_response.json()
        print(f"  - Workflow success: {workflow_result.get('success', False)}")
        print(f"  - User ID in result: {workflow_result.get('user_id', 'NOT_FOUND')}")
        
        # Check if the workflow result contains any portfolio reset logic
        if 'portfolio_update' in workflow_result.get('data', {}):
            portfolio_update = workflow_result['data']['portfolio_update']
            print(f"  - Portfolio update in workflow: {portfolio_update.get('status', 'N/A')}")
            if portfolio_update.get('status') == 'new_user':
                print("❌ WORKFLOW DETECTED USER AS NEW!")
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
        
        after_total_value = portfolio_data.get('portfolio_summary', {}).get('totalValue', 0)
        after_cash_balance = portfolio_data.get('portfolio_summary', {}).get('cashBalance', 0)
        after_investments = len(portfolio_data.get('investments', []))
        
        # Check if portfolio was reset
        if (after_total_value < before_total_value or 
            after_cash_balance < before_cash_balance or 
            after_investments < before_investments):
            print("❌ PORTFOLIO WAS RESET!")
            print(f"  - Total Value: {before_total_value} -> {after_total_value}")
            print(f"  - Cash Balance: {before_cash_balance} -> {after_cash_balance}")
            print(f"  - Investments: {before_investments} -> {after_investments}")
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
    
    # Step 6: Check if there are any database operations that might reset the portfolio
    print("\n6. Checking for any database operations that might reset portfolio...")
    try:
        import sys
        import os
        sys.path.append('backend')
        from database_config import db_config
        
        # Check if any portfolio-related tables were modified
        investments_query = "SELECT COUNT(*) as count FROM investments WHERE user_id = %s"
        investments_result = db_config.execute_query(investments_query, (TEST_USER_ID,))
        
        if investments_result:
            investment_count = investments_result[0]['count']
            print(f"✓ Investment count: {investment_count}")
        else:
            print("❌ Could not check investment count")
            
    except Exception as e:
        print(f"Error checking database operations: {e}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_frontend_agentic_reset() 