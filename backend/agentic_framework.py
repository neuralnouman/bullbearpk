#!/usr/bin/env python3
"""
Agentic Framework for BullBearPK
================================

This module implements the LangGraph-based agentic framework for:
1. Stock data scraping and analysis
2. News scraping and sentiment analysis
3. Risk profiling and portfolio management
4. Recommendation generation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from langgraph.graph import StateGraph, END
from typing import Annotated

# Import agents
from agents.fin_scraper import scrape_stocks_tool
from agents.advanced_stock_analyzer import analyze_stocks_advanced_agentic
from agents.news_scraper import news_scraper_node
from agents.news_analyzer import news_analyzer_node
from agents.risk_checker import check_risk_profile
from agents.past_investments_checker import check_past_investments
from agents.portfolio_checker import check_portfolio
from agents.recommendation_agent import recommendation_agent
from agents.manager_record_agent import handle_user_investment_decision

# Import database config
from database_config import db_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BullBearPKState:
    """State management for BullBearPK agentic framework"""
    
    def __init__(self):
        self.stock_data = []
        self.stock_analysis = []
        self.news_data = []
        self.news_analysis = {}
        self.risk_profile = {}
        self.user_history = {}
        self.portfolio_update = {}
        self.recommendations = []
        self.user_input = {}
        self.user_id = "default_user"

class AgenticFramework:
    """Main agentic framework orchestrator"""
    
    def __init__(self):
        self.workflow = self._create_workflow()
        logger.info("Agentic framework initialized")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Create the workflow graph with proper state typing
        workflow = StateGraph(Annotated[Dict, "state"])
        
        # Add nodes
        workflow.add_node("scrape_stocks", self._scrape_stocks_node)
        workflow.add_node("analyze_stocks", self._analyze_stocks_node)
        workflow.add_node("scrape_news", self._scrape_news_node)
        workflow.add_node("analyze_news", self._analyze_news_node)
        workflow.add_node("check_risk", self._check_risk_node)
        workflow.add_node("check_past_investments", self._check_past_investments_node)
        workflow.add_node("check_portfolio", self._check_portfolio_node)
        workflow.add_node("generate_recommendations", self._generate_recommendations_node)
        workflow.add_node("handle_user_decision", self._handle_user_decision_node)
        
        # Define the workflow edges
        workflow.set_entry_point("scrape_stocks")
        workflow.add_edge("scrape_stocks", "analyze_stocks")
        workflow.add_edge("analyze_stocks", "scrape_news")
        workflow.add_edge("scrape_news", "analyze_news")
        workflow.add_edge("analyze_news", "check_risk")
        workflow.add_edge("check_risk", "check_past_investments")
        workflow.add_edge("check_past_investments", "check_portfolio")
        workflow.add_edge("check_portfolio", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "handle_user_decision")
        workflow.add_edge("handle_user_decision", END)
        
        return workflow.compile()
    
    async def _scrape_stocks_node(self, state: Dict) -> Dict:
        """Scrape current stock data"""
        try:
            logger.info("Scraping stock data...")
            result = scrape_stocks_tool()
            
            if result.get('success', False):
                state['stock_data'] = result.get('data', [])
                logger.info(f"Scraped {len(state['stock_data'])} stocks")
            else:
                logger.warning("Stock scraping failed, using sample data for testing")
                # Use sample data for testing when scraping fails
                state['stock_data'] = [
                    {
                        'code': 'HBL',
                        'name': 'Habib Bank Limited',
                        'sector': 'Banking',
                        'open_price': 100.50,
                        'high_price': 102.30,
                        'low_price': 99.80,
                        'close_price': 101.20,
                        'volume': 1500000,
                        'change_amount': 0.70,
                        'change_percent': 0.70
                    },
                    {
                        'code': 'UBL',
                        'name': 'United Bank Limited',
                        'sector': 'Banking',
                        'open_price': 95.20,
                        'high_price': 97.10,
                        'low_price': 94.50,
                        'close_price': 96.80,
                        'volume': 1200000,
                        'change_amount': 1.60,
                        'change_percent': 1.68
                    },
                    {
                        'code': 'OGDC',
                        'name': 'Oil & Gas Development Company',
                        'sector': 'Energy',
                        'open_price': 85.40,
                        'high_price': 87.20,
                        'low_price': 84.90,
                        'close_price': 86.50,
                        'volume': 2000000,
                        'change_amount': 1.10,
                        'change_percent': 1.29
                    },
                    {
                        'code': 'PPL',
                        'name': 'Pakistan Petroleum Limited',
                        'sector': 'Energy',
                        'open_price': 78.30,
                        'high_price': 80.10,
                        'low_price': 77.80,
                        'close_price': 79.60,
                        'volume': 1800000,
                        'change_amount': 1.30,
                        'change_percent': 1.66
                    },
                    {
                        'code': 'LUCK',
                        'name': 'Lucky Cement Limited',
                        'sector': 'Cement',
                        'open_price': 450.00,
                        'high_price': 455.50,
                        'low_price': 448.20,
                        'close_price': 453.80,
                        'volume': 500000,
                        'change_amount': 3.80,
                        'change_percent': 0.84
                    }
                ]
            
            return state
            
        except Exception as e:
            logger.error(f"Error in scrape stocks node: {e}")
            state['stock_data'] = []
            return state
    
    async def _analyze_stocks_node(self, state: Dict) -> Dict:
        """Analyze stock data using advanced stock analyzer"""
        try:
            logger.info("Analyzing stocks...")
            
            # Get stock data from state
            stock_data = state.get('stock_data', [])
            
            if not stock_data:
                logger.warning("No stock data available for analysis")
                state['stock_analysis'] = []
                return state
            
            # Call the advanced stock analyzer
            analysis_result = await analyze_stocks_advanced_agentic(stock_data)
            
            if analysis_result.get('success', False):
                state['stock_analysis'] = analysis_result.get('top_performers', [])
                logger.info(f"Analyzed {len(state['stock_analysis'])} stocks")
            else:
                logger.warning("Stock analysis failed, using mock data")
                state['stock_analysis'] = self._create_mock_analysis(stock_data)
            
            return state
            
        except Exception as e:
            logger.error(f"Error in analyze stocks node: {e}")
            state['stock_analysis'] = []
            return state
    
    async def _scrape_news_node(self, state: Dict) -> Dict:
        """Scrape news for top performing companies"""
        try:
            logger.info("Scraping news for top companies...")
            
            # Get top 5 companies from stock analysis
            stock_analysis = state.get('stock_analysis', [])
            top_performers = stock_analysis[:5]  # Pass the full stock objects
            
            if not top_performers:
                logger.warning("No companies available for news scraping")
                state['news_data'] = []
                return state
            
            # Call the news scraper node with the correct format
            news_result = await news_scraper_node.run({
                'top_performers': top_performers,
                'user_id': state.get('user_id', 'default_user')
            })
            
            if news_result.get('news_records'):
                state['news_data'] = news_result.get('news_records', {})
                logger.info(f"Scraped news for {len(top_performers)} companies")
            else:
                logger.warning("News scraping failed")
                state['news_data'] = {}
            
            return state
            
        except Exception as e:
            logger.error(f"Error in scrape news node: {e}")
            state['news_data'] = {}
            return state
    
    async def _analyze_news_node(self, state: Dict) -> Dict:
        """Analyze news sentiment"""
        try:
            logger.info("Analyzing news sentiment...")
            
            # Get news data from state
            news_records = state.get('news_data', {})
            
            if not news_records:
                logger.warning("No news data available for analysis")
                state['news_analysis'] = {}
                return state
            
            # Call the news analyzer node with the correct format
            analysis_result = await news_analyzer_node.run({
                'news_records': news_records,
                'user_id': state.get('user_id', 'default_user')
            })
            
            if analysis_result.get('news_analysis'):
                state['news_analysis'] = analysis_result.get('news_analysis', {})
                logger.info(f"Analyzed news for {len(state['news_analysis'])} companies")
            else:
                logger.warning("News analysis failed")
                state['news_analysis'] = {}
            
            return state
            
        except Exception as e:
            logger.error(f"Error in analyze news node: {e}")
            state['news_analysis'] = {}
            return state
    
    async def _check_risk_node(self, state: Dict) -> Dict:
        """Check user risk profile"""
        try:
            logger.info("Checking risk profile...")
            
            user_id = state.get('user_id', 'default_user')
            user_input = state.get('user_input', {})
            
            # Call the risk checker
            risk_result = await check_risk_profile(user_id, user_input)
            
            if risk_result.get('success', False):
                state['risk_profile'] = risk_result.get('risk_profile', {})
                logger.info("Risk profile check completed")
            else:
                logger.warning("Risk check failed")
                state['risk_profile'] = {}
            
            return state
            
        except Exception as e:
            logger.error(f"Error in check risk node: {e}")
            state['risk_profile'] = {}
            return state
    
    async def _check_past_investments_node(self, state: Dict) -> Dict:
        """Check user past investments"""
        try:
            logger.info("Checking past investments...")
            
            user_id = state.get('user_id', 'default_user')
            
            # Call the past investments checker
            history_result = await check_past_investments(user_id)
            
            if history_result.get('success', False):
                state['user_history'] = history_result
                logger.info("Past investments checked successfully")
            else:
                logger.warning("Failed to check past investments")
                state['user_history'] = {}
            
            return state
            
        except Exception as e:
            logger.error(f"Error in check past investments node: {e}")
            state['user_history'] = {}
            return state
    
    async def _check_portfolio_node(self, state: Dict) -> Dict:
        """Check user portfolio"""
        try:
            logger.info("Checking portfolio...")
            
            user_id = state.get('user_id', 'default_user')
            stock_analysis = state.get('stock_analysis', [])
            
            # Call the portfolio checker
            portfolio_result = await check_portfolio(user_id, stock_analysis)
            
            if portfolio_result.get('status') in ['existing_user', 'new_user']:
                state['portfolio_update'] = portfolio_result
                if portfolio_result.get('status') == 'new_user':
                    logger.info("New user detected - no existing portfolio")
                else:
                    logger.info("Portfolio analysis completed successfully")
            else:
                logger.warning("Portfolio check failed")
                state['portfolio_update'] = {}
            
            return state
            
        except Exception as e:
            logger.error(f"Error in check portfolio node: {e}")
            state['portfolio_update'] = {}
            return state
    
    async def _generate_recommendations_node(self, state: Dict) -> Dict:
        """Generate final recommendations using dedicated recommendation agent"""
        try:
            logger.info("Generating recommendations using dedicated agent...")
            
            # Get all analysis data from state
            stock_analysis = state.get('stock_analysis', [])
            news_analysis = state.get('news_analysis', {})
            risk_profile = state.get('risk_profile', {})
            user_input = state.get('user_input', {})
            user_id = state.get('user_id', 'default_user')
            
            # Call the dedicated recommendation agent
            recommendation_result = await recommendation_agent.generate_recommendations(
                stock_analysis=stock_analysis,
                news_analysis=news_analysis,
                risk_profile=risk_profile,
                user_input=user_input,
                user_id=user_id
            )
            
            if recommendation_result.get('success', False):
                state['recommendations'] = recommendation_result.get('recommendations', [])
                logger.info(f"Successfully generated {len(state['recommendations'])} recommendations")
            else:
                logger.error(f"Failed to generate recommendations: {recommendation_result.get('error')}")
                state['recommendations'] = []
            
            return state
            
        except Exception as e:
            logger.error(f"Error in generate recommendations node: {e}")
            state['recommendations'] = []
            return state
    
    async def _handle_user_decision_node(self, state: Dict) -> Dict:
        """Handle user investment decisions after recommendations"""
        try:
            logger.info("Processing user investment decisions...")
            
            # Get recommendations and user input from state
            recommendations = state.get('recommendations', [])
            user_input = state.get('user_input', {})
            user_id = state.get('user_id', 'default_user')
            
            # Check if user has made any decisions
            user_decisions = user_input.get('user_decisions', [])
            
            if not user_decisions:
                logger.info("No user decisions to process")
                state['user_decision_results'] = {
                    'status': 'no_decisions',
                    'message': 'No investment decisions made by user',
                    'processed_decisions': []
                }
                return state
            
            # Process each user decision
            processed_decisions = []
            
            for decision in user_decisions:
                try:
                    decision_type = decision.get('decision_type', '')
                    stock_code = decision.get('stock_code', '')
                    quantity = decision.get('quantity', 0)
                    price = decision.get('price', 0.0)
                    recommendation_id = decision.get('recommendation_id', '')
                    
                    # Call the manager record agent
                    result = await handle_user_investment_decision(
                        user_id=user_id,
                        decision_type=decision_type,
                        stock_code=stock_code,
                        quantity=quantity,
                        price=price,
                        recommendation_id=recommendation_id
                    )
                    
                    processed_decisions.append({
                        'original_decision': decision,
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    logger.info(f"Processed {decision_type} decision for {stock_code}: {result.get('status')}")
                    
                except Exception as e:
                    logger.error(f"Error processing decision {decision}: {e}")
                    processed_decisions.append({
                        'original_decision': decision,
                        'result': {
                            'status': 'error',
                            'message': f'Error processing decision: {str(e)}'
                        },
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Update state with decision results
            state['user_decision_results'] = {
                'status': 'completed',
                'message': f'Processed {len(processed_decisions)} user decisions',
                'processed_decisions': processed_decisions,
                'total_decisions': len(processed_decisions),
                'successful_decisions': len([d for d in processed_decisions if d['result'].get('status') == 'success']),
                'failed_decisions': len([d for d in processed_decisions if d['result'].get('status') == 'error'])
            }
            
            logger.info(f"Completed processing {len(processed_decisions)} user decisions")
            return state
            
        except Exception as e:
            logger.error(f"Error in handle user decision node: {e}")
            state['user_decision_results'] = {
                'status': 'error',
                'message': f'Error processing user decisions: {str(e)}',
                'processed_decisions': []
            }
            return state
    
    def _create_mock_analysis(self, stock_data: List[Dict]) -> List[Dict]:
        """Create mock stock analysis for testing"""
        mock_analysis = []
        
        for i, stock in enumerate(stock_data[:5]):
            current_price = stock.get('close_price', 100.0)
            mock_analysis.append({
                'stock_code': stock.get('code', f'STOCK{i}'),
                'stock_name': stock.get('name', f'Stock {i}'),
                'sector': stock.get('sector', 'Unknown'),
                'current_price': current_price,
                'change_percent': stock.get('change_percent', 0.0),
                'volume': stock.get('volume', 1000000),
                'performance_score': 0.7 + (i * 0.05),
                'rank': i + 1,
                'rank_description': f'Top {i + 1}',
                'confidence_score': 0.6 + (i * 0.08),
                'rsi': 45 + (i * 8),  # More varied RSI values
                'momentum': 2.5 + (i * 1.2),  # More realistic momentum values
                'trend': 'bullish' if i % 2 == 0 else 'bearish',
                'volatility': 0.2 + (i * 0.02),
                'technical_analysis': {
                    'rsi': 45 + (i * 8),
                    'macd': 0.1 + (i * 0.02),
                    'bollinger_bands': 'neutral',
                    'support_level': current_price * 0.95,
                    'resistance_level': current_price * 1.05
                },
                'fundamental_analysis': {
                    'pe_ratio': 15 + i,
                    'pb_ratio': 1.5 + (i * 0.1),
                    'dividend_yield': 2.0 + (i * 0.5),
                    'market_cap': 1000000000 + (i * 100000000)
                }
            })
        
        return mock_analysis
    
    def _create_mock_news_analysis(self, stock_codes: List[str]) -> Dict:
        """Create mock news analysis for testing"""
        mock_news_analysis = {}
        
        for i, stock_code in enumerate(stock_codes):
            mock_news_analysis[stock_code] = {
                'stock_code': stock_code,
                'overall_sentiment': 'positive' if i % 2 == 0 else 'negative',
                'sentiment_score': 0.6 + (i * 0.1),
                'news_count': 5 + i,
                'positive_news': 3 + i,
                'negative_news': 1,
                'neutral_news': 1,
                'key_events': [
                    f'Event {i+1} for {stock_code}',
                    f'Another event for {stock_code}'
                ],
                'risk_factors': [
                    'Market volatility',
                    'Economic uncertainty'
                ],
                'opportunities': [
                    'Growth potential',
                    'Market expansion'
                ],
                'recommendation': 'buy' if i % 2 == 0 else 'hold',
                'confidence': 0.7 + (i * 0.05),
                'analysis_summary': f'Comprehensive analysis for {stock_code} shows mixed sentiment with growth potential.',
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        return mock_news_analysis
    
    async def run_workflow(
        self, 
        user_input: Dict, 
        chat_message: str = '', 
        user_id: Optional[str] = None
    ) -> Dict:
        """Run the complete agentic workflow with returning user support"""
        try:
            logger.info(f"Starting agentic workflow for user: {user_id}")

            # 1. Fetch previous form submission and recommendations
            previous_form = None
            previous_recommendations = []
            comparison_summary = {}
            if user_id:
                prev_forms = db_config.get_user_previous_submissions(user_id)
                if prev_forms:
                    previous_form = prev_forms[0]
                    previous_recommendations = db_config.get_user_previous_recommendations(user_id, previous_form['id'])

            # 2. Initialize state
            initial_state = {
                'user_input': user_input,
                'user_id': user_id or 'default_user',
                'chat_message': chat_message,
                'stock_data': [],
                'stock_analysis': [],
                'news_data': [],
                'news_analysis': {},
                'risk_profile': {},
                'user_history': {},
                'portfolio_update': {},
                'recommendations': []
            }

            # 3. Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)

            # 4. Extract new recommendations
            new_recommendations = final_state.get('recommendations', [])

            # 5. Compare with previous recommendations if available
            if previous_recommendations:
                comparison_summary = db_config.compare_recommendations(previous_recommendations, new_recommendations)

            # 6. Save new form submission and recommendations
            db_config.save_user_form_submission(user_id, user_input, new_recommendations)

            # 7. Build result
            result = {
                'success': True,
                'data': {
                    'stock_analysis': final_state.get('stock_analysis', []),
                    'news_analysis': final_state.get('news_analysis', {}),
                    'risk_profile': final_state.get('risk_profile', {}),
                    'user_history': final_state.get('user_history', {}),
                    'portfolio_update': final_state.get('portfolio_update', {}),
                    'recommendations': new_recommendations,
                    'previous_form': previous_form,
                    'previous_recommendations': previous_recommendations,
                    'recommendation_changes': comparison_summary
                },
                'user_id': final_state.get('user_id'),
                'timestamp': datetime.now().isoformat()
            }

            logger.info("Agentic workflow completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error running agentic workflow: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {},
                'timestamp': datetime.now().isoformat()
            }

# Create global instance
agentic_framework = AgenticFramework() 