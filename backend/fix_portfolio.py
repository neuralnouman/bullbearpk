#!/usr/bin/env python3
"""
Fix portfolio data issues by initializing sample data
"""

from init_portfolio_data import init_portfolio_data
from api.portfolio_update import update_portfolio_current_prices
from agents.stock_agent import EnhancedDatabaseManager

def fix_portfolio():
    """Fix portfolio data issues"""
    print("Fixing portfolio data...")
    
    # 1. Initialize sample portfolio data
    success = init_portfolio_data("demo_user")
    if not success:
        print("Failed to initialize portfolio data")
        return False
    
    # 2. Update current prices
    success = update_portfolio_current_prices("demo_user")
    if not success:
        print("Failed to update portfolio prices")
        return False
    
    # 3. Verify portfolio data
    db_manager = EnhancedDatabaseManager()
    with db_manager.get_connection() as conn:
        # Check user
        user = conn.execute("SELECT * FROM users WHERE user_id = ?", ("demo_user",)).fetchone()
        if not user:
            print("User not found")
            return False
        
        # Check investments
        investments = conn.execute("SELECT * FROM investments WHERE user_id = ?", ("demo_user",)).fetchall()
        if not investments:
            print("No investments found")
            return False
        
        print(f"User cash balance: {user['cash_balance']}")
        print(f"Number of investments: {len(investments)}")
        
        # Print investment details
        for inv in investments:
            print(f"Investment: {inv['stock_symbol']} - {inv['quantity']} shares at {inv['purchase_price']} (current: {inv['current_price']})")
    
    print("Portfolio data fixed successfully!")
    return True

if __name__ == "__main__":
    fix_portfolio()