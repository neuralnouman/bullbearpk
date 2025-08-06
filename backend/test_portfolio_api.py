#!/usr/bin/env python3
"""
Portfolio API Test Script
=========================

This script tests the portfolio API endpoints to ensure they're working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_ID = "user_89e4b6e17e1ea088"  # Use the test user we created

def test_get_portfolio():
    """Test getting user portfolio"""
    print("🔍 Testing Get Portfolio Endpoint...")
    
    url = f"{BASE_URL}/portfolio/{TEST_USER_ID}"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Portfolio retrieved successfully!")
            
            if result.get('success'):
                portfolio_data = result
                print(f"User ID: {TEST_USER_ID}")
                
                # Check portfolio summary
                if 'portfolio_summary' in portfolio_data:
                    summary = portfolio_data['portfolio_summary']
                    print(f"Total Invested: ₨{summary.get('totalInvested', 0):,.2f}")
                    print(f"Total Value: ₨{summary.get('totalValue', 0):,.2f}")
                    print(f"Total Returns: ₨{summary.get('totalReturns', 0):,.2f}")
                    print(f"Return %: {summary.get('returnPercentage', 0):+.2f}%")
                    print(f"Cash Balance: ₨{summary.get('cashBalance', 0):,.2f}")
                    print(f"Active Investments: {summary.get('activeInvestments', 0)}")
                
                # Check investments
                if 'investments' in portfolio_data:
                    investments = portfolio_data['investments']
                    print(f"Number of investments: {len(investments)}")
                    
                    for i, inv in enumerate(investments[:3]):  # Show first 3
                        print(f"  Investment {i+1}: {inv.get('stockSymbol', 'N/A')} - {inv.get('quantity', 0)} shares")
                
                # Check allocation
                if 'allocation' in portfolio_data:
                    allocation = portfolio_data['allocation']
                    print(f"Sector allocation entries: {len(allocation)}")
                    
                    for sector in allocation[:3]:  # Show first 3
                        print(f"  {sector.get('sector', 'N/A')}: {sector.get('percentage', 0):.1f}%")
                
                return True
            else:
                print(f"❌ Portfolio request failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Portfolio request failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_portfolio_performance():
    """Test portfolio performance endpoint"""
    print("\n🔍 Testing Portfolio Performance Endpoint...")
    
    url = f"{BASE_URL}/portfolio/{TEST_USER_ID}/performance"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Portfolio performance retrieved successfully!")
            return True
        else:
            print(f"❌ Performance request failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_portfolio_holdings():
    """Test portfolio holdings endpoint"""
    print("\n🔍 Testing Portfolio Holdings Endpoint...")
    
    url = f"{BASE_URL}/portfolio/{TEST_USER_ID}/holdings"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Portfolio holdings retrieved successfully!")
            return True
        else:
            print(f"❌ Holdings request failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_sector_allocation():
    """Test sector allocation endpoint"""
    print("\n🔍 Testing Sector Allocation Endpoint...")
    
    url = f"{BASE_URL}/portfolio/{TEST_USER_ID}/sector-allocation"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sector allocation retrieved successfully!")
            return True
        else:
            print(f"❌ Sector allocation request failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def main():
    """Run all portfolio tests"""
    print("=" * 60)
    print("BullBearPK Portfolio API Test")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print()
    
    tests = [
        ("Get Portfolio", test_get_portfolio),
        ("Portfolio Performance", test_portfolio_performance),
        ("Portfolio Holdings", test_portfolio_holdings),
        ("Sector Allocation", test_sector_allocation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All portfolio tests passed!")
        print("\n✅ Backend portfolio endpoints are working correctly.")
        print("✅ Portfolio data should display properly in the frontend.")
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        print("Please check the backend server and database configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 