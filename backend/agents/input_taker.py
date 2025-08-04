#!/usr/bin/env python3
"""
Input Taker Agent for BullBearPK
================================

This agent is responsible for:
1. Taking user input from frontend forms
2. Validating and processing user preferences
3. Converting form data to agentic framework format
4. Initiating the LangGraph workflow
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class UserInvestmentProfile:
    """User investment profile from form input"""
    user_id: str
    budget: float
    sector_preference: str
    risk_tolerance: str
    time_horizon: str
    target_profit: float
    investment_goal: str
    chat_message: Optional[str] = None
    additional_preferences: Optional[Dict] = None

class InputTakerAgent:
    """Agent responsible for taking and processing user input"""
    
    def __init__(self):
        self.supported_sectors = [
            "Banking", "Technology", "Energy", "Healthcare", "Consumer Goods",
            "Real Estate", "Manufacturing", "Telecommunications", "Transportation",
            "Utilities", "Any"
        ]
        
        self.risk_levels = ["low", "moderate", "high"]
        self.time_horizons = ["short", "medium", "long"]
        self.investment_goals = ["growth", "income", "balanced", "conservative"]
    
    def validate_user_input(self, form_data: Dict) -> Dict[str, Any]:
        """Validate user input from frontend form"""
        try:
            # Extract and validate budget
            budget = float(form_data.get('budget', 0))
            if budget <= 0:
                return {"valid": False, "error": "Budget must be greater than 0"}
            
            # Extract and validate sector preference
            sector = form_data.get('sector_preference', 'Any')
            if sector not in self.supported_sectors:
                return {"valid": False, "error": f"Unsupported sector: {sector}"}
            
            # Extract and validate risk tolerance
            risk = form_data.get('risk_tolerance', 'moderate').lower()
            if risk not in self.risk_levels:
                return {"valid": False, "error": f"Invalid risk tolerance: {risk}"}
            
            # Extract and validate time horizon
            horizon = form_data.get('time_horizon', 'medium').lower()
            if horizon not in self.time_horizons:
                return {"valid": False, "error": f"Invalid time horizon: {horizon}"}
            
            # Extract and validate target profit
            target_profit = float(form_data.get('target_profit', 10))
            if target_profit < 0 or target_profit > 100:
                return {"valid": False, "error": "Target profit must be between 0 and 100"}
            
            # Extract and validate investment goal
            goal = form_data.get('investment_goal', 'growth').lower()
            if goal not in self.investment_goals:
                return {"valid": False, "error": f"Invalid investment goal: {goal}"}
            
            # Extract user ID
            user_id = form_data.get('user_id', 'default_user')
            
            # Extract chat message if provided
            chat_message = form_data.get('chat_message', '')
            
            return {
                "valid": True,
                "user_id": user_id,
                "budget": budget,
                "sector_preference": sector,
                "risk_tolerance": risk,
                "time_horizon": horizon,
                "target_profit": target_profit,
                "investment_goal": goal,
                "chat_message": chat_message
            }
            
        except (ValueError, TypeError) as e:
            return {"valid": False, "error": f"Invalid input format: {str(e)}"}
    
    def create_investment_profile(self, validated_data: Dict) -> UserInvestmentProfile:
        """Create investment profile from validated data"""
        return UserInvestmentProfile(
            user_id=validated_data['user_id'],
            budget=validated_data['budget'],
            sector_preference=validated_data['sector_preference'],
            risk_tolerance=validated_data['risk_tolerance'],
            time_horizon=validated_data['time_horizon'],
            target_profit=validated_data['target_profit'],
            investment_goal=validated_data['investment_goal'],
            chat_message=validated_data.get('chat_message', ''),
            additional_preferences={
                "refresh_data": validated_data.get('refresh_data', False),
                "max_recommendations": validated_data.get('max_recommendations', 5)
            }
        )
    
    def format_for_agentic_framework(self, profile: UserInvestmentProfile) -> Dict:
        """Format user profile for agentic framework"""
        return {
            "user_id": profile.user_id,
            "budget": profile.budget,
            "sector_preference": profile.sector_preference,
            "risk_tolerance": profile.risk_tolerance,
            "time_horizon": profile.time_horizon,
            "target_profit": profile.target_profit,
            "investment_goal": profile.investment_goal,
            "message": profile.chat_message,
            "refresh_data": profile.additional_preferences.get('refresh_data', False),
            "max_recommendations": profile.additional_preferences.get('max_recommendations', 5)
        }
    
    async def process_user_input(self, form_data: Dict) -> Dict:
        """Main method to process user input and initiate agentic workflow"""
        try:
            logger.info(f"Processing user input for user: {form_data.get('user_id', 'unknown')}")
            
            # Step 1: Validate input
            validation_result = self.validate_user_input(form_data)
            if not validation_result['valid']:
                return {
                    "success": False,
                    "error": validation_result['error'],
                    "message": "Invalid input provided"
                }
            
            # Step 2: Create investment profile
            profile = self.create_investment_profile(validation_result)
            logger.info(f"Created investment profile for user {profile.user_id}")
            
            # Step 3: Format for agentic framework
            agentic_input = self.format_for_agentic_framework(profile)
            
            # Step 4: Import and call agentic framework
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from agentic_framework import agentic_framework
            
            logger.info(f"Initiating agentic workflow for user {profile.user_id}")
            
            # Step 5: Run the agentic workflow
            workflow_result = await agentic_framework.run_workflow(
                user_input=agentic_input,
                chat_message=profile.chat_message,
                user_id=profile.user_id
            )
            
            if not workflow_result.get('success', False):
                return {
                    "success": False,
                    "error": workflow_result.get('error', 'Unknown error'),
                    "message": "Agentic workflow failed"
                }
            
            # Step 6: Extract analysis results (recommendations are now generated in the LangGraph pipeline)
            analysis_data = workflow_result.get('data', {})
            recommendations = analysis_data.get('recommendations', [])
            
            if recommendations:
                logger.info(f"Successfully generated {len(recommendations)} recommendations through LangGraph pipeline")
                analysis_data['recommendations_saved'] = True
            else:
                logger.warning("No recommendations generated in LangGraph pipeline")
                analysis_data['recommendations_saved'] = False
            
            # Step 7: Return success response
            return {
                "success": True,
                "message": "Investment analysis completed successfully",
                "user_profile": {
                    "user_id": profile.user_id,
                    "budget": profile.budget,
                    "sector_preference": profile.sector_preference,
                    "risk_tolerance": profile.risk_tolerance,
                    "time_horizon": profile.time_horizon,
                    "target_profit": profile.target_profit,
                    "investment_goal": profile.investment_goal
                },
                "analysis_results": analysis_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Internal server error"
            }

# Create a global instance
input_taker_agent = InputTakerAgent()

async def input_taker_node(state: Dict) -> Dict:
    """LangGraph node for input taking"""
    try:
        logger.info("Starting input taker node...")
        
        # Extract user input from state
        user_input = state.get('user_input', {})
        
        # Process the input
        result = await input_taker_agent.process_user_input(user_input)
        
        if result['success']:
            # Add results to state
            state['input_processing'] = {
                "success": True,
                "user_profile": result['user_profile'],
                "analysis_results": result['analysis_results']
            }
            logger.info("Input processing completed successfully")
        else:
            # Add error to state
            state['input_processing'] = {
                "success": False,
                "error": result.get('error', 'Unknown error')
            }
            logger.error(f"Input processing failed: {result.get('error')}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in input taker node: {str(e)}")
        state['input_processing'] = {
            "success": False,
            "error": str(e)
        }
        return state

# Terminal interface for testing
async def terminal_input_interface():
    """Terminal interface for testing user input"""
    print("=" * 60)
    print("🎯 BULLBEARPK - USER INPUT INTERFACE")
    print("=" * 60)
    print("📝 Please enter your investment preferences:")
    print("=" * 60)
    
    # Get user input interactively
    user_form_data = {}
    
    # User ID
    user_id = input("👤 Enter User ID (or press Enter for 'test_user_001'): ").strip()
    user_form_data['user_id'] = user_id if user_id else "test_user_001"
    
    # Budget
    while True:
        try:
            budget_input = input("💰 Enter investment budget (PKR): ").strip()
            budget = float(budget_input) if budget_input else 50000
            if budget <= 0:
                print("❌ Budget must be greater than 0")
                continue
            user_form_data['budget'] = budget
            break
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Sector preference
    print("\n🏢 Available sectors:")
    sectors = ["Banking", "Technology", "Energy", "Healthcare", "Consumer Goods", 
               "Real Estate", "Manufacturing", "Telecommunications", "Transportation", "Utilities", "Any"]
    for i, sector in enumerate(sectors, 1):
        print(f"   {i}. {sector}")
    
    while True:
        try:
            sector_choice = input(f"🏢 Choose sector (1-{len(sectors)}) or enter sector name: ").strip()
            if sector_choice.isdigit():
                choice = int(sector_choice) - 1
                if 0 <= choice < len(sectors):
                    user_form_data['sector_preference'] = sectors[choice]
                    break
            elif sector_choice in sectors:
                user_form_data['sector_preference'] = sector_choice
                break
            else:
                print("❌ Invalid choice. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Risk tolerance
    print("\n⚠️ Risk tolerance levels:")
    risk_levels = ["low", "moderate", "high"]
    for i, risk in enumerate(risk_levels, 1):
        print(f"   {i}. {risk.capitalize()}")
    
    while True:
        try:
            risk_choice = input(f"⚠️ Choose risk tolerance (1-{len(risk_levels)}) or enter risk level: ").strip().lower()
            if risk_choice.isdigit():
                choice = int(risk_choice) - 1
                if 0 <= choice < len(risk_levels):
                    user_form_data['risk_tolerance'] = risk_levels[choice]
                    break
            elif risk_choice in risk_levels:
                user_form_data['risk_tolerance'] = risk_choice
                break
            else:
                print("❌ Invalid choice. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Time horizon
    print("\n⏰ Time horizon:")
    horizons = ["short", "medium", "long"]
    for i, horizon in enumerate(horizons, 1):
        print(f"   {i}. {horizon.capitalize()}")
    
    while True:
        try:
            horizon_choice = input(f"⏰ Choose time horizon (1-{len(horizons)}) or enter horizon: ").strip().lower()
            if horizon_choice.isdigit():
                choice = int(horizon_choice) - 1
                if 0 <= choice < len(horizons):
                    user_form_data['time_horizon'] = horizons[choice]
                    break
            elif horizon_choice in horizons:
                user_form_data['time_horizon'] = horizon_choice
                break
            else:
                print("❌ Invalid choice. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Target profit
    while True:
        try:
            profit_input = input("🎯 Enter target profit percentage (0-100): ").strip()
            target_profit = float(profit_input) if profit_input else 15
            if 0 <= target_profit <= 100:
                user_form_data['target_profit'] = target_profit
                break
            else:
                print("❌ Target profit must be between 0 and 100")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Investment goal
    print("\n📈 Investment goals:")
    goals = ["growth", "income", "balanced", "conservative"]
    for i, goal in enumerate(goals, 1):
        print(f"   {i}. {goal.capitalize()}")
    
    while True:
        try:
            goal_choice = input(f"📈 Choose investment goal (1-{len(goals)}) or enter goal: ").strip().lower()
            if goal_choice.isdigit():
                choice = int(goal_choice) - 1
                if 0 <= choice < len(goals):
                    user_form_data['investment_goal'] = goals[choice]
                    break
            elif goal_choice in goals:
                user_form_data['investment_goal'] = goal_choice
                break
            else:
                print("❌ Invalid choice. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Chat message
    chat_message = input("💬 Enter additional message (optional): ").strip()
    if chat_message:
        user_form_data['chat_message'] = chat_message
    else:
        # Generate a default message based on inputs
        user_form_data['chat_message'] = f"I want to invest {user_form_data['budget']:,} PKR in {user_form_data['sector_preference']} sector with {user_form_data['risk_tolerance']} risk tolerance for {user_form_data['time_horizon']} term targeting {user_form_data['target_profit']}% profit."
    
    print("\n" + "=" * 60)
    print("📊 Your Investment Profile:")
    print("=" * 60)
    print(json.dumps(user_form_data, indent=2))
    print(f"💬 Chat Message: {user_form_data['chat_message']}")
    print(f"👤 User ID: {user_form_data['user_id']}")
    print("\n🔄 Processing input through agentic framework...")
    
    # Process the input
    result = await input_taker_agent.process_user_input(user_form_data)
    
    print("\n" + "=" * 60)
    print("📋 PROCESSING RESULTS")
    print("=" * 60)
    
    if result['success']:
        print("✅ Status: SUCCESS")
        print(f"👤 User: {result['user_profile']['user_id']}")
        print(f"💰 Budget: {result['user_profile']['budget']:,} PKR")
        print(f"🏢 Sector: {result['user_profile']['sector_preference']}")
        print(f"⚠️ Risk: {result['user_profile']['risk_tolerance']}")
        print(f"⏰ Horizon: {result['user_profile']['time_horizon']}")
        print(f"🎯 Target: {result['user_profile']['target_profit']}%")
        print(f"📈 Goal: {result['user_profile']['investment_goal']}")
        
        # Show analysis results
        analysis = result.get('analysis_results', {})
        if analysis:
            recommendations = analysis.get('recommendations', [])
            stock_analysis = analysis.get('stock_analysis', [])
            news_analysis = analysis.get('news_analysis', {})
            risk_profile = analysis.get('risk_profile', {})
            portfolio_update = analysis.get('portfolio_update', {})
            
            print(f"\n📊 Analysis Summary:")
            print(f"   - Recommendations: {len(recommendations)}")
            print(f"   - Stock Analysis: {len(stock_analysis)} stocks analyzed")
            print(f"   - News Analysis: {len(news_analysis)} companies with news")
            
            # Show risk profile
            if risk_profile:
                print(f"   - Risk Profile: {risk_profile.get('risk_level', 'Unknown')} risk tolerance")
                print(f"     Investment Style: {risk_profile.get('investment_style', 'Unknown')}")
                print(f"     Risk Score: {risk_profile.get('risk_score', 0):.2f}")
            
            # Show portfolio update
            if portfolio_update:
                print(f"   - Portfolio Status: {portfolio_update.get('status', 'Unknown')}")
                print(f"     Total Value: PKR {portfolio_update.get('total_value', 0):,.2f}")
                print(f"     Cash Balance: PKR {portfolio_update.get('cash_balance', 0):,.2f}")
            
            # Show top performing stocks
            if stock_analysis:
                print(f"\n🏆 Top Performing Stocks:")
                for i, stock in enumerate(stock_analysis[:3], 1):
                    print(f"   {i}. {stock.get('stock_code', 'Unknown')} - {stock.get('stock_name', 'Unknown')}")
                    print(f"      Performance Score: {stock.get('performance_score', 0):.2f}")
                    print(f"      Rank: {stock.get('rank', 0)}/{stock.get('rank_description', 'Unknown')}")
                    print(f"      Change: {stock.get('change_percent', 0):+.2f}%")
            
            if recommendations:
                print(f"\n📈 Top Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"\n   {i}. {rec.get('stock_code', 'Unknown')} - {rec.get('stock_name', 'Unknown')}")
                    print(f"      🏢 Sector: {rec.get('sector', 'Unknown')}")
                    print(f"      📊 Recommendation: {rec.get('recommendation_type', 'Unknown').upper()}")
                    print(f"      🎯 Confidence: {rec.get('confidence_score', 0):.2%}")
                    print(f"      💰 Expected Return: {rec.get('expected_return', 0):.2f}%")
                    print(f"      ⚠️ Risk Level: {rec.get('risk_level', 'Unknown')}")
                    
                    # Show reasoning summary
                    reasoning = rec.get('reasoning_summary', '')
                    if reasoning:
                        print(f"      📝 Reasoning: {reasoning[:120]}...")
                    
                    # Show key factors
                    key_factors = rec.get('key_factors', [])
                    if key_factors:
                        print(f"      🔑 Key Factors:")
                        for factor in key_factors[:3]:
                            print(f"         • {factor}")
                    
                    # Show risk factors
                    risk_factors = rec.get('risk_factors', [])
                    if risk_factors:
                        print(f"      ⚠️ Risk Factors:")
                        for risk in risk_factors[:2]:
                            print(f"         • {risk}")
                    
                    # Show technical analysis details
                    technical = rec.get('technical_analysis', {})
                    if technical:
                        print(f"      📊 Technical Analysis:")
                        print(f"         - Current Price: PKR {technical.get('current_price', 0):,.2f}")
                        print(f"         - Change: {technical.get('change_percent', 0):+.2f}%")
                        print(f"         - RSI: {technical.get('rsi', 0):.1f}")
                        print(f"         - Performance Score: {technical.get('performance_score', 0):.2f}")
                        print(f"         - Rank: {technical.get('rank', 0)}/{technical.get('rank_description', 'Unknown')}")
                        
                        # Show trend and momentum
                        if 'price_trend' in technical:
                            print(f"         - Trend: {technical.get('price_trend', 'Unknown')}")
                        if 'momentum' in technical:
                            print(f"         - Momentum: {technical.get('momentum', 0):.1f}")
                        if 'volatility' in technical:
                            print(f"         - Volatility: {technical.get('volatility', 0):.1f}")
                    
                    # Show news sentiment details
                    news_sentiment = rec.get('news_sentiment', {})
                    if news_sentiment:
                        print(f"      📰 News Sentiment:")
                        if isinstance(news_sentiment, dict):
                            print(f"         - Sentiment: {news_sentiment.get('overall_sentiment', 'Unknown')}")
                            # Handle sentiment_score that might be string or float
                            sentiment_score = news_sentiment.get('sentiment_score', 0)
                            if isinstance(sentiment_score, str):
                                try:
                                    sentiment_score = float(sentiment_score)
                                except (ValueError, TypeError):
                                    sentiment_score = 0.0
                            print(f"         - Score: {sentiment_score:.2f}")
                            print(f"         - Articles Analyzed: {news_sentiment.get('news_count', 0)}")
                            if 'key_events' in news_sentiment and news_sentiment['key_events']:
                                print(f"         - Key Events: {len(news_sentiment['key_events'])} identified")
                            if 'risk_factors' in news_sentiment and news_sentiment['risk_factors']:
                                print(f"         - Risk Factors: {len(news_sentiment['risk_factors'])} identified")
                        else:
                            # Handle non-dict news sentiment (should be properly serialized now)
                            sentiment_summary = f"Sentiment data available ({type(news_sentiment).__name__})"
                            print(f"         - {sentiment_summary}")
                    
                    print(f"      {'─' * 50}")
    else:
        print("❌ Status: ERROR")
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Message: {result.get('message', 'No message')}")
    
    print("=" * 60)
    print("🎉 Input processing completed!")
    print("=" * 60)

if __name__ == "__main__":
    # Run the terminal interface
    asyncio.run(terminal_input_interface()) 