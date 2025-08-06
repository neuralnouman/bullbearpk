#!/usr/bin/env python3
"""
Test the agentic workflow to ensure it runs when form is submitted
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_agentic_workflow():
    """Test the agentic workflow with form data"""
    try:
        # Test data matching the form structure (without sector)
        test_form_data = {
            "budget": 10000,
            "risk_appetite": "medium",
            "time_horizon": "medium",
            "target_profit": 15
        }
        
        # Convert to agentic framework input
        user_input = {
            "budget": test_form_data["budget"],
            "risk_tolerance": test_form_data["risk_appetite"],
            "time_horizon": test_form_data["time_horizon"],
            "target_profit": test_form_data["target_profit"],
            "investment_goal": "growth"
        }
        
        chat_message = f"I want to invest {test_form_data['budget']} PKR with {test_form_data['risk_appetite']} risk tolerance for {test_form_data['time_horizon']} term targeting {test_form_data['target_profit']}% profit."
        
        # Prepare request payload
        payload = {
            "user_input": user_input,
            "chat_message": chat_message,
            "user_id": "test_user_123",
            "refresh_data": False
        }
        
        print("=== Testing Agentic Workflow ===")
        print(f"User Input: {user_input}")
        print(f"Chat Message: {chat_message}")
        print(f"User ID: test_user_123")
        
        # Make request to the hybrid endpoint
        response = requests.post(
            "http://localhost:5000/api/hybrid",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minutes timeout
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Agentic workflow executed successfully!")
            print(f"Success: {result.get('success', False)}")
            print(f"Message: {result.get('message', 'No message')}")
            
            # Check if recommendations were generated
            if 'data' in result and 'recommendations' in result['data']:
                recommendations = result['data']['recommendations']
                print(f"📊 Generated {len(recommendations)} recommendations")
                for i, rec in enumerate(recommendations[:3]):  # Show first 3
                    print(f"  {i+1}. {rec.get('stock_code', 'N/A')} - {rec.get('company_name', 'N/A')}")
            
            # Check if stock analysis was performed
            if 'data' in result and 'stock_analysis' in result['data']:
                analysis = result['data']['stock_analysis']
                print(f"📈 Stock analysis performed for {len(analysis)} stocks")
            
            # Check if news analysis was performed
            if 'data' in result and 'news_analysis' in result['data']:
                news = result['data']['news_analysis']
                print(f"📰 News analysis performed for {len(news)} companies")
            
            return True
        else:
            print("❌ Agentic workflow failed!")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on http://localhost:5000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: The agentic workflow is taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_agentic_workflow() 