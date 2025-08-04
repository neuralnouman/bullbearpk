#!/usr/bin/env python3
"""
Portfolio Update Utilities for BullBearPK
========================================

Utility functions for updating portfolio data:
1. Update current prices of stocks in portfolio
2. Calculate portfolio performance
3. Update portfolio snapshots
"""

from database_config import db_config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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
        logger.info(f"Updating portfolio prices for user: {user_id}")
        
        # Get user investments
        investments_query = """
            SELECT id, stock_code, current_quantity 
            FROM investments 
            WHERE user_id = %s AND status = 'active'
        """
        investments = db_config.execute_query(investments_query, (user_id,))
        
        if not investments:
            logger.info(f"No active investments found for user {user_id}")
            return True
        
        updated_count = 0
        
        # Update each investment with the latest price
        for investment in investments:
            investment_id = investment['id']
            stock_code = investment['stock_code']
            current_quantity = investment['current_quantity']
            
            # Get the latest price for this stock
            latest_price_query = """
                SELECT close_price FROM stocks 
                WHERE code = %s 
                ORDER BY scraped_at DESC LIMIT 1
            """
            latest_price_result = db_config.execute_query(latest_price_query, (stock_code,))
            
            if latest_price_result:
                latest_price = latest_price_result[0]['close_price']
                current_value = latest_price * current_quantity
                
                # Update the investment with the latest price
                update_query = """
                    UPDATE investments 
                    SET current_price = %s, current_value = %s, market_value = %s, last_updated = %s
                    WHERE id = %s
                """
                
                db_config.execute_query(update_query, (
                    latest_price, current_value, current_value, datetime.now(), investment_id
                ))
                
                updated_count += 1
                logger.debug(f"Updated {stock_code} price to {latest_price}")
            else:
                logger.warning(f"No price data found for stock {stock_code}")
        
        logger.info(f"Updated prices for {updated_count} investments")
        return True
    
    except Exception as e:
        logger.error(f"Error updating portfolio prices: {str(e)}", exc_info=True)
        return False

def calculate_portfolio_performance(user_id: str) -> dict:
    """
    Calculate comprehensive portfolio performance metrics
    
    Args:
        user_id: The ID of the user
        
    Returns:
        dict: Portfolio performance metrics
    """
    try:
        logger.info(f"Calculating portfolio performance for user: {user_id}")
        
        # Get all investments
        investments_query = """
            SELECT * FROM investments 
            WHERE user_id = %s
            ORDER BY buy_date DESC
        """
        investments = db_config.execute_query(investments_query, (user_id,))
        
        if not investments:
            return {
                'total_invested': 0.0,
                'total_value': 0.0,
                'total_pnl': 0.0,
                'pnl_percent': 0.0,
                'active_investments': 0,
                'sold_investments': 0,
                'realized_pnl': 0.0,
                'unrealized_pnl': 0.0
            }
        
        # Calculate metrics
        total_invested = sum(inv.get('total_invested', 0) for inv in investments)
        total_value = sum(inv.get('current_value', 0) for inv in investments if inv.get('status') == 'active')
        realized_pnl = sum(inv.get('realized_pnl', 0) for inv in investments)
        unrealized_pnl = total_value - sum(inv.get('total_invested', 0) for inv in investments if inv.get('status') == 'active')
        
        total_pnl = realized_pnl + unrealized_pnl
        pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        active_investments = len([inv for inv in investments if inv.get('status') == 'active'])
        sold_investments = len([inv for inv in investments if inv.get('status') == 'sold'])
        
        return {
            'total_invested': total_invested,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'pnl_percent': round(pnl_percent, 2),
            'active_investments': active_investments,
            'sold_investments': sold_investments,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'last_updated': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error calculating portfolio performance: {str(e)}", exc_info=True)
        return {}

def update_portfolio_snapshot(user_id: str) -> bool:
    """
    Create a new portfolio snapshot with current performance data
    
    Args:
        user_id: The ID of the user
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Creating portfolio snapshot for user: {user_id}")
        
        # Calculate current performance
        performance = calculate_portfolio_performance(user_id)
        
        if not performance:
            logger.error(f"Failed to calculate performance for user {user_id}")
            return False
        
        # Create snapshot
        snapshot_query = """
            INSERT INTO portfolios (
                user_id, portfolio_date, total_value, total_invested,
                cash_balance, available_cash, total_stocks_held,
                active_investments, total_realized_pnl, total_unrealized_pnl,
                portfolio_return_percent, snapshot_type, notes, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        snapshot_params = (
            user_id,
            datetime.now().date(),
            performance.get('total_value', 0),
            performance.get('total_invested', 0),
            10000.0,  # Default cash balance
            10000.0 - performance.get('total_invested', 0),  # Available cash
            performance.get('active_investments', 0) + performance.get('sold_investments', 0),
            performance.get('active_investments', 0),
            performance.get('realized_pnl', 0),
            performance.get('unrealized_pnl', 0),
            performance.get('pnl_percent', 0),
            'manual',
            f"Portfolio snapshot created at {datetime.now()}",
            datetime.now()
        )
        
        db_config.execute_query(snapshot_query, snapshot_params)
        
        logger.info(f"Successfully created portfolio snapshot for user {user_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating portfolio snapshot: {str(e)}", exc_info=True)
        return False