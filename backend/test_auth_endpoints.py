#!/usr/bin/env python3
"""
Authentication Endpoints Test Script
===================================

This script tests the authentication endpoints to ensure they're working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_EMAIL = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
TEST_PASSWORD = "TestPassword123!"

def test_register_endpoint():
    """Test user registration endpoint"""
    print("🔍 Testing Registration Endpoint...")
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "name": "Test User",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "risk_tolerance": "moderate",
        "investment_goal": "Wealth Growth",
        "preferred_sectors": ["technology", "finance"]
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Registration successful!")
            print(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_login_endpoint():
    """Test user login endpoint"""
    print("\n🔍 Testing Login Endpoint...")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful!")
            print(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n🔍 Testing Invalid Login...")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": TEST_EMAIL,
        "password": "WrongPassword123!"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Invalid login correctly rejected!")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_duplicate_registration():
    """Test registration with existing email"""
    print("\n🔍 Testing Duplicate Registration...")
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "name": "Test User 2",
        "email": TEST_EMAIL,  # Same email as before
        "password": "AnotherPassword123!",
        "risk_tolerance": "high",
        "investment_goal": "Retirement",
        "preferred_sectors": ["healthcare"]
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 409:
            print("✅ Duplicate registration correctly rejected!")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_invalid_registration():
    """Test registration with invalid data"""
    print("\n🔍 Testing Invalid Registration...")
    
    url = f"{BASE_URL}/auth/register"
    data = {
        "name": "",  # Empty name
        "email": "invalid-email",  # Invalid email
        "password": "123",  # Too short password
        "risk_tolerance": "moderate",
        "investment_goal": "",
        "preferred_sectors": []
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Invalid registration correctly rejected!")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def main():
    """Run all authentication tests"""
    print("=" * 60)
    print("BullBearPK Authentication Endpoints Test")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Test Password: {TEST_PASSWORD}")
    print()
    
    tests = [
        ("Registration", test_register_endpoint),
        ("Login", test_login_endpoint),
        ("Invalid Login", test_invalid_login),
        ("Duplicate Registration", test_duplicate_registration),
        ("Invalid Registration", test_invalid_registration),
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
        print("\n🎉 All authentication tests passed!")
        print("\n✅ Backend authentication endpoints are working correctly.")
        print("✅ You can now test the frontend login/register pages.")
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        print("Please check the backend server and database configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 