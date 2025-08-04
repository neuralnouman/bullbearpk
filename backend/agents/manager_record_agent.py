#!/usr/bin/env python3
"""
Manager Record Agent for BullBearPK
===================================

Core agent that handles user investment decisions after recommendations:
1. Buy new stocks from recommendations
2. Hold existing stocks
3. Sell old stocks
4. Update investment records
5. Update portfolio snapshots
6. Track transaction history
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
import json
from database_config import db_config

logger = logging.getLogger(__name__)

class ManagerRecordAgent:
    """Core agent for handling user investment decisions and record management"""
    
    def __init__(self):
        self.db = db_config
        self.transaction_types = {
            'buy': 'purchase',
            'sell': 'sale',
            'hold': 'hold',
            'pending': 'pending'
        }
    
    async def handle_user_decision(
        self,
        user_id: str,
        decision_type: str,
        stock_code: str = None,
        quantity: int = None,
        price: float = None,
        recommendation_id: str = None,
        **kwargs
    ) -> Dict:
        """
        Main method to handle user investment decisions
        
        Args:
            user_id: User making the decision
            decision_type: 'buy', 'sell', 'hold', 'pending'
            stock_code: Stock code for the transaction
            quantity: Number of shares
            price: Price per share
            recommendation_id: ID of the recommendation being acted upon
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with transaction result and updated portfolio info
        """
        try:
            logger.info(f"Processing {decision_type} decision for user {user_id}")
            
            if decision_type == 'buy':
                return await self._handle_buy_decision(
                    user_id, stock_code, quantity, price, recommendation_id, **kwargs
                )
            elif decision_type == 'sell':
                return await self._handle_sell_decision(
                    user_id, stock_code, quantity, price, **kwargs
                )
            elif decision_type == 'hold':
                return await self._handle_hold_decision(
                    user_id, stock_code, **kwargs
                )
            elif decision_type == 'pending':
                return await self._handle_pending_decision(
                    user_id, stock_code, recommendation_id, **kwargs
                )
            else:
                return {
                    "status": "error",
                    "message": f"Invalid decision type: {decision_type}",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
                
        except Exception as e:
            logger.error(f"Error handling user decision: {e}")
            return {
                "status": "error",
                "message": f"Error processing decision: {str(e)}",
                "transaction_id": None,
                "portfolio_updated": False
            }
    
    async def _handle_buy_decision(
        self,
        user_id: str,
        stock_code: str,
        quantity: int,
        price: float,
        recommendation_id: str = None,
        **kwargs
    ) -> Dict:
        """Handle buying new stocks from recommendations"""
        try:
            # Validate inputs
            if not all([stock_code, quantity, price]):
                return {
                    "status": "error",
                    "message": "Missing required parameters for buy decision",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Get stock details
            stock_details = self._get_stock_details(stock_code)
            if not stock_details:
                return {
                    "status": "error",
                    "message": f"Stock {stock_code} not found in database",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Calculate transaction details
            total_amount = quantity * price
            transaction_id = f"TXN_{user_id}_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Check if user has existing investment in this stock
            existing_investment = self._get_existing_investment(user_id, stock_code)
            
            if existing_investment:
                # Update existing investment
                new_quantity = existing_investment['current_quantity'] + quantity
                new_total_invested = existing_investment['total_invested'] + total_amount
                new_avg_price = new_total_invested / new_quantity
                
                # Update investment record
                update_success = self._update_existing_investment(
                    user_id, stock_code, new_quantity, new_avg_price, 
                    new_total_invested, transaction_id
                )
                
                if not update_success:
                    return {
                        "status": "error",
                        "message": "Failed to update existing investment",
                        "transaction_id": None,
                        "portfolio_updated": False
                    }
                
                logger.info(f"Updated existing investment for {stock_code}")
                
            else:
                # Create new investment record
                insert_success = self._create_new_investment(
                    user_id, stock_code, stock_details, quantity, price,
                    total_amount, transaction_id, recommendation_id
                )
                
                if not insert_success:
                    return {
                        "status": "error",
                        "message": "Failed to create new investment record",
                        "transaction_id": None,
                        "portfolio_updated": False
                    }
                
                logger.info(f"Created new investment for {stock_code}")
            
            # Update portfolio snapshot
            portfolio_updated = self._update_portfolio_snapshot(user_id)
            
            # Get updated portfolio info
            portfolio_info = self._get_portfolio_summary(user_id)
            
            return {
                "status": "success",
                "message": f"Successfully purchased {quantity} shares of {stock_code} at ${price:.2f}",
                "transaction_id": transaction_id,
                "transaction_type": "buy",
                "stock_code": stock_code,
                "stock_name": stock_details.get('name', ''),
                "quantity": quantity,
                "price": price,
                "total_amount": total_amount,
                "recommendation_id": recommendation_id,
                "portfolio_updated": portfolio_updated,
                "portfolio_summary": portfolio_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling buy decision: {e}")
            return {
                "status": "error",
                "message": f"Error processing buy decision: {str(e)}",
                "transaction_id": None,
                "portfolio_updated": False
            }
    
    async def _handle_sell_decision(
        self,
        user_id: str,
        stock_code: str,
        quantity: int,
        price: float,
        **kwargs
    ) -> Dict:
        """Handle selling existing stocks"""
        try:
            # Validate inputs
            if not all([stock_code, quantity, price]):
                return {
                    "status": "error",
                    "message": "Missing required parameters for sell decision",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Get existing investment
            existing_investment = self._get_existing_investment(user_id, stock_code)
            if not existing_investment:
                return {
                    "status": "error",
                    "message": f"No existing investment found for {stock_code}",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Check if user has enough shares to sell
            if existing_investment['current_quantity'] < quantity:
                return {
                    "status": "error",
                    "message": f"Insufficient shares. You have {existing_investment['current_quantity']} shares, trying to sell {quantity}",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Calculate transaction details
            total_amount = quantity * price
            transaction_id = f"TXN_{user_id}_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calculate profit/loss
            avg_buy_price = existing_investment['total_invested'] / existing_investment['current_quantity']
            profit_loss = (price - avg_buy_price) * quantity
            profit_loss_percent = ((price - avg_buy_price) / avg_buy_price) * 100
            
            # Update investment record
            new_quantity = existing_investment['current_quantity'] - quantity
            new_total_invested = existing_investment['total_invested'] - (avg_buy_price * quantity)
            
            if new_quantity == 0:
                # Completely sold out
                update_success = self._mark_investment_sold(
                    user_id, stock_code, transaction_id, total_amount, profit_loss
                )
            else:
                # Partial sale
                update_success = self._update_existing_investment(
                    user_id, stock_code, new_quantity, avg_buy_price, 
                    new_total_invested, transaction_id
                )
            
            if not update_success:
                return {
                    "status": "error",
                    "message": "Failed to update investment record",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Update portfolio snapshot
            portfolio_updated = self._update_portfolio_snapshot(user_id)
            
            # Get updated portfolio info
            portfolio_info = self._get_portfolio_summary(user_id)
            
            return {
                "status": "success",
                "message": f"Successfully sold {quantity} shares of {stock_code} at ${price:.2f}",
                "transaction_id": transaction_id,
                "transaction_type": "sell",
                "stock_code": stock_code,
                "quantity": quantity,
                "price": price,
                "total_amount": total_amount,
                "profit_loss": profit_loss,
                "profit_loss_percent": profit_loss_percent,
                "portfolio_updated": portfolio_updated,
                "portfolio_summary": portfolio_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling sell decision: {e}")
            return {
                "status": "error",
                "message": f"Error processing sell decision: {str(e)}",
                "transaction_id": None,
                "portfolio_updated": False
            }
    
    async def _handle_hold_decision(
        self,
        user_id: str,
        stock_code: str,
        **kwargs
    ) -> Dict:
        """Handle holding existing stocks"""
        try:
            # Get existing investment
            existing_investment = self._get_existing_investment(user_id, stock_code)
            if not existing_investment:
                return {
                    "status": "error",
                    "message": f"No existing investment found for {stock_code}",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Update investment status to 'hold'
            update_success = self._update_investment_status(user_id, stock_code, 'hold')
            
            if not update_success:
                return {
                    "status": "error",
                    "message": "Failed to update investment status",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Update portfolio snapshot
            portfolio_updated = self._update_portfolio_snapshot(user_id)
            
            # Get updated portfolio info
            portfolio_info = self._get_portfolio_summary(user_id)
            
            return {
                "status": "success",
                "message": f"Successfully marked {stock_code} as hold",
                "transaction_id": None,
                "transaction_type": "hold",
                "stock_code": stock_code,
                "portfolio_updated": portfolio_updated,
                "portfolio_summary": portfolio_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling hold decision: {e}")
            return {
                "status": "error",
                "message": f"Error processing hold decision: {str(e)}",
                "transaction_id": None,
                "portfolio_updated": False
            }
    
    async def _handle_pending_decision(
        self,
        user_id: str,
        stock_code: str,
        recommendation_id: str = None,
        **kwargs
    ) -> Dict:
        """Handle pending decisions (user wants to think about it)"""
        try:
            # Create a pending investment record
            transaction_id = f"PENDING_{user_id}_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get stock details
            stock_details = self._get_stock_details(stock_code)
            if not stock_details:
                return {
                    "status": "error",
                    "message": f"Stock {stock_code} not found in database",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            # Create pending investment record
            insert_success = self._create_pending_investment(
                user_id, stock_code, stock_details, transaction_id, recommendation_id
            )
            
            if not insert_success:
                return {
                    "status": "error",
                    "message": "Failed to create pending investment record",
                    "transaction_id": None,
                    "portfolio_updated": False
                }
            
            return {
                "status": "success",
                "message": f"Successfully marked {stock_code} as pending decision",
                "transaction_id": transaction_id,
                "transaction_type": "pending",
                "stock_code": stock_code,
                "recommendation_id": recommendation_id,
                "portfolio_updated": False,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling pending decision: {e}")
            return {
                "status": "error",
                "message": f"Error processing pending decision: {str(e)}",
                "transaction_id": None,
                "portfolio_updated": False
            }
    
    def _get_stock_details(self, stock_code: str) -> Optional[Dict]:
        """Get stock details from database"""
        try:
            query = "SELECT code, name, sector, close_price FROM stocks WHERE code = %s"
            result = self.db.execute_query(query, (stock_code,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting stock details: {e}")
            return None
    
    def _get_existing_investment(self, user_id: str, stock_code: str) -> Optional[Dict]:
        """Get existing investment for user and stock"""
        try:
            query = """
                SELECT * FROM investments 
                WHERE user_id = %s AND stock_code = %s AND status = 'active'
                ORDER BY buy_date DESC LIMIT 1
            """
            result = self.db.execute_query(query, (user_id, stock_code))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting existing investment: {e}")
            return None
    
    def _create_new_investment(
        self,
        user_id: str,
        stock_code: str,
        stock_details: Dict,
        quantity: int,
        price: float,
        total_amount: float,
        transaction_id: str,
        recommendation_id: str = None
    ) -> bool:
        """Create new investment record"""
        try:
            query = """
                INSERT INTO investments (
                    user_id, stock_code, stock_name, sector, transaction_type,
                    quantity, buy_price, total_invested, current_quantity,
                    current_price, current_value, market_value, status,
                    recommendation_when_bought, confidence_score_when_bought
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            params = (
                user_id, stock_code, stock_details.get('name', ''),
                stock_details.get('sector', ''), 'buy', quantity, price,
                total_amount, quantity, price, total_amount, total_amount,
                'active', 'buy', 0.8  # Default confidence score
            )
            
            self.db.execute_query(query, params)
            logger.info(f"Created new investment record for {stock_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating new investment: {e}")
            return False
    
    def _update_existing_investment(
        self,
        user_id: str,
        stock_code: str,
        new_quantity: int,
        new_avg_price: float,
        new_total_invested: float,
        transaction_id: str
    ) -> bool:
        """Update existing investment record"""
        try:
            query = """
                UPDATE investments 
                SET current_quantity = %s, buy_price = %s, total_invested = %s,
                    current_value = %s, market_value = %s, last_updated = %s
                WHERE user_id = %s AND stock_code = %s AND status = 'active'
            """
            
            current_value = new_quantity * new_avg_price
            
            params = (
                new_quantity, new_avg_price, new_total_invested,
                current_value, current_value, datetime.now(),
                user_id, stock_code
            )
            
            self.db.execute_query(query, params)
            logger.info(f"Updated existing investment for {stock_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating existing investment: {e}")
            return False
    
    def _mark_investment_sold(
        self,
        user_id: str,
        stock_code: str,
        transaction_id: str,
        total_amount: float,
        profit_loss: float
    ) -> bool:
        """Mark investment as completely sold"""
        try:
            query = """
                UPDATE investments 
                SET current_quantity = 0, current_value = 0, market_value = 0,
                    status = 'sold', realized_pnl = %s, sell_date = %s, last_updated = %s
                WHERE user_id = %s AND stock_code = %s AND status = 'active'
            """
            
            params = (profit_loss, datetime.now(), datetime.now(), user_id, stock_code)
            self.db.execute_query(query, params)
            
            logger.info(f"Marked investment as sold for {stock_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking investment as sold: {e}")
            return False
    
    def _update_investment_status(
        self,
        user_id: str,
        stock_code: str,
        status: str
    ) -> bool:
        """Update investment status"""
        try:
            query = """
                UPDATE investments 
                SET status = %s, last_updated = %s
                WHERE user_id = %s AND stock_code = %s AND status = 'active'
            """
            
            params = (status, datetime.now(), user_id, stock_code)
            self.db.execute_query(query, params)
            
            logger.info(f"Updated investment status to {status} for {stock_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating investment status: {e}")
            return False
    
    def _create_pending_investment(
        self,
        user_id: str,
        stock_code: str,
        stock_details: Dict,
        transaction_id: str,
        recommendation_id: str = None
    ) -> bool:
        """Create pending investment record"""
        try:
            query = """
                INSERT INTO investments (
                    user_id, stock_code, stock_name, sector, transaction_type,
                    quantity, buy_price, total_invested, current_quantity,
                    current_price, current_value, market_value, status,
                    recommendation_when_bought, confidence_score_when_bought
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            params = (
                user_id, stock_code, stock_details.get('name', ''),
                stock_details.get('sector', ''), 'pending', 0, 0.0,
                0.0, 0, 0.0, 0.0, 0.0, 'pending', 'pending', 0.5
            )
            
            self.db.execute_query(query, params)
            logger.info(f"Created pending investment record for {stock_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating pending investment: {e}")
            return False
    
    def _update_portfolio_snapshot(self, user_id: str) -> bool:
        """Update portfolio snapshot after transaction"""
        try:
            # Get current portfolio data
            portfolio_data = self._calculate_portfolio_data(user_id)
            
            query = """
                INSERT INTO portfolios (
                    user_id, portfolio_date, total_value, total_invested,
                    cash_balance, available_cash, total_stocks_held,
                    active_investments, total_realized_pnl, total_unrealized_pnl,
                    portfolio_return_percent, snapshot_type, notes, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            
            params = (
                user_id, date.today(), portfolio_data['total_value'],
                portfolio_data['total_invested'], portfolio_data['cash_balance'],
                portfolio_data['available_cash'], portfolio_data['total_stocks_held'],
                portfolio_data['active_investments'], portfolio_data['total_realized_pnl'],
                portfolio_data['total_unrealized_pnl'], portfolio_data['portfolio_return_percent'],
                'transaction', f"Portfolio updated after transaction at {datetime.now()}", datetime.now()
            )
            
            self.db.execute_query(query, params)
            logger.info(f"Updated portfolio snapshot for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating portfolio snapshot: {e}")
            return False
    
    def _calculate_portfolio_data(self, user_id: str) -> Dict:
        """Calculate current portfolio data"""
        try:
            # Get active investments
            query = """
                SELECT 
                    SUM(total_invested) as total_invested,
                    SUM(current_value) as total_current_value,
                    SUM(realized_pnl) as total_realized_pnl,
                    COUNT(*) as total_stocks_held,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_investments
                FROM investments 
                WHERE user_id = %s
            """
            
            result = self.db.execute_query(query, (user_id,))
            if not result:
                return {
                    'total_value': 0.0,
                    'total_invested': 0.0,
                    'cash_balance': 10000.0,  # Default starting cash
                    'available_cash': 10000.0,
                    'total_stocks_held': 0,
                    'active_investments': 0,
                    'total_realized_pnl': 0.0,
                    'total_unrealized_pnl': 0.0,
                    'portfolio_return_percent': 0.0
                }
            
            data = result[0]
            total_invested = float(data['total_invested'] or 0)
            total_current_value = float(data['total_current_value'] or 0)
            total_realized_pnl = float(data['total_realized_pnl'] or 0)
            total_unrealized_pnl = total_current_value - total_invested
            
            # Calculate portfolio return
            portfolio_return_percent = 0.0
            if total_invested > 0:
                portfolio_return_percent = ((total_current_value - total_invested) / total_invested) * 100
            
            return {
                'total_value': total_current_value,
                'total_invested': total_invested,
                'cash_balance': 10000.0,  # Simplified for now
                'available_cash': 10000.0 - total_invested,
                'total_stocks_held': int(data['total_stocks_held'] or 0),
                'active_investments': int(data['active_investments'] or 0),
                'total_realized_pnl': total_realized_pnl,
                'total_unrealized_pnl': total_unrealized_pnl,
                'portfolio_return_percent': portfolio_return_percent
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio data: {e}")
            return {
                'total_value': 0.0,
                'total_invested': 0.0,
                'cash_balance': 10000.0,
                'available_cash': 10000.0,
                'total_stocks_held': 0,
                'active_investments': 0,
                'total_realized_pnl': 0.0,
                'total_unrealized_pnl': 0.0,
                'portfolio_return_percent': 0.0
            }
    
    def _get_portfolio_summary(self, user_id: str) -> Dict:
        """Get current portfolio summary"""
        try:
            portfolio_data = self._calculate_portfolio_data(user_id)
            
            # Get recent transactions
            query = """
                SELECT stock_code, stock_name, transaction_type, quantity, 
                       buy_price, total_invested, buy_date
                FROM investments 
                WHERE user_id = %s 
                ORDER BY buy_date DESC 
                LIMIT 5
            """
            
            recent_transactions = self.db.execute_query(query, (user_id,))
            
            return {
                'portfolio_data': portfolio_data,
                'recent_transactions': recent_transactions,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {
                'portfolio_data': {},
                'recent_transactions': [],
                'last_updated': datetime.now().isoformat()
            }

# Create instance for LangGraph integration
manager_record_agent = ManagerRecordAgent()

# Standalone function for LangGraph
async def handle_user_investment_decision(
    user_id: str,
    decision_type: str,
    stock_code: str = None,
    quantity: int = None,
    price: float = None,
    recommendation_id: str = None,
    **kwargs
) -> Dict:
    """Standalone function for handling user investment decisions"""
    return await manager_record_agent.handle_user_decision(
        user_id, decision_type, stock_code, quantity, price, recommendation_id, **kwargs
    ) 