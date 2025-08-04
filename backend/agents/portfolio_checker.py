import logging
from typing import Dict, Optional, List
import sys
import os
from datetime import datetime

# Add parent directory to path for database import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_config import db_config

logger = logging.getLogger(__name__)

class PortfolioChecker:
    """Enhanced Portfolio Updater Agent for comprehensive portfolio analysis and updates"""
    
    def __init__(self):
        self.analysis_thresholds = {
            'excellent_performance': 0.15,  # 15%+ return
            'good_performance': 0.08,       # 8-15% return
            'average_performance': 0.02,    # 2-8% return
            'poor_performance': -0.05       # Below -5% return
        }
    
    async def check_portfolio(self, user_id: Optional[str] = None, stock_data: List[Dict] = None) -> Dict:
        """
        Enhanced portfolio analysis for existing portfolios
        
        Args:
            user_id: User ID to check portfolio for
            stock_data: Current stock market data
            
        Returns:
            Dictionary with comprehensive portfolio analysis information
        """
        try:
            logger.info(f"Starting comprehensive portfolio check for user {user_id}")
            
            if not user_id:
                return {
                    "status": "error",
                    "message": "Missing user ID.",
                    "updated_holdings": [],
                    "total_value": 0.0,
                    "total_profit_loss": 0.0,
                    "portfolio_analysis": {}
                }
            
            # Get user portfolio and investments from MySQL database
            portfolio = db_config.get_user_portfolio(user_id)
            investments = db_config.get_user_investments(user_id)
            
            # Check if user is new (no existing portfolio data)
            if not portfolio or not investments:
                logger.info(f"No existing portfolio found for user {user_id} - new user")
                return {
                    "status": "new_user",
                    "message": "No existing portfolio found. User is new to the platform.",
                    "updated_holdings": [],
                    "total_value": 0.0,
                    "total_invested": 0.0,
                    "total_profit_loss": 0.0,
                    "portfolio_analysis": {
                        "portfolio_status": "new_user",
                        "recommendations": [
                            "Start with small investments to build portfolio",
                            "Consider diversifying across sectors",
                            "Set up initial investment goals"
                        ],
                        "risk_level": "low",
                        "cash_available": 10000.0  # Default starting cash
                    }
                }
            
            # Perform comprehensive portfolio analysis for existing portfolio
            portfolio_update = self._update_portfolio_values(investments, stock_data)
            portfolio_analysis = self._analyze_portfolio_performance(portfolio_update)
            recommendations = self._generate_portfolio_recommendations(portfolio_analysis)
            
            logger.info(f"Portfolio analysis completed for user {user_id}")
            logger.info(f"Portfolio Analysis Summary:")
            logger.info(f"  - Total Holdings: {len(portfolio_update['updated_holdings'])}")
            logger.info(f"  - Total Value: ${portfolio_update['total_value']:,.2f}")
            logger.info(f"  - Total P&L: ${portfolio_update['total_profit_loss']:,.2f}")
            logger.info(f"  - Performance: {portfolio_analysis['overall_performance']}")
            logger.info(f"  - Risk Level: {portfolio_analysis['risk_level']}")
            logger.info(f"  - Recommendations: {len(recommendations)} generated")
            
            return {
                "status": "existing_user",
                "message": "Portfolio analysis completed successfully.",
                "updated_holdings": portfolio_update['updated_holdings'],
                "total_value": portfolio_update['total_value'],
                "total_invested": portfolio_update['total_invested'],
                "total_profit_loss": portfolio_update['total_profit_loss'],
                "profit_loss_percent": portfolio_update['profit_loss_percent'],
                "portfolio_analysis": portfolio_analysis,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking portfolio: {e}")
            return {
                "status": "error",
                "message": f"Error checking portfolio: {str(e)}",
                "updated_holdings": [],
                "total_value": 0.0,
                "total_profit_loss": 0.0,
                "portfolio_analysis": {}
            }
    

    
    def _update_portfolio_values(self, investments: List[Dict], stock_data: List[Dict]) -> Dict:
        """Update portfolio values with current market data"""
        try:
            updated_holdings = []
            total_current_value = 0.0
            total_invested = 0.0
            total_profit_loss = 0.0
            
            for investment in investments:
                stock_code = investment.get('stock_code')
                quantity = float(investment.get('quantity', 0))
                buy_price = float(investment.get('buy_price', 0))
                total_invested_amount = float(investment.get('total_invested', 0))
                
                # Find current stock price from stock_data
                current_price = buy_price  # Default to buy price if not found
                if stock_data:
                    for stock in stock_data:
                        if stock.get('code') == stock_code:
                            current_price = float(stock.get('close_price', buy_price))
                            break
                
                # Calculate current value and profit/loss
                current_value = quantity * current_price
                profit_loss = current_value - total_invested_amount
                profit_loss_percent = (profit_loss / total_invested_amount * 100) if total_invested_amount > 0 else 0
                
                updated_holding = {
                    "stock_code": stock_code,
                    "stock_name": investment.get('stock_name', ''),
                    "quantity": quantity,
                    "buy_price": buy_price,
                    "current_price": current_price,
                    "total_invested": total_invested_amount,
                    "current_value": current_value,
                    "profit_loss": profit_loss,
                    "profit_loss_percent": profit_loss_percent,
                    "sector": investment.get('sector', ''),
                    "status": investment.get('status', 'active')
                }
                
                updated_holdings.append(updated_holding)
                total_current_value += current_value
                total_invested += total_invested_amount
                total_profit_loss += profit_loss
            
            overall_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
            
            return {
                "updated_holdings": updated_holdings,
                "total_value": total_current_value,
                "total_invested": total_invested,
                "total_profit_loss": total_profit_loss,
                "profit_loss_percent": overall_profit_loss_percent
            }
            
        except Exception as e:
            logger.error(f"Error updating portfolio values: {e}")
            return {
                "updated_holdings": [],
                "total_value": 0.0,
                "total_invested": 0.0,
                "total_profit_loss": 0.0,
                "profit_loss_percent": 0.0
            }
    
    def _analyze_portfolio_performance(self, portfolio_update: Dict) -> Dict:
        """Analyze portfolio performance and risk metrics"""
        try:
            holdings = portfolio_update['updated_holdings']
            total_value = portfolio_update['total_value']
            total_profit_loss = portfolio_update['total_profit_loss']
            profit_loss_percent = portfolio_update['profit_loss_percent']
            
            if not holdings:
                return {
                    "overall_performance": "new_portfolio",
                    "risk_level": "low",
                    "diversification_score": 0.0,
                    "top_performers": [],
                    "underperformers": [],
                    "sector_allocation": {},
                    "volatility_analysis": "insufficient_data"
                }
            
            # Analyze individual holdings
            top_performers = []
            underperformers = []
            
            for holding in holdings:
                pnl_percent = holding['profit_loss_percent']
                if pnl_percent > 10:  # 10%+ gain
                    top_performers.append({
                        'stock_code': holding['stock_code'],
                        'stock_name': holding['stock_name'],
                        'profit_percent': pnl_percent,
                        'current_value': holding['current_value']
                    })
                elif pnl_percent < -5:  # -5%+ loss
                    underperformers.append({
                        'stock_code': holding['stock_code'],
                        'stock_name': holding['stock_name'],
                        'loss_percent': pnl_percent,
                        'current_value': holding['current_value']
                    })
            
            # Calculate diversification
            sectors = set(holding['sector'] for holding in holdings)
            diversification_score = len(sectors) / len(holdings) if holdings else 0
            
            # Sector allocation
            sector_allocation = {}
            for holding in holdings:
                sector = holding['sector']
                if sector not in sector_allocation:
                    sector_allocation[sector] = 0
                sector_allocation[sector] += holding['current_value']
            
            # Determine overall performance
            if profit_loss_percent > 15:
                overall_performance = "excellent"
            elif profit_loss_percent > 8:
                overall_performance = "good"
            elif profit_loss_percent > 2:
                overall_performance = "average"
            elif profit_loss_percent > -5:
                overall_performance = "below_average"
            else:
                overall_performance = "poor"
            
            # Determine risk level
            if diversification_score < 0.3:
                risk_level = "high"
            elif diversification_score < 0.6:
                risk_level = "moderate"
            else:
                risk_level = "low"
            
            return {
                "overall_performance": overall_performance,
                "risk_level": risk_level,
                "diversification_score": diversification_score,
                "total_holdings": len(holdings),
                "top_performers": top_performers,
                "underperformers": underperformers,
                "sector_allocation": sector_allocation,
                "profit_loss_percent": profit_loss_percent,
                "volatility_analysis": "moderate" if len(holdings) > 3 else "low"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio performance: {e}")
            return {
                "overall_performance": "unknown",
                "risk_level": "moderate",
                "diversification_score": 0.0,
                "top_performers": [],
                "underperformers": [],
                "sector_allocation": {},
                "volatility_analysis": "unknown"
            }
    
    def _generate_portfolio_recommendations(self, portfolio_analysis: Dict) -> List[str]:
        """Generate portfolio-specific recommendations"""
        recommendations = []
        
        try:
            performance = portfolio_analysis.get('overall_performance', 'unknown')
            risk_level = portfolio_analysis.get('risk_level', 'moderate')
            diversification = portfolio_analysis.get('diversification_score', 0)
            top_performers = portfolio_analysis.get('top_performers', [])
            underperformers = portfolio_analysis.get('underperformers', [])
            
            # Performance-based recommendations
            if performance == 'excellent':
                recommendations.append("Portfolio performing excellently - consider taking partial profits on top performers")
            elif performance == 'poor':
                recommendations.append("Review underperforming positions and consider setting stop-losses")
            
            # Diversification recommendations
            if diversification < 0.3:
                recommendations.append("Portfolio lacks diversification - consider adding stocks from different sectors")
            elif diversification > 0.7:
                recommendations.append("Good diversification - maintain current sector allocation")
            
            # Risk-based recommendations
            if risk_level == 'high':
                recommendations.append("High concentration risk - consider reducing exposure to largest holdings")
            elif risk_level == 'low':
                recommendations.append("Low risk portfolio - consider adding growth stocks for higher returns")
            
            # Specific stock recommendations
            if top_performers:
                recommendations.append(f"Consider taking profits on {len(top_performers)} overperforming stocks")
            
            if underperformers:
                recommendations.append(f"Review {len(underperformers)} underperforming stocks for potential exit")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating portfolio recommendations: {e}")
            return ["Unable to generate specific portfolio recommendations at this time"]

# Standalone function for agentic framework
async def check_portfolio(user_id: Optional[str] = None, stock_analysis: List[Dict] = None) -> Dict:
    """
    Standalone function for portfolio analysis
    """
    agent = PortfolioChecker()
    return await agent.check_portfolio(user_id=user_id, stock_data=stock_analysis)