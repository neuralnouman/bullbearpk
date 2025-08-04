import logging
from typing import Dict, Optional, List
import sys
import os
from datetime import datetime

# Add parent directory to path for database import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_config import db_config

logger = logging.getLogger(__name__)

class PastInvestmentsChecker:
    """Enhanced Portfolio History Agent for comprehensive investment analysis"""
    
    def __init__(self):
        self.performance_thresholds = {
            'excellent': 0.15,  # 15%+ return
            'good': 0.08,       # 8-15% return
            'average': 0.02,    # 2-8% return
            'poor': -0.05       # Below -5% return
        }
    
    async def check_past_investments(self, user_id: Optional[str] = None) -> Dict:
        """
        Enhanced user investment history analysis with comprehensive portfolio insights
        
        Args:
            user_id: User ID to get history for
            
        Returns:
            Dictionary with comprehensive user history and portfolio analysis
        """
        try:
            logger.info(f"Getting comprehensive user history for user {user_id}")
            
            if not user_id:
                return {
                    "success": False,
                    "history_summary": "No user history available.",
                    "preferred_sectors": [],
                    "recent_trades": [],
                    "total_invested": 0.0,
                    "total_profit_loss": 0.0,
                    "portfolio_analysis": {},
                    "investment_recommendations": []
                }
            
            # Get user investments from MySQL database
            investments = db_config.get_user_investments(user_id)
            
            # Get user portfolio
            portfolio = db_config.get_user_portfolio(user_id)
            
            # Analyze current portfolio status
            portfolio_analysis = self._analyze_current_portfolio(investments, portfolio)
            
            # Analyze investment performance
            performance_analysis = self._analyze_investment_performance(investments)
            
            # Generate investment recommendations
            investment_recommendations = self._generate_investment_recommendations(
                investments, portfolio_analysis, performance_analysis
            )
            
            # Process investments for history
            processed_investments = []
            sector_values = {}
            
            for inv in investments:
                processed_inv = {
                    "stock_code": inv.get('stock_code'),
                    "stock_name": inv.get('stock_name'),
                    "action": inv.get('transaction_type', 'buy'),
                    "quantity": inv.get('quantity'),
                    "price": inv.get('buy_price'),
                    "date": inv.get('buy_date'),
                    "sector": inv.get('sector'),
                    "current_value": inv.get('current_value'),
                    "profit_loss": inv.get('profit_loss'),
                    "profit_loss_percent": inv.get('profit_loss_percent'),
                    "status": inv.get('status', 'active')
                }
                processed_investments.append(processed_inv)
                
                # Calculate sector preferences
                sector = inv.get('sector', 'Unknown')
                if sector not in sector_values:
                    sector_values[sector] = 0
                sector_values[sector] += inv.get('total_invested', 0)
            
            # Sort sectors by investment value
            preferred_sectors = sorted(
                sector_values.keys(), 
                key=lambda s: sector_values.get(s, 0), 
                reverse=True
            )
            
            # Generate comprehensive summary
            history_summary = self._generate_comprehensive_summary(
                preferred_sectors, portfolio_analysis, performance_analysis
            )
            
            # Portfolio summary
            total_invested = portfolio.get('total_invested', 0.0) if portfolio else 0.0
            total_profit_loss = portfolio.get('total_profit_loss', 0.0) if portfolio else 0.0
            
            return {
                "success": True,
                "history_summary": history_summary,
                "preferred_sectors": preferred_sectors,
                "recent_trades": processed_investments[:10],  # Return 10 most recent trades
                "total_invested": total_invested,
                "total_profit_loss": total_profit_loss,
                "portfolio_value": portfolio.get('total_value', 0.0) if portfolio else 0.0,
                "portfolio_analysis": portfolio_analysis,
                "performance_analysis": performance_analysis,
                "investment_recommendations": investment_recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return {
                "success": False,
                "history_summary": "Error retrieving user history.",
                "preferred_sectors": [],
                "recent_trades": [],
                "total_invested": 0.0,
                "total_profit_loss": 0.0,
                "error": str(e)
            }
    
    def _analyze_current_portfolio(self, investments: List[Dict], portfolio: Dict) -> Dict:
        """Analyze current portfolio status and health"""
        try:
            active_investments = [inv for inv in investments if inv.get('status') == 'active']
            
            if not active_investments:
                return {
                    "portfolio_health": "new",
                    "diversification_score": 0.0,
                    "risk_level": "low",
                    "cash_utilization": 0.0,
                    "top_holdings": [],
                    "underperforming_stocks": [],
                    "overperforming_stocks": []
                }
            
            # Calculate portfolio metrics
            total_value = sum(float(inv.get('current_value', 0)) for inv in active_investments)
            total_invested = sum(float(inv.get('amount_invested', 0)) for inv in active_investments)
            
            # Calculate diversification
            sectors = set(inv.get('sector', 'Unknown') for inv in active_investments)
            diversification_score = len(sectors) / len(active_investments) if active_investments else 0
            
            # Analyze performance
            overperforming = []
            underperforming = []
            
            for inv in active_investments:
                pnl_percent = float(inv.get('profit_loss_percent', 0))
                if pnl_percent > 10:  # 10%+ gain
                    overperforming.append({
                        'stock_code': inv.get('stock_code'),
                        'stock_name': inv.get('stock_name'),
                        'profit_percent': pnl_percent,
                        'current_value': inv.get('current_value')
                    })
                elif pnl_percent < -5:  # -5%+ loss
                    underperforming.append({
                        'stock_code': inv.get('stock_code'),
                        'stock_name': inv.get('stock_name'),
                        'loss_percent': pnl_percent,
                        'current_value': inv.get('current_value')
                    })
            
            # Determine portfolio health
            if total_value > total_invested * 1.1:
                portfolio_health = "excellent"
            elif total_value > total_invested:
                portfolio_health = "good"
            elif total_value > total_invested * 0.9:
                portfolio_health = "average"
            else:
                portfolio_health = "poor"
            
            # Calculate cash utilization
            cash_balance = float(portfolio.get('cash_balance', 0)) if portfolio else 0
            cash_utilization = 1 - (cash_balance / max(total_value + cash_balance, 1))
            
            # Get top holdings
            top_holdings = sorted(
                active_investments,
                key=lambda x: float(x.get('current_value', 0)),
                reverse=True
            )[:5]
            
            return {
                "portfolio_health": portfolio_health,
                "diversification_score": diversification_score,
                "risk_level": "moderate" if diversification_score < 0.5 else "low",
                "cash_utilization": cash_utilization,
                "total_active_investments": len(active_investments),
                "total_portfolio_value": total_value,
                "total_invested": total_invested,
                "overall_return_percent": ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
                "top_holdings": top_holdings,
                "overperforming_stocks": overperforming,
                "underperforming_stocks": underperforming
            }
            
        except Exception as e:
            logger.error(f"Error analyzing current portfolio: {e}")
            return {
                "portfolio_health": "unknown",
                "diversification_score": 0.0,
                "risk_level": "moderate",
                "cash_utilization": 0.0,
                "top_holdings": [],
                "underperforming_stocks": [],
                "overperforming_stocks": []
            }
    
    def _analyze_investment_performance(self, investments: List[Dict]) -> Dict:
        """Analyze investment performance patterns"""
        try:
            if not investments:
                return {
                    "avg_holding_period": 0,
                    "win_rate": 0,
                    "avg_profit_percent": 0,
                    "best_performing_sector": "None",
                    "worst_performing_sector": "None",
                    "performance_trend": "stable"
                }
            
            # Calculate performance metrics
            profitable_trades = [inv for inv in investments if float(inv.get('profit_loss', 0)) > 0]
            win_rate = len(profitable_trades) / len(investments) if investments else 0
            
            # Calculate average profit percentage
            profit_percentages = [float(inv.get('profit_loss_percent', 0)) for inv in investments]
            avg_profit_percent = sum(profit_percentages) / len(profit_percentages) if profit_percentages else 0
            
            # Analyze sector performance
            sector_performance = {}
            for inv in investments:
                sector = inv.get('sector', 'Unknown')
                if sector not in sector_performance:
                    sector_performance[sector] = []
                sector_performance[sector].append(float(inv.get('profit_loss_percent', 0)))
            
            # Find best and worst performing sectors
            sector_avg_performance = {}
            for sector, performances in sector_performance.items():
                sector_avg_performance[sector] = sum(performances) / len(performances)
            
            if sector_avg_performance:
                best_sector = max(sector_avg_performance.items(), key=lambda x: x[1])
                worst_sector = min(sector_avg_performance.items(), key=lambda x: x[1])
                best_performing_sector = best_sector[0]
                worst_performing_sector = worst_sector[0]
            else:
                best_performing_sector = "None"
                worst_performing_sector = "None"
            
            # Determine performance trend
            if avg_profit_percent > 5:
                performance_trend = "improving"
            elif avg_profit_percent < -2:
                performance_trend = "declining"
            else:
                performance_trend = "stable"
            
            return {
                "avg_holding_period": 30,  # Simplified - would calculate from dates
                "win_rate": win_rate,
                "avg_profit_percent": avg_profit_percent,
                "best_performing_sector": best_performing_sector,
                "worst_performing_sector": worst_performing_sector,
                "performance_trend": performance_trend,
                "total_trades": len(investments),
                "profitable_trades": len(profitable_trades)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing investment performance: {e}")
            return {
                "avg_holding_period": 0,
                "win_rate": 0,
                "avg_profit_percent": 0,
                "best_performing_sector": "None",
                "worst_performing_sector": "None",
                "performance_trend": "stable"
            }
    
    def _generate_investment_recommendations(self, investments: List[Dict], portfolio_analysis: Dict, performance_analysis: Dict) -> List[str]:
        """Generate investment recommendations based on analysis"""
        recommendations = []
        
        try:
            # Portfolio health recommendations
            portfolio_health = portfolio_analysis.get('portfolio_health', 'unknown')
            if portfolio_health == 'poor':
                recommendations.append("Consider reviewing underperforming positions and setting stop-losses")
            elif portfolio_health == 'excellent':
                recommendations.append("Portfolio performing well - consider taking partial profits on overperforming stocks")
            
            # Diversification recommendations
            diversification_score = portfolio_analysis.get('diversification_score', 0)
            if diversification_score < 0.3:
                recommendations.append("Portfolio lacks diversification - consider adding stocks from different sectors")
            
            # Performance recommendations
            win_rate = performance_analysis.get('win_rate', 0)
            if win_rate < 0.4:
                recommendations.append("Low win rate suggests need for better entry/exit timing - consider technical analysis")
            
            # Cash utilization recommendations
            cash_utilization = portfolio_analysis.get('cash_utilization', 0)
            if cash_utilization > 0.9:
                recommendations.append("High cash utilization - maintain some reserves for opportunities")
            elif cash_utilization < 0.5:
                recommendations.append("Low cash utilization - consider deploying more capital if opportunities arise")
            
            # Sector recommendations
            best_sector = performance_analysis.get('best_performing_sector', 'None')
            worst_sector = performance_analysis.get('worst_performing_sector', 'None')
            
            if best_sector != 'None':
                recommendations.append(f"Consider increasing exposure to {best_sector} sector based on past performance")
            
            if worst_sector != 'None':
                recommendations.append(f"Review positions in {worst_sector} sector - consider reducing exposure")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating investment recommendations: {e}")
            return ["Unable to generate specific recommendations at this time"]
    
    def _generate_comprehensive_summary(self, preferred_sectors: List[str], portfolio_analysis: Dict, performance_analysis: Dict) -> str:
        """Generate comprehensive portfolio summary"""
        try:
            summary_parts = []
            
            # Portfolio health summary
            portfolio_health = portfolio_analysis.get('portfolio_health', 'unknown')
            summary_parts.append(f"Portfolio health: {portfolio_health.title()}")
            
            # Performance summary
            win_rate = performance_analysis.get('win_rate', 0)
            avg_profit = performance_analysis.get('avg_profit_percent', 0)
            summary_parts.append(f"Win rate: {win_rate:.1%}, Average return: {avg_profit:.1f}%")
            
            # Sector preferences
            if preferred_sectors:
                top_sectors = preferred_sectors[:3]
                summary_parts.append(f"Preferred sectors: {', '.join(top_sectors)}")
            
            # Diversification
            diversification = portfolio_analysis.get('diversification_score', 0)
            if diversification < 0.5:
                summary_parts.append("Portfolio needs better diversification")
            else:
                summary_parts.append("Good sector diversification")
            
            # Active investments
            active_count = portfolio_analysis.get('total_active_investments', 0)
            summary_parts.append(f"Active investments: {active_count}")
            
            return ". ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating comprehensive summary: {e}")
            return "Portfolio analysis summary unavailable"
            
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return {
                "history_summary": "Error retrieving user history.",
                "preferred_sectors": [],
                "recent_trades": [],
                "total_invested": 0.0,
                "total_profit_loss": 0.0,
                "error": str(e)
            }

# Standalone function for agentic framework
async def check_past_investments(user_id: Optional[str] = None) -> Dict:
    """
    Standalone function for checking past investments
    """
    agent = PastInvestmentsChecker()
    return await agent.check_past_investments(user_id=user_id)
        
    def get_extended_context(self, user_id):
        """Get extended user context based on history"""
        if not user_id:
            return {
                "risk_tolerance": "moderate",
                "investment_horizon": "medium",
                "preferred_sectors": []
            }
            
        # Get user preferences from database
        from agents.stock_agent import EnhancedDatabaseManager
        db_manager = EnhancedDatabaseManager()
        
        user_prefs = {
            "risk_tolerance": "moderate",
            "investment_horizon": "medium",
            "preferred_sectors": []
        }
        
        with db_manager.get_connection() as conn:
            # Get user preferences
            result = conn.execute('''
                SELECT * FROM user_preferences 
                WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            if result:
                user_prefs["risk_tolerance"] = result['risk_appetite']
                user_prefs["investment_horizon"] = result['time_horizon']
                user_prefs["preferred_sectors"] = [result['sector']] if result['sector'] else []
                
        # If no preferred sectors in preferences, get from investments
        if not user_prefs["preferred_sectors"]:
            history = self.run(user_id)
            user_prefs["preferred_sectors"] = history.get("preferred_sectors", [])
            
        return user_prefs
        
    def update_from_feedback(self, user_id, feedback, recommendations):
        """Update user history based on feedback"""
        if not user_id or not feedback or not recommendations:
            return False
            
        # Extract sectors from recommendations
        sectors = []
        for rec in recommendations:
            if isinstance(rec, dict) and 'company' in rec:
                # Extract sector if available
                if 'analysis_highlights' in rec and 'sector' in rec['analysis_highlights']:
                    sectors.append(rec['analysis_highlights']['sector'])
        
        # Update user preferences in database if we have sectors
        if sectors:
            from agents.stock_agent import EnhancedDatabaseManager
            db_manager = EnhancedDatabaseManager()
            
            with db_manager.get_connection() as conn:
                # Get existing preferences
                result = conn.execute('''
                    SELECT * FROM user_preferences 
                    WHERE user_id = ?
                ''', (user_id,)).fetchone()
                
                if result:
                    # Update sector preference based on feedback
                    if feedback.lower() == 'positive':
                        # Use the first sector from recommendations
                        conn.execute('''
                            UPDATE user_preferences 
                            SET sector = ? 
                            WHERE user_id = ?
                        ''', (sectors[0], user_id))
                        conn.commit()
                
        return True