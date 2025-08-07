#!/usr/bin/env python3
"""
Check if database migration has been applied
"""

import mysql.connector
from mysql.connector import Error

def check_migration():
    connection = None
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Add your password if needed
            database='bullbearpk'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Check if total_invested column exists in users table
            cursor.execute("DESCRIBE users")
            columns = [column[0] for column in cursor.fetchall()]
            
            if 'total_invested' in columns and 'total_returns' in columns:
                print("✅ Migration has been applied successfully!")
                print("The 'total_invested' and 'total_returns' columns exist in the users table.")
                
                # Check if there's data in these columns
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE total_invested IS NOT NULL OR total_returns IS NOT NULL")
                result = cursor.fetchone()
                
                if result[0] > 0:
                    print(f"✅ Found {result[0]} users with portfolio data in the new columns.")
                else:
                    print("⚠️  No users have portfolio data in the new columns yet.")
                    print("   This is normal for new users or if no investments have been made.")
                    
            else:
                print("❌ Migration has NOT been applied!")
                print("Missing columns in users table:")
                if 'total_invested' not in columns:
                    print("   - total_invested")
                if 'total_returns' not in columns:
                    print("   - total_returns")
                print("\nPlease run the migration script:")
                print("   mysql -u root -p bullbearpk < backend/database/migration_add_portfolio_columns.sql")
                
    except Error as e:
        print(f"❌ Database connection error: {e}")
        print("Please make sure MySQL is running and the database exists.")
        print("You may need to provide the correct password for the root user.")
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_migration() 