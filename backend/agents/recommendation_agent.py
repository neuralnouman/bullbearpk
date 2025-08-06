#!/usr/bin/env python3
"""
Recommendation Agent for BullBearPK
===================================

This agent is responsible for:
1. Taking output from the agentic framework
2. Generating comprehensive recommendations
3. Saving recommendations to database
4. Providing detailed recommendation display
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from database_config import db_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationAgent:
    """
    Dedicated recommendation agent for generating and storing investment recommendations
    """
    
    def __init__(self):
        self.agent_name = "RecommendationAgent"
        self.version = "v1.0"
    
    async def generate_recommendations(self, 
                                     stock_analysis: List[Dict], 
                                     news_analysis: Dict,
                                     risk_profile: Dict,
                                     user_input: Dict,
                                     user_id: str = "default_user") -> Dict:
        """
        Generate comprehensive recommendations from agentic framework output
        """
        try:
            logger.info(f"Starting recommendation generation for user {user_id}")
            
            # Clear previous recommendations
            try:
                db_config.clear_recommendations()
                logger.info("Cleared previous recommendations")
            except Exception as e:
                logger.warning(f"Error clearing previous recommendations: {e}")
            
            recommendations = []
            
            # Process top 5 stocks from analysis
            for analysis in stock_analysis[:5]:
                stock_code = analysis.get('stock_code', '')
                
                # Get news sentiment for this stock
                news_sentiment = news_analysis.get(stock_code, {})
                
                # Calculate recommendation score
                technical_score = analysis.get('confidence_score', 0.5)
                
                # Handle different news sentiment data types
                if hasattr(news_sentiment, 'sentiment_score'):
                    sentiment_score = float(news_sentiment.sentiment_score)
                elif isinstance(news_sentiment, dict):
                    sentiment_score = float(news_sentiment.get('sentiment_score', 0.5))
                else:
                    sentiment_score = 0.5
                
                # Calculate risk-adjusted score
                risk_adjusted_score = technical_score * 0.6 + sentiment_score * 0.4
                
                # Determine recommendation type based on score
                if risk_adjusted_score > 0.8:
                    recommendation_type = 'strong_buy'
                elif risk_adjusted_score > 0.6:
                    recommendation_type = 'buy'
                elif risk_adjusted_score > 0.4:
                    recommendation_type = 'hold'
                else:
                    recommendation_type = 'sell'
                
                # Calculate expected return
                expected_return = analysis.get('momentum', 0) * 100
                
                # Determine risk level
                risk_level = 'high' if risk_adjusted_score < 0.4 else 'medium' if risk_adjusted_score < 0.7 else 'low'
                
                # Create comprehensive reasoning
                reasoning_summary = f"Stock {stock_code} shows {technical_score:.1f} technical score with {sentiment_score:.1f} sentiment score. "
                reasoning_summary += f"Combined risk-adjusted score: {risk_adjusted_score:.1f}. "
                reasoning_summary += f"Recommendation: {recommendation_type.upper()} with {risk_adjusted_score:.1%} confidence. "
                reasoning_summary += f"Expected return: {expected_return:.1f}% with {risk_level} risk level."
                
                # Serialize news sentiment for display
                serialized_news_sentiment = self._serialize_news_sentiment(news_sentiment)
                
                # Extract technical analysis data properly to match frontend interface
                technical_analysis = {
                    'stock_code': stock_code,
                    'stock_name': analysis.get('stock_name', ''),
                    'sector': analysis.get('sector', ''),
                    'current_price': analysis.get('current_price', 0),
                    'rsi': analysis.get('rsi', 0),
                    'momentum': analysis.get('momentum', 0),
                    'price_trend': analysis.get('trend', 'neutral'),
                    'volatility': analysis.get('volatility', 0),
                    'confidence_score': technical_score,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'macd': {
                        'macd': analysis.get('technical_analysis', {}).get('macd', 0),
                        'signal': 0,
                        'histogram': 0
                    },
                    'bollinger_bands': {
                        'upper': analysis.get('technical_analysis', {}).get('resistance_level', 0),
                        'middle': analysis.get('current_price', 0),
                        'lower': analysis.get('technical_analysis', {}).get('support_level', 0)
                    },
                    'support_resistance': {
                        'support': analysis.get('technical_analysis', {}).get('support_level', 0),
                        'resistance': analysis.get('technical_analysis', {}).get('resistance_level', 0)
                    }
                }
                
                recommendation = {
                    'stock_code': stock_code,
                    'stock_name': analysis.get('stock_name', ''),
                    'sector': analysis.get('sector', ''),
                    'recommendation_type': recommendation_type,
                    'confidence_score': risk_adjusted_score,
                    'expected_return': expected_return,
                    'risk_level': risk_level,
                    'allocation_percent': 20.0,  # Default allocation
                    'technical_analysis': technical_analysis,
                    'news_sentiment': serialized_news_sentiment,
                    'fundamental_analysis': analysis.get('fundamental_analysis', {}),
                    'reasoning': reasoning_summary,
                    'key_factors': [
                        f"Technical Score: {technical_score:.1f}",
                        f"Sentiment Score: {sentiment_score:.1f}",
                        f"Risk-Adjusted Score: {risk_adjusted_score:.1f}",
                        f"Risk Level: {risk_level}",
                        f"Expected Return: {expected_return:.1f}%"
                    ],
                    'risk_factors': [
                        "Market volatility and economic conditions",
                        "Sector-specific risks and regulatory changes",
                        "Company-specific operational risks",
                        "Liquidity and trading volume risks"
                    ]
                }
                
                recommendations.append(recommendation)
            
            # Sort by confidence score
            recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            # Save recommendations to database using centralized db_config method
            if recommendations:
                try:
                    success = db_config.save_recommendations_batch(recommendations, user_id, user_input)
                    if success:
                        logger.info(f"Successfully saved {len(recommendations)} recommendations to database")
                    else:
                        logger.error("Failed to save recommendations to database")
                except Exception as e:
                    logger.error(f"Error saving recommendations: {e}")
            
            return {
                'success': True,
                'recommendations': recommendations,
                'total_generated': len(recommendations),
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': [],
                'total_generated': 0
            }
    

    
    def get_user_recommendations(self, user_id: str) -> List[Dict]:
        """
        Get recommendations for a specific user from database
        """
        try:
            query = """
                SELECT * FROM recommendations 
                WHERE user_id = %s AND is_active = TRUE 
                ORDER BY created_at DESC
            """
            results = db_config.execute_query(query, (user_id,))
            return results or []
        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            return []

    def _serialize_news_sentiment(self, news_sentiment) -> Dict:
        """Properly serialize NewsAnalysisResult dataclass to dictionary for display"""
        try:
            if hasattr(news_sentiment, '__dict__'):
                # Convert dataclass to dictionary
                news_sentiment_dict = {}
                for key, value in news_sentiment.__dict__.items():
                    if hasattr(value, 'isoformat'):  # datetime objects
                        news_sentiment_dict[key] = value.isoformat()
                    elif isinstance(value, (list, dict)):
                        news_sentiment_dict[key] = value
                    elif key == 'sentiment_score':
                        # Ensure sentiment_score is always a float
                        try:
                            news_sentiment_dict[key] = float(value) if value is not None else 0.0
                        except (ValueError, TypeError):
                            news_sentiment_dict[key] = 0.0
                    else:
                        news_sentiment_dict[key] = str(value) if value is not None else ''
                return news_sentiment_dict
            elif isinstance(news_sentiment, dict):
                # Already a dictionary, just ensure datetime objects are serialized
                serialized_dict = {}
                for key, value in news_sentiment.items():
                    if hasattr(value, 'isoformat'):  # datetime objects
                        serialized_dict[key] = value.isoformat()
                    elif key == 'sentiment_score':
                        # Ensure sentiment_score is always a float
                        try:
                            serialized_dict[key] = float(value) if value is not None else 0.0
                        except (ValueError, TypeError):
                            serialized_dict[key] = 0.0
                    else:
                        serialized_dict[key] = value
                return serialized_dict
            else:
                # Fallback for other types
                return {
                    'sentiment_data': str(news_sentiment),
                    'overall_sentiment': 'neutral',
                    'sentiment_score': 0.0,
                    'news_count': 0
                }
        except Exception as e:
            logger.error(f"Error serializing news sentiment: {e}")
            return {
                'error': 'Failed to serialize news sentiment data',
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'news_count': 0
            }

# Global recommendation agent instance
recommendation_agent = RecommendationAgent() 