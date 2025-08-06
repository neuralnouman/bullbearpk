#!/usr/bin/env python3
"""
Create Test User Script
=======================

This script creates a test user in the database for authentication testing.
"""

import sys
import os
from datetime import datetime
import hashlib
import json

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id() -> str:
    """Generate unique user ID"""
    import secrets
    return f"user_{secrets.token_hex(8)}"

def create_test_user():
    """Create a test user for authentication testing"""
    
    db = DatabaseConfig()
    
    # Test user credentials
    test_email = "test@example.com"
    test_password = "Password123!"
    test_name = "Test User"
    
    print("🔍 Creating test user for authentication...")
    print(f"Email: {test_email}")
    print(f"Password: {test_password}")
    print(f"Name: {test_name}")
    print()
    
    try:
        # Check if user already exists
        existing_user = db.execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (test_email,)
        )
        
        if existing_user:
            print("⚠️  User already exists. Updating password...")
            
            # Update the password
            hashed_password = hash_password(test_password)
            update_query = """
                UPDATE users 
                SET password = %s, updated_at = %s 
                WHERE email = %s
            """
            db.execute_query(update_query, (hashed_password, datetime.now(), test_email))
            print("✅ Password updated successfully!")
            
        else:
            print("➕ Creating new test user...")
            
            # Generate user ID and hash password
            user_id = generate_user_id()
            hashed_password = hash_password(test_password)
            
            # Create user in database
            insert_query = """
                INSERT INTO users (
                    user_id, name, email, password, risk_tolerance,
                    investment_goal, preferred_sectors, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            user_params = (
                user_id,
                test_name,
                test_email,
                hashed_password,
                'moderate',
                'Wealth Growth',
                json.dumps(['technology', 'finance']),
                datetime.now(),
                datetime.now()
            )
            
            db.execute_query(insert_query, user_params)
            print("✅ Test user created successfully!")
        
        # Verify the user was created/updated
        verify_user = db.execute_query(
            "SELECT user_id, name, email, risk_tolerance, investment_goal FROM users WHERE email = %s",
            (test_email,)
        )
        
        if verify_user:
            user = verify_user[0]
            print("\n📋 Test User Details:")
            print(f"User ID: {user['user_id']}")
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"Risk Tolerance: {user['risk_tolerance']}")
            print(f"Investment Goal: {user['investment_goal']}")
            print()
            print("✅ Test user is ready for authentication testing!")
            print("\n🎯 You can now use these credentials to test login:")
            print(f"   Email: {test_email}")
            print(f"   Password: {test_password}")
            
        else:
            print("❌ Failed to verify user creation")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False
    
    return True

def test_login():
    """Test the login functionality with the created user"""
    
    print("\n🔍 Testing login functionality...")
    
    # Test credentials
    test_email = "test@example.com"
    test_password = "Password123!"
    
    # Hash the password for verification
    hashed_password = hash_password(test_password)
    
    db = DatabaseConfig()
    
    try:
        # Check if user exists and password matches
        user = db.execute_query(
            "SELECT user_id, name, email FROM users WHERE email = %s AND password = %s",
            (test_email, hashed_password)
        )
        
        if user:
            print("✅ Login test successful!")
            print(f"User found: {user[0]['name']} ({user[0]['email']})")
            return True
        else:
            print("❌ Login test failed - user not found or password incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("BullBearPK Test User Creation")
    print("=" * 60)
    
    # Create test user
    if create_test_user():
        # Test login
        test_login()
        
        print("\n" + "=" * 60)
        print("✅ Test user setup completed!")
        print("=" * 60)
        print("\n🎯 Ready for frontend testing!")
        print("Use these credentials in the login/register forms:")
        print("   Email: test@example.com")
        print("   Password: Password123!")
        print("\n📝 Note: If you get a 409 CONFLICT error during registration,")
        print("   it means the email already exists. You can use the login form instead.")
        
    else:
        print("\n❌ Failed to create test user")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 