import logging
from typing import Dict, Optional, List
import sys
import os
from datetime import datetime

# Add parent directory to path for database import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_config import db_config

logger = logging.getLogger(__name__)

class RiskChecker:
    """Enhanced Risk Profiler Agent for comprehensive investment behavior analysis"""
    
    def __init__(self):
        self.risk_keywords = {
            "bankruptcy", "default", "debt", "loss", "decline", "downturn", "recession",
            "crisis", "scandal", "investigation", "penalty", "fine", "suspension",
            "delisting", "insolvency", "liquidation", "restructuring", "layoffs"
        }
        
        self.opportunity_keywords = {
            "growth", "expansion", "profit", "success", "award", "recognition",
            "partnership", "contract", "deal", "investment", "funding", "innovation"
        }
    
    async def check_risk_profile(self, user_id: Optional[str] = None, user_input: Dict = None) -> Dict:
        """
        Enhanced risk profile analysis based on user's investment history and behavior
        """
        try:
            logger.info(f"Analyzing comprehensive risk profile for user {user_id}")
            
            # Get user profile from database
            user_profile = None
            if user_id:
                user_profile = db_config.get_user_profile(user_id)
            
            # Get user's investment history
            investment_history = []
            if user_id:
                investment_history = db_config.get_user_investments(user_id)
            
            # Get user's portfolio
            portfolio = None
            if user_id:
                portfolio = db_config.get_user_portfolio(user_id)
            
            # Analyze investment behavior patterns
            behavior_analysis = self._analyze_investment_behavior(investment_history)
            
            # Analyze portfolio risk metrics
            portfolio_risk = self._analyze_portfolio_risk(portfolio, investment_history)
            
            # Calculate comprehensive risk score
            risk_score = self._calculate_comprehensive_risk_score(user_profile, behavior_analysis, portfolio_risk)
            
            # Generate risk profile
            risk_profile = self._generate_risk_profile(user_profile, behavior_analysis, portfolio_risk, risk_score)
            
            return {
                "success": True,
                "risk_profile": risk_profile,
                "behavior_analysis": behavior_analysis,
                "portfolio_risk": portfolio_risk,
                "user_profile": user_profile,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive risk profile analysis: {e}")
            return {
                "success": False,
                "risk_profile": {
                    "risk_level": "moderate",
                    "risk_score": 0.5,
                    "recommendation": "Unable to complete risk analysis. Using moderate risk profile."
                },
                "error": str(e)
            }
    
    def _analyze_investment_behavior(self, investment_history: List[Dict]) -> Dict:
        """Analyze user's investment behavior patterns"""
        try:
            if not investment_history:
                return {
                    "total_trades": 0,
                    "avg_trade_size": 0,
                    "holding_period_avg": 0,
                    "profit_loss_ratio": 0,
                    "risk_tolerance_indicator": "moderate",
                    "trading_frequency": "low",
                    "sector_diversification": 0,
                    "behavior_score": 0.5
                }
            
            # Calculate trading metrics
            total_trades = len(investment_history)
            total_invested = sum(float(inv.get('amount_invested', 0)) for inv in investment_history)
            avg_trade_size = total_invested / total_trades if total_trades > 0 else 0
            
            # Calculate holding periods
            holding_periods = []
            for inv in investment_history:
                if inv.get('buy_date') and inv.get('sell_date'):
                    try:
                        buy_date = datetime.strptime(inv['buy_date'], '%Y-%m-%d')
                        sell_date = datetime.strptime(inv['sell_date'], '%Y-%m-%d')
                        holding_days = (sell_date - buy_date).days
                        holding_periods.append(holding_days)
                    except:
                        continue
            
            avg_holding_period = sum(holding_periods) / len(holding_periods) if holding_periods else 0
            
            # Calculate profit/loss ratio
            profitable_trades = [inv for inv in investment_history if float(inv.get('realized_pnl', 0)) > 0]
            profit_loss_ratio = len(profitable_trades) / total_trades if total_trades > 0 else 0
            
            # Analyze trading frequency
            if total_trades > 20:
                trading_frequency = "high"
            elif total_trades > 10:
                trading_frequency = "medium"
            else:
                trading_frequency = "low"
            
            # Analyze sector diversification
            sectors = set(inv.get('sector', 'Unknown') for inv in investment_history)
            sector_diversification = len(sectors) / max(total_trades, 1)
            
            # Calculate behavior score
            behavior_score = (
                (profit_loss_ratio * 0.4) +
                (min(avg_holding_period / 365, 1) * 0.3) +
                (sector_diversification * 0.3)
            )
            
            # Determine risk tolerance indicator
            if behavior_score > 0.7:
                risk_tolerance_indicator = "conservative"
            elif behavior_score < 0.3:
                risk_tolerance_indicator = "aggressive"
            else:
                risk_tolerance_indicator = "moderate"
            
            return {
                "total_trades": total_trades,
                "avg_trade_size": avg_trade_size,
                "holding_period_avg": avg_holding_period,
                "profit_loss_ratio": profit_loss_ratio,
                "risk_tolerance_indicator": risk_tolerance_indicator,
                "trading_frequency": trading_frequency,
                "sector_diversification": sector_diversification,
                "behavior_score": behavior_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing investment behavior: {e}")
            return {
                "total_trades": 0,
                "avg_trade_size": 0,
                "holding_period_avg": 0,
                "profit_loss_ratio": 0,
                "risk_tolerance_indicator": "moderate",
                "trading_frequency": "low",
                "sector_diversification": 0,
                "behavior_score": 0.5
            }
    
    def _analyze_portfolio_risk(self, portfolio: Dict, investment_history: List[Dict]) -> Dict:
        """Analyze current portfolio risk metrics"""
        try:
            if not portfolio:
                return {
                    "portfolio_volatility": 0.5,
                    "concentration_risk": 0.5,
                    "liquidity_risk": 0.5,
                    "sector_risk": 0.5,
                    "overall_portfolio_risk": 0.5
                }
            
            # Calculate portfolio volatility
            total_value = float(portfolio.get('total_value', 0))
            total_profit_loss = float(portfolio.get('total_profit_loss', 0))
            portfolio_volatility = abs(total_profit_loss) / max(total_value, 1)
            
            # Calculate concentration risk
            active_investments = [inv for inv in investment_history if inv.get('status') == 'active']
            if active_investments:
                largest_investment = max(float(inv.get('current_value', 0)) for inv in active_investments)
                concentration_risk = largest_investment / max(total_value, 1)
            else:
                concentration_risk = 0.5
            
            # Calculate liquidity risk
            cash_balance = float(portfolio.get('cash_balance', 0))
            liquidity_risk = 1 - (cash_balance / max(total_value, 1))
            
            # Calculate sector risk
            sectors = {}
            for inv in active_investments:
                sector = inv.get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + float(inv.get('current_value', 0))
            
            if sectors:
                max_sector_exposure = max(sectors.values())
                sector_risk = max_sector_exposure / max(total_value, 1)
            else:
                sector_risk = 0.5
            
            # Calculate overall portfolio risk
            overall_portfolio_risk = (
                portfolio_volatility * 0.3 +
                concentration_risk * 0.25 +
                liquidity_risk * 0.25 +
                sector_risk * 0.2
            )
            
            return {
                "portfolio_volatility": portfolio_volatility,
                "concentration_risk": concentration_risk,
                "liquidity_risk": liquidity_risk,
                "sector_risk": sector_risk,
                "overall_portfolio_risk": overall_portfolio_risk
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio risk: {e}")
            return {
                "portfolio_volatility": 0.5,
                "concentration_risk": 0.5,
                "liquidity_risk": 0.5,
                "sector_risk": 0.5,
                "overall_portfolio_risk": 0.5
            }
    
    def _calculate_comprehensive_risk_score(self, user_profile: Dict, behavior_analysis: Dict, portfolio_risk: Dict) -> float:
        """Calculate comprehensive risk score based on all factors"""
        try:
            # Base risk score from user profile
            base_risk = 0.5
            risk_tolerance = 'moderate'  # Default value
            
            if user_profile:
                risk_tolerance = user_profile.get('risk_tolerance', 'moderate').lower()
            
            if risk_tolerance == 'low':
                base_risk = 0.3
            elif risk_tolerance == 'high':
                base_risk = 0.8
            
            # Behavior-based risk adjustment
            behavior_score = behavior_analysis.get('behavior_score', 0.5)
            behavior_risk = 1 - behavior_score  # Higher behavior score = lower risk
            
            # Portfolio risk
            portfolio_risk_score = portfolio_risk.get('overall_portfolio_risk', 0.5)
            
            # Calculate weighted risk score
            comprehensive_risk = (
                base_risk * 0.3 +
                behavior_risk * 0.4 +
                portfolio_risk_score * 0.3
            )
            
            return min(max(comprehensive_risk, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive risk score: {e}")
            return 0.5
    
    def _generate_risk_profile(self, user_profile: Dict, behavior_analysis: Dict, portfolio_risk: Dict, risk_score: float) -> Dict:
        """Generate comprehensive risk profile"""
        try:
            # Determine risk level
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.7:
                risk_level = "moderate"
            else:
                risk_level = "high"
            
            # Generate recommendations based on analysis
            recommendations = []
            
            if behavior_analysis.get('profit_loss_ratio', 0) < 0.5:
                recommendations.append("Consider improving trade timing and risk management")
            
            if portfolio_risk.get('concentration_risk', 0) > 0.3:
                recommendations.append("Diversify portfolio to reduce concentration risk")
            
            if portfolio_risk.get('liquidity_risk', 0) > 0.7:
                recommendations.append("Maintain higher cash reserves for liquidity")
            
            if behavior_analysis.get('sector_diversification', 0) < 0.3:
                recommendations.append("Consider diversifying across more sectors")
            
            # Generate comprehensive recommendation
            if risk_level == "low":
                main_recommendation = "Focus on stable, dividend-paying stocks with lower volatility. Consider blue-chip companies and defensive sectors."
            elif risk_level == "high":
                main_recommendation = "Consider growth stocks with higher potential returns but increased volatility. Monitor positions closely and set stop-losses."
            else:
                main_recommendation = "Balance your portfolio between growth and stability. Consider a mix of growth and value stocks."
            
            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "recommendation": main_recommendation,
                "detailed_recommendations": recommendations,
                "behavior_insights": {
                    "trading_frequency": behavior_analysis.get('trading_frequency', 'low'),
                    "avg_holding_period": behavior_analysis.get('holding_period_avg', 0),
                    "profit_loss_ratio": behavior_analysis.get('profit_loss_ratio', 0),
                    "sector_diversification": behavior_analysis.get('sector_diversification', 0)
                },
                "portfolio_insights": {
                    "volatility": portfolio_risk.get('portfolio_volatility', 0),
                    "concentration_risk": portfolio_risk.get('concentration_risk', 0),
                    "liquidity_risk": portfolio_risk.get('liquidity_risk', 0),
                    "sector_risk": portfolio_risk.get('sector_risk', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating risk profile: {e}")
            return {
                "risk_level": "moderate",
                "risk_score": 0.5,
                "recommendation": "Unable to generate detailed risk profile. Using moderate risk level.",
                "detailed_recommendations": [],
                "behavior_insights": {},
                "portfolio_insights": {}
            }

# Standalone function for agentic framework
async def check_risk_profile(user_id: Optional[str] = None, user_input: Dict = None) -> Dict:
    """
    Enhanced risk profile analysis based on user's investment history and behavior
    """
    try:
        logger.info(f"Checking comprehensive risk profile for user {user_id}")
        
        # Get user profile from database
        user_profile = None
        if user_id:
            user_profile = db_config.get_user_profile(user_id)
        
        # Get user's investment history
        investment_history = []
        if user_id:
            investment_history = db_config.get_user_investments(user_id)
        
        # Get user's portfolio
        portfolio = None
        if user_id:
            portfolio = db_config.get_user_portfolio(user_id)
        
        # Create agent instance and analyze
        agent = RiskChecker()
        return await agent.check_risk_profile(user_id=user_id)
        
    except Exception as e:
        logger.error(f"Error in comprehensive risk profile analysis: {e}")
        return {
            "success": False,
            "risk_profile": {
                "risk_level": "moderate",
                "risk_score": 0.5,
                "recommendation": "Unable to complete risk analysis. Using moderate risk profile."
            },
            "error": str(e)
        }