#!/usr/bin/env python3
"""
Detailed test to debug the agentic workflow portfolio reset issue
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_ID = "test_detailed_debug_user"

def test_detailed_agentic_debug():
    """Detailed test to debug the agentic workflow"""
    
    print("=== Detailed Agentic Workflow Debug ===")
    
    # Step 1: Create user and add investments
    print("\n1. Creating user and adding investments...")
    
    # Create user
    portfolio_response = requests.get(f"{BASE_URL}/portfolio/{TEST_USER_ID}")
    if portfolio_response.status_code != 200:
        print(f"Failed to create/get user: {portfolio_response.text}")
        return
    
    print("✓ User created/retrieved successfully")
    
    # Add cash
    cash_response = requests.post(f"{BASE_URL}/portfolio/{TEST_USER_ID}/add-cash", 
                                json={"amount": 10000})
    if cash_response.status_code == 200:
        print("✓ Added cash to portfolio")
    else:
        print(f"Failed to add cash: {cash_response.text}")
    
    # Buy stocks
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
    
    # Step 2: Check database state before workflow
    print("\n2. Checking database state before workflow...")
    try:
        import sys
        import os
        sys.path.append('backend')
        from database_config import db_config
        
        # Check investments
        investments_query = "SELECT * FROM investments WHERE user_id = %s"
        investments_result = db_config.execute_query(investments_query, (TEST_USER_ID,))
        print(f"✓ Investments before workflow: {len(investments_result)}")
        for inv in investments_result:
            print(f"  - {inv['stock_code']}: {inv['quantity']} @ {inv['buy_price']}")
        
        # Check user table
        user_query = "SELECT user_id, portfolio_value, cash_balance FROM users WHERE user_id = %s"
        user_result = db_config.execute_query(user_query, (TEST_USER_ID,))
        if user_result:
            user_data = user_result[0]
            print(f"✓ User table before workflow:")
            print(f"  - Portfolio Value: {user_data['portfolio_value']}")
            print(f"  - Cash Balance: {user_data['cash_balance']}")
        
    except Exception as e:
        print(f"Error checking database: {e}")
    
    # Step 3: Run agentic workflow with detailed logging
    print("\n3. Running agentic workflow...")
    
    workflow_data = {
        "user_input": {
            "budget": 10000,
            "risk_tolerance": "moderate",
            "time_horizon": "medium",
            "target_profit": 15
        },
        "chat_message": "I want to invest 10000 PKR with moderate risk tolerance for medium term targeting 15% profit.",
        "user_id": TEST_USER_ID,
        "refresh_data": True
    }
    
    workflow_response = requests.post(f"{BASE_URL}/hybrid", json=workflow_data)
    if workflow_response.status_code == 200:
        print("✓ Agentic workflow completed successfully")
        workflow_result = workflow_response.json()
        print(f"  - Workflow success: {workflow_result.get('success', False)}")
        print(f"  - User ID in result: {workflow_result.get('user_id', 'NOT_FOUND')}")
        
        # Check portfolio update in workflow result
        if 'data' in workflow_result and 'portfolio_update' in workflow_result['data']:
            portfolio_update = workflow_result['data']['portfolio_update']
            print(f"  - Portfolio update status: {portfolio_update.get('status', 'N/A')}")
            print(f"  - Portfolio update message: {portfolio_update.get('message', 'N/A')}")
            if portfolio_update.get('status') == 'new_user':
                print("❌ WORKFLOW DETECTED USER AS NEW!")
    else:
        print(f"Failed to run agentic workflow: {workflow_response.text}")
        return
    
    # Step 4: Check database state after workflow
    print("\n4. Checking database state after workflow...")
    try:
        # Check investments
        investments_query = "SELECT * FROM investments WHERE user_id = %s"
        investments_result = db_config.execute_query(investments_query, (TEST_USER_ID,))
        print(f"✓ Investments after workflow: {len(investments_result)}")
        for inv in investments_result:
            print(f"  - {inv['stock_code']}: {inv['quantity']} @ {inv['buy_price']}")
        
        # Check user table
        user_query = "SELECT user_id, portfolio_value, cash_balance FROM users WHERE user_id = %s"
        user_result = db_config.execute_query(user_query, (TEST_USER_ID,))
        if user_result:
            user_data = user_result[0]
            print(f"✓ User table after workflow:")
            print(f"  - Portfolio Value: {user_data['portfolio_value']}")
            print(f"  - Cash Balance: {user_data['cash_balance']}")
        
        # Check if investments were deleted
        if len(investments_result) == 0:
            print("❌ ALL INVESTMENTS WERE DELETED!")
            
            # Check if there are any deleted investments in the table
            all_investments_query = "SELECT * FROM investments WHERE user_id = %s ORDER BY buy_date DESC"
            all_investments_result = db_config.execute_query(all_investments_query, (TEST_USER_ID,))
            print(f"✓ All investments (including inactive): {len(all_investments_result)}")
            for inv in all_investments_result:
                print(f"  - {inv['stock_code']}: {inv['quantity']} @ {inv['buy_price']} (Status: {inv['status']})")
        
    except Exception as e:
        print(f"Error checking database: {e}")
    
    # Step 5: Test the get_user_investments function directly
    print("\n5. Testing get_user_investments function directly...")
    try:
        investments = db_config.get_user_investments(TEST_USER_ID)
        print(f"✓ get_user_investments returned: {len(investments)} investments")
        for inv in investments:
            print(f"  - {inv['stock_code']}: {inv['quantity']} @ {inv['buy_price']}")
    except Exception as e:
        print(f"Error testing get_user_investments: {e}")
    
    print("\n=== Debug completed ===")

if __name__ == "__main__":
    test_detailed_agentic_debug() 