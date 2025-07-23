from agents.stock_agent import EnhancedDatabaseManager

def update_portfolio_current_prices(user_id: str) -> bool:
    """
    Update the current prices of stocks in a user's portfolio
    based on the latest stock data in the database.
    
    Args:
        user_id: The ID of the user whose portfolio should be updated
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db_manager = EnhancedDatabaseManager()
        
        # Get user investments
        investments = []
        with db_manager.get_connection() as conn:
            results = conn.execute('''
                SELECT * FROM investments WHERE user_id = ?
            ''', (user_id,)).fetchall()
            
            if not results:
                return True  # No investments to update
            
            for row in results:
                investments.append({
                    'id': row['id'],
                    'stock_symbol': row['stock_symbol']
                })
        
        # Update each investment with the latest price
        with db_manager.get_connection() as conn:
            for investment in investments:
                # Get the latest price for this stock
                latest_price_result = conn.execute('''
                    SELECT close_price FROM stock_data 
                    WHERE code = ? 
                    ORDER BY timestamp DESC LIMIT 1
                ''', (investment['stock_symbol'],)).fetchone()
                
                if latest_price_result:
                    latest_price = latest_price_result['close_price']
                    
                    # Update the investment with the latest price
                    conn.execute('''
                        UPDATE investments 
                        SET current_price = ? 
                        WHERE id = ?
                    ''', (latest_price, investment['id']))
            
            conn.commit()
        
        return True
    
    except Exception as e:
        print(f"Error updating portfolio prices: {str(e)}")
        return False