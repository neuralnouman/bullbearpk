#!/usr/bin/env python3
"""
Portfolio Manager for BullBearPK
===============================

Comprehensive portfolio management system that tracks:
1. Individual investment transactions
2. Portfolio performance over time
3. Risk metrics and diversification
4. Investment goals and progress
5. Complete investment history
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
from database_config import db_config

logger = logging.getLogger(__name__)

class PortfolioManager:
    """Comprehensive portfolio management system"""
    
    def __init__(self):
        self.db = db_config
    
    def create_user_portfolio(self, user_id: str, initial_cash: float = 0.0) -> bool:
        """Create initial portfolio for new user"""
        try:
            # Create initial portfolio snapshot
            portfolio_data = {
                'user_id': user_id,
                'portfolio_date': date.today(),
                'total_value': 0.00,
                'total_invested': 0.00,
                'cash_balance': initial_cash,
                'available_cash': initial_cash,
                'total_stocks_held': 0,
                'active_investments': 0,
                'snapshot_type': 'manual',
                'notes': 'Initial portfolio creation'
            }
            
            query = """
                INSERT INTO portfolios (
                    user_id, portfolio_date, total_value, total_invested,
                    cash_balance, available_cash, total_stocks_held,
                    active_investments, snapshot_type, notes
                ) VALUES (
                    %(user_id)s, %(portfolio_date)s, %(total_value)s, %(total_invested)s,
                    %(cash_balance)s, %(available_cash)s, %(total_stocks_held)s,
                    %(active_investments)s, %(snapshot_type)s, %(notes)s
                )
            """
            
            self.db.execute_query(query, portfolio_data)
            logger.info(f"Created initial portfolio for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating portfolio for user {user_id}: {e}")
            return False
    
    def record_investment_transaction(
        self,
        user_id: str,
        stock_code: str,
        transaction_type: str,
        quantity: int,
        price: float,
        total_amount: float,
        **kwargs
    ) -> bool:
        """Record a new investment transaction"""
        try:
            logger.info(f"Recording investment transaction for user {user_id}, stock {stock_code}")
            # Get stock details with current price
            stock_result = self.db.execute_query(
                "SELECT name, sector, close_price FROM stocks WHERE code = %s ORDER BY scraped_at DESC LIMIT 1",
                (stock_code,)
            )
            logger.info(f"Stock details found: {stock_result}")
            
            stock_details = stock_result[0] if stock_result else {}
            stock_name = stock_details.get('name', '') if stock_details else ''
            sector = stock_details.get('sector', '') if stock_details else ''
            current_price = stock_details.get('close_price', price) if stock_details else price
            
            if transaction_type == 'sell':
                logger.info(f"Processing sell transaction for {stock_code}")
                # For sell transactions, update existing buy record
                success = self._handle_sell_transaction(user_id, stock_code, quantity, price, total_amount, **kwargs)
                logger.info(f"Sell transaction result: {success}")
                if success:
                    # Update user's cash balance for sell transactions
                    cash_update_query = """
                        UPDATE users SET 
                            cash_balance = cash_balance + %s,
                            updated_at = %s
                        WHERE user_id = %s
                    """
                    self.db.execute_query(cash_update_query, (total_amount, datetime.now(), user_id))
                    logger.info(f"Updated cash balance for user {user_id}: increased by {total_amount}")
                    
                    # Update portfolio snapshot
                    self.update_portfolio_snapshot(user_id)
                    
                    # Synchronize user table with portfolio data
                    self._sync_user_portfolio_data(user_id)
                return success
            
            # For buy transactions, create new record
            investment_data = {
                'user_id': user_id,
                'stock_code': stock_code,
                'stock_name': stock_name,
                'sector': sector,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'buy_price': price,
                'total_invested': total_amount,
                'current_quantity': quantity,
                'current_price': current_price,
                'current_value': quantity * current_price,
                'market_value': quantity * current_price,
                'status': 'active',
                'investment_duration_days': 0,
                'created_by': kwargs.get('created_by', 'user'),
                'source': kwargs.get('source', 'manual'),
                'user_notes': kwargs.get('notes', ''),
                'tags': json.dumps(kwargs.get('tags', []))
            }
            
            # Add analysis data if provided
            # Note: These fields are optional and will be handled separately if needed
            # if 'technical_analysis' in kwargs:
            #     investment_data['technical_analysis_when_bought'] = json.dumps(kwargs['technical_analysis'])
            # if 'news_sentiment' in kwargs:
            #     investment_data['news_sentiment_when_bought'] = json.dumps(kwargs['news_sentiment'])
            # if 'recommendation' in kwargs:
            #     investment_data['recommendation_when_bought'] = kwargs['recommendation']
            # if 'confidence_score' in kwargs:
            #     investment_data['confidence_score_when_bought'] = kwargs['confidence_score']
            
            # Insert investment record with error handling
            logger.info(f"Executing investment insert with data: {investment_data}")
            try:
                query = """
                    INSERT INTO investments (
                        user_id, stock_code, stock_name, sector, transaction_type,
                        quantity, buy_price, total_invested, current_quantity,
                        current_price, current_value, market_value, status,
                        investment_duration_days, created_by, source, user_notes,
                        tags
                    ) VALUES (
                        %(user_id)s, %(stock_code)s, %(stock_name)s, %(sector)s, %(transaction_type)s,
                        %(quantity)s, %(buy_price)s, %(total_invested)s, %(current_quantity)s,
                        %(current_price)s, %(current_value)s, %(market_value)s, %(status)s,
                        %(investment_duration_days)s, %(created_by)s, %(source)s, %(user_notes)s,
                        %(tags)s
                    )
                """
                self.db.execute_query(query, investment_data)
                logger.info(f"Recorded {transaction_type} transaction for user {user_id}, stock {stock_code}")
            except Exception as e:
                logger.error(f"Error inserting investment record: {e}")
                # Try with minimal required fields
                minimal_query = """
                    INSERT INTO investments (
                        user_id, stock_code, stock_name, sector, transaction_type,
                        quantity, buy_price, total_invested, current_quantity,
                        current_price, current_value, market_value, status
                    ) VALUES (
                        %(user_id)s, %(stock_code)s, %(stock_name)s, %(sector)s, %(transaction_type)s,
                        %(quantity)s, %(buy_price)s, %(total_invested)s, %(current_quantity)s,
                        %(current_price)s, %(current_value)s, %(market_value)s, %(status)s
                    )
                """
                minimal_data = {
                    'user_id': investment_data['user_id'],
                    'stock_code': investment_data['stock_code'],
                    'stock_name': investment_data['stock_name'],
                    'sector': investment_data['sector'],
                    'transaction_type': investment_data['transaction_type'],
                    'quantity': investment_data['quantity'],
                    'buy_price': investment_data['buy_price'],
                    'total_invested': investment_data['total_invested'],
                    'current_quantity': investment_data['current_quantity'],
                    'current_price': investment_data['current_price'],
                    'current_value': investment_data['current_value'],
                    'market_value': investment_data['market_value'],
                    'status': investment_data['status']
                }
                self.db.execute_query(minimal_query, minimal_data)
                logger.info(f"Recorded {transaction_type} transaction with minimal fields for user {user_id}, stock {stock_code}")
            
            # Update user's cash balance with safety checks
            if transaction_type == 'buy':
                # Check if user has sufficient cash before buying
                current_cash_query = "SELECT cash_balance FROM users WHERE user_id = %s"
                current_cash_result = self.db.execute_query(current_cash_query, (user_id,))
                current_cash = float(current_cash_result[0]['cash_balance']) if current_cash_result else 0
                
                if current_cash < total_amount:
                    logger.error(f"Insufficient cash for user {user_id}. Available: {current_cash}, Required: {total_amount}")
                    return False
                
                # Decrease cash balance for buy transactions
                cash_update_query = """
                    UPDATE users SET 
                        cash_balance = GREATEST(0, cash_balance - %s),
                        updated_at = %s
                    WHERE user_id = %s
                """
                self.db.execute_query(cash_update_query, (total_amount, datetime.now(), user_id))
                logger.info(f"Updated cash balance for user {user_id}: decreased by {total_amount}")

            
            # Update portfolio snapshot
            self.update_portfolio_snapshot(user_id)
            
            # Synchronize user table with portfolio data
            self._sync_user_portfolio_data(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording investment transaction: {e}", exc_info=True)
            return False
    
    def _sync_user_portfolio_data(self, user_id: str) -> bool:
        """Synchronize user table with current portfolio data"""
        try:
            # Get current portfolio data
            investments = self.db.execute_query(
                """
                SELECT SUM(current_value) as total_value, SUM(total_invested) as total_invested
                FROM investments 
                WHERE user_id = %s AND status = 'active'
                """,
                (user_id,)
            )
            
            # Get user's current cash balance
            user_result = self.db.execute_query(
                "SELECT cash_balance FROM users WHERE user_id = %s",
                (user_id,)
            )
            
            if not user_result:
                logger.error(f"User {user_id} not found")
                return False
            
            # Calculate portfolio values
            total_value = float(investments[0]['total_value']) if investments and investments[0]['total_value'] else 0
            total_invested = float(investments[0]['total_invested']) if investments and investments[0]['total_invested'] else 0
            cash_balance = float(user_result[0]['cash_balance'])
            
            # Total portfolio value includes cash balance
            total_portfolio_value = total_value + cash_balance
            
            # Update user table with current portfolio data
            update_query = """
                UPDATE users SET 
                    portfolio_value = %s,
                    updated_at = NOW()
                WHERE user_id = %s
            """
            
            self.db.execute_query(update_query, (total_portfolio_value, user_id))
            logger.info(f"Synchronized user {user_id} portfolio data: total_value={total_portfolio_value}, cash_balance={cash_balance}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error synchronizing user portfolio data: {e}")
            return False
    
    def _handle_sell_transaction(self, user_id: str, stock_code: str, quantity: int, price: float, total_amount: float, **kwargs) -> bool:
        """Handle sell transaction by updating existing buy record"""
        try:
            logger.info(f"Starting sell transaction for user {user_id}, stock {stock_code}, quantity {quantity}, price {price}")
            
            # Find existing investment for this stock with remaining shares
            existing_investment = self.db.execute_query(
                "SELECT * FROM investments WHERE user_id = %s AND stock_code = %s AND current_quantity > 0",
                (user_id, stock_code)
            )
            
            if not existing_investment:
                logger.error(f"No investment with remaining shares found for user {user_id}, stock {stock_code}")
                return False
            
            investment = existing_investment[0]
            logger.info(f"Found investment: {investment}")
            
            # Convert Decimal to float for calculations
            current_quantity = float(investment['current_quantity'])
            buy_price = float(investment['buy_price'])
            
            logger.info(f"Current quantity: {current_quantity}, Buy price: {buy_price}")
            
            if quantity > current_quantity:
                logger.error(f"Insufficient shares to sell. Available: {current_quantity}, Requested: {quantity}")
                return False
            
            # Calculate realized P&L
            realized_pnl = (price - buy_price) * quantity
            logger.info(f"Calculated realized P&L: {realized_pnl}")
            
            # Update the investment record
            new_quantity = current_quantity - quantity
            status = 'sold' if new_quantity == 0 else 'partial_sold'
            
            logger.info(f"New quantity: {new_quantity}, Status: {status}")
            
            # Convert existing realized_pnl to float if it exists
            existing_realized_pnl = float(investment.get('realized_pnl', 0))
            total_realized_pnl = existing_realized_pnl + realized_pnl
            
            update_data = {
                'current_quantity': new_quantity,
                'current_value': float(new_quantity * price),
                'market_value': float(new_quantity * price),
                'sell_price': float(price),
                'sell_quantity': quantity,
                'sell_reason': kwargs.get('sell_reason', 'manual'),
                'sell_date': datetime.now(),
                'realized_pnl': total_realized_pnl,
                'status': status,
                'last_updated': datetime.now()
            }
            
            logger.info(f"Update data: {update_data}")
            
            query = """
                UPDATE investments SET
                    current_quantity = %(current_quantity)s,
                    current_value = %(current_value)s,
                    market_value = %(market_value)s,
                    sell_price = %(sell_price)s,
                    sell_quantity = %(sell_quantity)s,
                    sell_reason = %(sell_reason)s,
                    sell_date = %(sell_date)s,
                    realized_pnl = %(realized_pnl)s,
                    status = %(status)s,
                    last_updated = %(last_updated)s
                WHERE user_id = %(user_id)s AND stock_code = %(stock_code)s AND current_quantity > 0
            """
            
            update_data['user_id'] = user_id
            update_data['stock_code'] = stock_code
            
            self.db.execute_query(query, update_data)
            logger.info(f"Updated sell transaction for user {user_id}, stock {stock_code}")
            
            # Update portfolio snapshot
            self.update_portfolio_snapshot(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling sell transaction: {e}")
            return False
    
    def update_investment_status(self, user_id: str, stock_code: str) -> bool:
        """Update current status of an investment"""
        try:
            # Get current stock price
            stock_result = self.db.execute_query(
                "SELECT close_price FROM stocks WHERE code = %s",
                (stock_code,)
            )
            
            if not stock_result:
                return False
            
            stock_data = stock_result[0]
            current_price = stock_data['close_price']
            
            # Get investment details
            investment_result = self.db.execute_query(
                "SELECT * FROM investments WHERE user_id = %s AND stock_code = %s AND status = 'active'",
                (user_id, stock_code)
            )
            
            if not investment_result:
                return False
            
            investment = investment_result[0]
            
            # Calculate updated values
            current_quantity = investment['current_quantity']
            buy_price = investment['buy_price']
            total_invested = investment['total_invested']
            
            current_value = current_quantity * current_price
            market_value = current_value
            unrealized_pnl = current_value - total_invested
            profit_loss_percent = (unrealized_pnl / total_invested * 100) if total_invested > 0 else 0
            
            # Update performance metrics
            highest_price = max(investment['highest_price_reached'] or 0, current_price)
            lowest_price = min(investment['lowest_price_reached'] or float('inf'), current_price)
            max_profit = max(investment['max_profit_reached'] or 0, unrealized_pnl)
            max_loss = min(investment['max_loss_reached'] or 0, unrealized_pnl)
            
            # Calculate investment duration
            buy_date = investment['buy_date']
            duration_days = (datetime.now() - buy_date).days
            
            # Update investment
            update_data = {
                'current_price': current_price,
                'current_value': current_value,
                'market_value': market_value,
                'unrealized_pnl': unrealized_pnl,
                'profit_loss_percent': profit_loss_percent,
                'highest_price_reached': highest_price,
                'lowest_price_reached': lowest_price,
                'max_profit_reached': max_profit,
                'max_loss_reached': max_loss,
                'investment_duration_days': duration_days,
                'last_updated': datetime.now()
            }
            
            query = """
                UPDATE investments SET
                    current_price = %(current_price)s,
                    current_value = %(current_value)s,
                    market_value = %(market_value)s,
                    unrealized_pnl = %(unrealized_pnl)s,
                    profit_loss_percent = %(profit_loss_percent)s,
                    highest_price_reached = %(highest_price_reached)s,
                    lowest_price_reached = %(lowest_price_reached)s,
                    max_profit_reached = %(max_profit_reached)s,
                    max_loss_reached = %(max_loss_reached)s,
                    investment_duration_days = %(investment_duration_days)s,
                    last_updated = %(last_updated)s
                WHERE user_id = %(user_id)s AND stock_code = %(stock_code)s AND status = 'active'
            """
            
            update_data['user_id'] = user_id
            update_data['stock_code'] = stock_code
            
            self.db.execute_query(query, update_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating investment status: {e}")
            return False
    
    def update_portfolio_snapshot(self, user_id: str) -> bool:
        """Create/update portfolio snapshot for user"""
        try:
            # Get all investments with remaining shares for user
            investments = self.db.execute_query(
                """
                SELECT * FROM investments 
                WHERE user_id = %s AND current_quantity > 0
                """,
                (user_id,)
            )
            
            # Calculate portfolio metrics
            total_invested = float(sum(inv['total_invested'] for inv in investments))
            total_value = float(sum(inv['current_value'] for inv in investments))
            total_pnl = total_value - total_invested
            pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            # Calculate sector allocation
            sector_allocation = {}
            for inv in investments:
                sector = inv['sector'] or 'Unknown'
                if sector not in sector_allocation:
                    sector_allocation[sector] = 0
                sector_allocation[sector] += float(inv['current_value'])
            
            # Convert to percentages
            if total_value > 0:
                sector_allocation = {k: (v / total_value * 100) for k, v in sector_allocation.items()}
            
            # Get top holdings
            top_holdings = sorted(investments, key=lambda x: x['current_value'], reverse=True)[:5]
            top_holdings_data = {}
            for inv in top_holdings:
                percentage = (float(inv['current_value']) / total_value * 100) if total_value > 0 else 0
                top_holdings_data[inv['stock_code']] = {
                    'name': inv['stock_name'],
                    'value': float(inv['current_value']),
                    'percentage': percentage
                }
            
            # Get user preferences
            user_result = self.db.execute_query(
                "SELECT risk_tolerance, investment_goal, preferred_sectors FROM users WHERE user_id = %s",
                (user_id,)
            )
            
            user_data = user_result[0] if user_result else {}
            
            # Prepare portfolio data
            portfolio_data = {
                'user_id': user_id,
                'portfolio_date': date.today(),
                'total_value': float(total_value),
                'total_invested': float(total_invested),
                'total_profit_loss': float(total_pnl),
                'profit_loss_percent': float(pnl_percent),
                'total_stocks_held': len(investments),
                'active_investments': len(investments),
                'sector_allocation': json.dumps(sector_allocation),
                'top_holdings': json.dumps(top_holdings_data),
                'risk_tolerance_snapshot': user_data.get('risk_tolerance', 'moderate') if user_data else 'moderate',
                'investment_goal_snapshot': user_data.get('investment_goal', '') if user_data else '',
                'preferred_sectors_snapshot': user_data.get('preferred_sectors', '[]') if user_data else '[]',
                'snapshot_type': 'transaction',
                'notes': f'Portfolio snapshot - {len(investments)} active investments'
            }
            
            # Check if portfolio snapshot exists for today
            existing_result = self.db.execute_query(
                "SELECT id FROM portfolios WHERE user_id = %s AND portfolio_date = %s",
                (user_id, date.today())
            )
            
            existing = existing_result[0] if existing_result else None
            
            if existing:
                # Update existing snapshot
                query = """
                    UPDATE portfolios SET
                        total_value = %(total_value)s,
                        total_invested = %(total_invested)s,
                        total_profit_loss = %(total_profit_loss)s,
                        profit_loss_percent = %(profit_loss_percent)s,
                        total_stocks_held = %(total_stocks_held)s,
                        active_investments = %(active_investments)s,
                        sector_allocation = %(sector_allocation)s,
                        top_holdings = %(top_holdings)s,
                        last_updated = NOW()
                    WHERE user_id = %(user_id)s AND portfolio_date = %(portfolio_date)s
                """
            else:
                # Create new snapshot
                query = """
                    INSERT INTO portfolios (
                        user_id, portfolio_date, total_value, total_invested,
                        total_profit_loss, profit_loss_percent, total_stocks_held,
                        active_investments, sector_allocation, top_holdings,
                        risk_tolerance_snapshot, investment_goal_snapshot,
                        preferred_sectors_snapshot, snapshot_type, notes
                    ) VALUES (
                        %(user_id)s, %(portfolio_date)s, %(total_value)s, %(total_invested)s,
                        %(total_profit_loss)s, %(profit_loss_percent)s, %(total_stocks_held)s,
                        %(active_investments)s, %(sector_allocation)s, %(top_holdings)s,
                        %(risk_tolerance_snapshot)s, %(investment_goal_snapshot)s,
                        %(preferred_sectors_snapshot)s, %(snapshot_type)s, %(notes)s
                    )
                """
            
            self.db.execute_query(query, portfolio_data)
            logger.info(f"Updated portfolio snapshot for user {user_id}")
            
            # Synchronize user table with portfolio data
            self._sync_user_portfolio_data(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating portfolio snapshot: {e}")
            return False
    
    def get_user_investment_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get complete investment history for user"""
        try:
            query = """
                SELECT * FROM investments 
                WHERE user_id = %s 
                ORDER BY buy_date DESC 
                LIMIT %s
            """
            
            investments = self.db.execute_query(query, (user_id, limit))
            return investments
            
        except Exception as e:
            logger.error(f"Error getting investment history: {e}")
            return []
    
    def get_portfolio_performance(self, user_id: str, days: int = 30) -> Dict:
        """Get portfolio performance over specified days"""
        try:
            start_date = date.today() - timedelta(days=days)
            
            query = """
                SELECT * FROM portfolios 
                WHERE user_id = %s AND portfolio_date >= %s
                ORDER BY portfolio_date ASC
            """
            
            snapshots = self.db.execute_query(query, (user_id, start_date))
            
            if not snapshots:
                return {}
            
            # Calculate performance metrics
            initial_value = snapshots[0]['total_value']
            final_value = snapshots[-1]['total_value']
            total_return = final_value - initial_value
            return_percent = (total_return / initial_value * 100) if initial_value > 0 else 0
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(snapshots)):
                prev_value = snapshots[i-1]['total_value']
                curr_value = snapshots[i]['total_value']
                daily_return = (curr_value - prev_value) / prev_value * 100 if prev_value > 0 else 0
                daily_returns.append(daily_return)
            
            # Calculate volatility
            volatility = 0
            if daily_returns:
                avg_return = sum(daily_returns) / len(daily_returns)
                variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
                volatility = variance ** 0.5
            
            return {
                'period_days': days,
                'initial_value': initial_value,
                'final_value': final_value,
                'total_return': total_return,
                'return_percent': return_percent,
                'volatility': volatility,
                'snapshots': snapshots,
                'daily_returns': daily_returns
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio performance: {e}")
            return {}
    
    def get_investment_analytics(self, user_id: str) -> Dict:
        """Get comprehensive investment analytics"""
        try:
            # Get all investments
            investments = self.db.execute_query(
                "SELECT * FROM investments WHERE user_id = %s",
                (user_id,)
            )
            
            if not investments:
                return {}
            
            # Calculate analytics
            total_investments = len(investments)
            active_investments = len([inv for inv in investments if inv['status'] == 'active'])
            sold_investments = len([inv for inv in investments if inv['status'] == 'sold'])
            
            # Performance metrics
            total_invested = sum(inv['total_invested'] for inv in investments)
            total_realized_pnl = sum(inv.get('realized_pnl', 0) for inv in investments)
            total_unrealized_pnl = sum(inv.get('unrealized_pnl', 0) for inv in investments)
            total_dividends = sum(inv.get('total_dividends_received', 0) for inv in investments)
            
            # Best and worst investments
            if investments:
                best_investment = max(investments, key=lambda x: x.get('profit_loss', 0))
                worst_investment = min(investments, key=lambda x: x.get('profit_loss', 0))
            else:
                best_investment = worst_investment = None
            
            # Sector analysis
            sector_analysis = {}
            for inv in investments:
                sector = inv['sector'] or 'Unknown'
                if sector not in sector_analysis:
                    sector_analysis[sector] = {
                        'count': 0,
                        'total_invested': 0,
                        'total_pnl': 0
                    }
                sector_analysis[sector]['count'] += 1
                sector_analysis[sector]['total_invested'] += inv['total_invested']
                sector_analysis[sector]['total_pnl'] += inv.get('profit_loss', 0)
            
            return {
                'total_investments': total_investments,
                'active_investments': active_investments,
                'sold_investments': sold_investments,
                'total_invested': total_invested,
                'total_realized_pnl': total_realized_pnl,
                'total_unrealized_pnl': total_unrealized_pnl,
                'total_dividends': total_dividends,
                'best_investment': best_investment,
                'worst_investment': worst_investment,
                'sector_analysis': sector_analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting investment analytics: {e}")
            return {}

# Global instance
portfolio_manager = PortfolioManager() 