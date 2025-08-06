#!/usr/bin/env python3
"""
Check investments table structure
"""

from database_config import db_config

def check_investments_table():
    """Check the investments table structure"""
    try:
        print("Checking investments table structure...")
        
        # Get table structure
        result = db_config.execute_query("DESCRIBE investments")
        if result:
            print("✓ Investments table exists")
            print("\nTable structure:")
            for column in result:
                print(f"  {column['Field']} - {column['Type']} - {column['Null']} - {column['Key']} - {column['Default']}")
        else:
            print("✗ Investments table does not exist")
            return False
        
        # Check if table has data
        count_result = db_config.execute_query("SELECT COUNT(*) as count FROM investments")
        if count_result:
            count = count_result[0]['count']
            print(f"\n✓ Investments table has {count} records")
        else:
            print("\n✗ No data in investments table")
        
        # Check specific columns that might be missing
        required_columns = [
            'user_id', 'stock_code', 'stock_name', 'sector', 'transaction_type',
            'quantity', 'buy_price', 'total_invested', 'current_quantity',
            'current_price', 'current_value', 'market_value', 'status',
            'investment_duration_days', 'created_by', 'source', 'user_notes', 'tags'
        ]
        
        print(f"\nChecking required columns:")
        existing_columns = [col['Field'] for col in result]
        
        for column in required_columns:
            if column in existing_columns:
                print(f"  ✓ {column}")
            else:
                print(f"  ✗ {column} - MISSING")
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking investments table: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    check_investments_table() 