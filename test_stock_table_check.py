#!/usr/bin/env python3
"""
Test script to check stocks table and understand the JOIN issue
"""

import sys
import os
sys.path.append('backend')
from database_config import db_config

def test_stock_table():
    """Test to check stocks table and investments JOIN issue"""
    
    print("=== Testing Stocks Table and JOIN Issue ===")
    
    # Check if OGDC exists in stocks table
    print("\n1. Checking if OGDC exists in stocks table...")
    stock_query = "SELECT * FROM stocks WHERE code = 'OGDC'"
    stock_result = db_config.execute_query(stock_query)
    
    if stock_result:
        print(f"✓ OGDC found in stocks table:")
        for key, value in stock_result[0].items():
            print(f"  - {key}: {value}")
    else:
        print("❌ OGDC not found in stocks table")
    
    # Check all stocks in the table
    print("\n2. Checking all stocks in the table...")
    all_stocks_query = "SELECT code, name FROM stocks LIMIT 10"
    all_stocks_result = db_config.execute_query(all_stocks_query)
    
    if all_stocks_result:
        print(f"✓ Found {len(all_stocks_result)} stocks in table:")
        for stock in all_stocks_result:
            print(f"  - {stock['code']}: {stock['name']}")
    else:
        print("❌ No stocks found in table")
    
    # Check investments for our test user
    print("\n3. Checking investments for test user...")
    investments_query = "SELECT * FROM investments WHERE user_id = 'test_frontend_reset_user'"
    investments_result = db_config.execute_query(investments_query)
    
    if investments_result:
        print(f"✓ Found {len(investments_result)} investments:")
        for inv in investments_result:
            print(f"  - Stock: {inv['stock_code']}, Quantity: {inv['quantity']}, Status: {inv['status']}")
    else:
        print("❌ No investments found")
    
    # Test the JOIN query that's failing
    print("\n4. Testing the JOIN query that's failing...")
    join_query = """
    SELECT i.*, s.name as stock_name, s.sector 
    FROM investments i 
    JOIN stocks s ON i.stock_code = s.code 
    WHERE i.user_id = 'test_frontend_reset_user' AND i.status = 'active'
    """
    join_result = db_config.execute_query(join_query)
    
    if join_result:
        print(f"✓ JOIN query returned {len(join_result)} results")
        for inv in join_result:
            print(f"  - Stock: {inv['stock_code']}, Name: {inv['stock_name']}, Sector: {inv['sector']}")
    else:
        print("❌ JOIN query returned no results - this is the problem!")
    
    # Test LEFT JOIN to see what we get
    print("\n5. Testing LEFT JOIN to see what we get...")
    left_join_query = """
    SELECT i.*, s.name as stock_name, s.sector 
    FROM investments i 
    LEFT JOIN stocks s ON i.stock_code = s.code 
    WHERE i.user_id = 'test_frontend_reset_user' AND i.status = 'active'
    """
    left_join_result = db_config.execute_query(left_join_query)
    
    if left_join_result:
        print(f"✓ LEFT JOIN query returned {len(left_join_result)} results")
        for inv in left_join_result:
            print(f"  - Stock: {inv['stock_code']}, Name: {inv['stock_name']}, Sector: {inv['sector']}")
    else:
        print("❌ LEFT JOIN query also returned no results")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_stock_table() 