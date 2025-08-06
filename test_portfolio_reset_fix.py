#!/usr/bin/env python3
"""
Test script to verify that the portfolio reset issue has been fixed.
This script simulates the AI analysis workflow and checks if the portfolio gets reset.
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000"
USER_ID = "test_user_123"

def test_portfolio_reset_fix():
    """Test that portfolio doesn't get reset when AI analysis workflow runs"""
    
    print("🧪 Testing Portfolio Reset Fix")
    print("=" * 50)
    
    # Step 1: Create initial portfolio with some investments
    print("\n1. Creating initial portfolio with investments...")
    
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
    
    # Step 2: Get initial portfolio state
    print("\n2. Getting initial portfolio state...")
    response = requests.get(f"{BASE_URL}/api/portfolio/{USER_ID}")
    initial_portfolio = response.json()
    
    if initial_portfolio.get('success'):
        initial_investments = initial_portfolio.get('investments', [])
        print(f"   Initial portfolio has {len(initial_investments)} investments")
        for inv in initial_investments:
            print(f"   - {inv['stockSymbol']}: {inv['quantity']} shares")
    else:
        print(f"   Error getting initial portfolio: {initial_portfolio.get('message')}")
        return False
    
    # Step 3: Run AI analysis workflow (simulate multiple runs)
    print("\n3. Running AI analysis workflow multiple times...")
    
    for i in range(3):
        print(f"   Running AI analysis workflow #{i+1}...")
        
        # Simulate the agentic workflow
        workflow_data = {
            "user_input": {
                "budget": 5000,
                "risk_tolerance": "moderate",
                "time_horizon": "medium",
                "target_profit": 10
            },
            "chat_message": "I want to invest 5000 PKR with moderate risk tolerance",
            "user_id": USER_ID
        }
        
        response = requests.post(f"{BASE_URL}/api/hybrid", json=workflow_data)
        workflow_result = response.json()
        
        if workflow_result.get('success'):
            print(f"   ✅ AI analysis workflow #{i+1} completed successfully")
        else:
            print(f"   ❌ AI analysis workflow #{i+1} failed: {workflow_result.get('message')}")
        
        # Small delay between runs
        time.sleep(1)
    
    # Step 4: Check final portfolio state
    print("\n4. Checking final portfolio state...")
    response = requests.get(f"{BASE_URL}/api/portfolio/{USER_ID}")
    final_portfolio = response.json()
    
    if final_portfolio.get('success'):
        final_investments = final_portfolio.get('investments', [])
        print(f"   Final portfolio has {len(final_investments)} investments")
        for inv in final_investments:
            print(f"   - {inv['stockSymbol']}: {inv['quantity']} shares")
        
        # Compare initial and final states
        initial_count = len(initial_investments)
        final_count = len(final_investments)
        
        if initial_count == final_count:
            print(f"\n✅ SUCCESS: Portfolio maintained {initial_count} investments after AI analysis workflow")
            print("   The portfolio reset issue has been fixed!")
            return True
        else:
            print(f"\n❌ FAILURE: Portfolio changed from {initial_count} to {final_count} investments")
            print("   The portfolio reset issue still exists!")
            return False
    else:
        print(f"   Error getting final portfolio: {final_portfolio.get('message')}")
        return False

if __name__ == "__main__":
    try:
        success = test_portfolio_reset_fix()
        if success:
            print("\n🎉 Test completed successfully!")
        else:
            print("\n💥 Test failed!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc() 