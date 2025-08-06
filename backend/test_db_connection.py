#!/usr/bin/env python3
"""
Test database connection and table structure
"""

from database_config import db_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and basic queries"""
    try:
        # Test connection
        print("Testing database connection...")
        if db_config.test_connection():
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
            return False
        
        # Test if tables exist
        print("\nTesting table existence...")
        tables_to_check = ['users', 'stocks', 'investments', 'portfolios']
        
        for table in tables_to_check:
            try:
                result = db_config.execute_query(f"SHOW TABLES LIKE '{table}'")
                if result:
                    print(f"✓ Table '{table}' exists")
                else:
                    print(f"✗ Table '{table}' does not exist")
            except Exception as e:
                print(f"✗ Error checking table '{table}': {e}")
        
        # Test if stocks table has data
        print("\nTesting stocks data...")
        stocks_result = db_config.execute_query("SELECT COUNT(*) as count FROM stocks")
        if stocks_result:
            count = stocks_result[0]['count']
            print(f"✓ Stocks table has {count} records")
        else:
            print("✗ No stocks data found")
        
        # Test if users table has data
        print("\nTesting users data...")
        users_result = db_config.execute_query("SELECT COUNT(*) as count FROM users")
        if users_result:
            count = users_result[0]['count']
            print(f"✓ Users table has {count} records")
        else:
            print("✗ No users data found")
        
        # Test specific user
        print("\nTesting specific user...")
        test_user = "user_89e4b6e17e1ea088"
        user_result = db_config.execute_query("SELECT * FROM users WHERE user_id = %s", (test_user,))
        if user_result:
            user = user_result[0]
            print(f"✓ User found: {user['user_id']}")
            print(f"  Cash balance: {user['cash_balance']}")
            print(f"  Portfolio value: {user['portfolio_value']}")
        else:
            print(f"✗ User {test_user} not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection() 