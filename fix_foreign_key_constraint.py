#!/usr/bin/env python3
"""
Script to fix the foreign key constraint that's causing investments to be deleted
"""

import sys
import os
sys.path.append('backend')
from database_config import db_config

def fix_foreign_key_constraint():
    """Fix the foreign key constraint to prevent cascade delete of investments"""
    
    print("=== Fixing Foreign Key Constraint ===")
    
    try:
        # First, drop the existing foreign key constraint
        print("\n1. Dropping existing foreign key constraint...")
        drop_fk_query = """
        ALTER TABLE investments 
        DROP FOREIGN KEY investments_ibfk_2
        """
        
        try:
            db_config.execute_query(drop_fk_query)
            print("✓ Dropped existing foreign key constraint")
        except Exception as e:
            print(f"Warning: Could not drop foreign key constraint: {e}")
            print("This might be because the constraint name is different")
        
        # Add the new foreign key constraint with RESTRICT
        print("\n2. Adding new foreign key constraint with RESTRICT...")
        add_fk_query = """
        ALTER TABLE investments 
        ADD CONSTRAINT investments_ibfk_2 
        FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE RESTRICT
        """
        
        try:
            db_config.execute_query(add_fk_query)
            print("✓ Added new foreign key constraint with RESTRICT")
        except Exception as e:
            print(f"Error adding new foreign key constraint: {e}")
            return False
        
        # Test the constraint by trying to delete a stock that has investments
        print("\n3. Testing the constraint...")
        
        # First, check if there are any investments
        investments_query = "SELECT DISTINCT stock_code FROM investments WHERE status = 'active' LIMIT 1"
        investments_result = db_config.execute_query(investments_query)
        
        if investments_result:
            test_stock_code = investments_result[0]['stock_code']
            print(f"✓ Found investment for stock: {test_stock_code}")
            
            # Try to delete this stock (should fail due to RESTRICT)
            test_delete_query = "DELETE FROM stocks WHERE code = %s"
            try:
                db_config.execute_query(test_delete_query, (test_stock_code,))
                print("❌ ERROR: Stock was deleted despite RESTRICT constraint!")
                return False
            except Exception as e:
                if "foreign key constraint fails" in str(e).lower():
                    print("✓ Foreign key constraint working correctly - prevented deletion")
                else:
                    print(f"Unexpected error: {e}")
                    return False
        else:
            print("✓ No active investments found for testing")
        
        print("\n✓ Foreign key constraint fixed successfully!")
        return True
        
    except Exception as e:
        print(f"Error fixing foreign key constraint: {e}")
        return False

if __name__ == "__main__":
    success = fix_foreign_key_constraint()
    if success:
        print("\n=== Foreign key constraint fixed successfully ===")
    else:
        print("\n=== Failed to fix foreign key constraint ===") 