#!/usr/bin/env python3
"""
Initialize portfolio data with sample investments
"""

from agents.stock_agent import EnhancedDatabaseManager, StockData
from datetime import datetime, timedelta
import random

def init_portfolio_data(user_id="demo_user"):
    """Initialize portfolio data with sample investments"""
    db_manager = EnhancedDatabaseManager()
    
    # 1. Make sure user exists
    user_profile = db_manager.get_user_profile(user_id)
    if not user_profile:
        # Create user if not exists
        with db_manager.get_connection() as conn:
            conn.execute('''
                INSERT INTO users (
                    user_id, name, email, risk_tolerance, investment_goal,
                    portfolio_value, cash_balance, preferred_sectors, blacklisted_stocks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, 'Demo User', f'{user_id}@example.com', 'medium', 'growth',
                10000.0, 5000.0, '[]', '[]'
            ))
            conn.commit()
        print(f"Created user {user_id}")
    
    # 2. Get some stock data to use for investments
    with db_manager.get_connection() as conn:
        stocks = conn.execute('''
            SELECT DISTINCT code, name, sector, close_price 
            FROM stock_data 
            ORDER BY timestamp DESC
            LIMIT 50
        ''').fetchall()
    
    if not stocks:
        print("No stock data found. Please run the scraper first.")
        return False
    
    # 3. Clear existing investments for this user
    with db_manager.get_connection() as conn:
        conn.execute('DELETE FROM investments WHERE user_id = ?', (user_id,))
        conn.commit()
    
    # 4. Create sample investments
    sample_stocks = random.sample(stocks, min(5, len(stocks)))
    total_invested = 0
    
    with db_manager.get_connection() as conn:
        for i, stock in enumerate(sample_stocks):
            # Create investment with realistic data
            quantity = random.randint(10, 100)
            purchase_price = float(stock['close_price']) * random.uniform(0.9, 1.1)  # Vary price slightly
            current_price = float(stock['close_price'])
            purchase_date = (datetime.now() - timedelta(days=random.randint(10, 90))).isoformat()
            investment_amount = quantity * purchase_price
            total_invested += investment_amount
            
            conn.execute('''
                INSERT INTO investments (
                    user_id, stock_symbol, company_name, quantity, purchase_price,
                    current_price, purchase_date, sector, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, stock['code'], stock['name'], quantity, purchase_price,
                current_price, purchase_date, stock['sector'], 'active'
            ))
        
        # Update user's cash balance
        initial_balance = 10000.0
        remaining_balance = initial_balance - total_invested
        if remaining_balance < 0:
            remaining_balance = 1000.0  # Ensure some cash balance
            
        conn.execute('''
            UPDATE users SET cash_balance = ? WHERE user_id = ?
        ''', (remaining_balance, user_id))
        
        conn.commit()
    
    print(f"Created {len(sample_stocks)} sample investments for user {user_id}")
    print(f"Total invested: {total_invested:.2f}, Remaining balance: {remaining_balance:.2f}")
    return True

if __name__ == "__main__":
    init_portfolio_data()
    print("Portfolio data initialized successfully!")