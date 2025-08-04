"""
Database Configuration for BullBearPK
====================================

MySQL database configuration and connection management.
"""

import mysql.connector
from mysql.connector import Error
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',
            'database': 'bullbearpk',
            'charset': 'utf8mb4',
            'autocommit': True,
            'pool_name': 'bullbearpk_pool',
            'pool_size': 10
        }
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**self.config)
            logger.info("Database connection pool initialized successfully")
        except Error as e:
            logger.error(f"Error initializing database pool: {e}")
            self.connection_pool = None
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        connection = None
        try:
            if self.connection_pool:
                connection = self.connection_pool.get_connection()
                yield connection
            else:
                # Fallback to direct connection
                connection = mysql.connector.connect(**self.config)
                yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("Database connection test successful")
                return True
        except Error as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """Execute a query and return results"""
        connection = None
        try:
            if self.connection_pool:
                connection = self.connection_pool.get_connection()
            else:
                connection = mysql.connector.connect(**self.config)
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                connection.commit()
                cursor.close()
                return None
        except Error as e:
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """Execute multiple queries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return True
        except Error as e:
            logger.error(f"Batch execution error: {e}")
            return False
    
    def insert_stock_data(self, stock_data: Dict[str, Any]) -> bool:
        """Insert stock data into database"""
        query = """
        INSERT INTO stocks (code, name, sector, open_price, high_price, low_price, 
                          close_price, volume, change_amount, change_percent, 
                          market_cap, pe_ratio, dividend_yield, scraped_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE
        open_price = VALUES(open_price),
        high_price = VALUES(high_price),
        low_price = VALUES(low_price),
        close_price = VALUES(close_price),
        volume = VALUES(volume),
        change_amount = VALUES(change_amount),
        change_percent = VALUES(change_percent),
        market_cap = VALUES(market_cap),
        pe_ratio = VALUES(pe_ratio),
        dividend_yield = VALUES(dividend_yield),
        scraped_at = CURRENT_TIMESTAMP
        """
        
        # Map the data fields correctly
        params = (
            stock_data.get('code'),
            stock_data.get('name'),
            stock_data.get('sector'),
            stock_data.get('open_price'),
            stock_data.get('high_price'),
            stock_data.get('low_price'),
            stock_data.get('close_price'),
            stock_data.get('volume'),
            stock_data.get('change'),  # Map 'change' to 'change_amount'
            stock_data.get('change_percent'),
            stock_data.get('market_cap', None),  # Default to None if not provided
            stock_data.get('pe_ratio', None),    # Default to None if not provided
            stock_data.get('dividend_yield', None)  # Default to None if not provided
        )
        
        try:
            self.execute_query(query, params)
            logger.info(f"Successfully inserted stock data for {stock_data.get('code')}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert stock data for {stock_data.get('code')}: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from database"""
        query = "SELECT * FROM users WHERE user_id = %s"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def get_latest_stocks(self, limit: int = 100) -> List[Dict]:
        """Get latest stock data"""
        query = """
        SELECT * FROM stocks 
        WHERE scraped_at = (SELECT MAX(scraped_at) FROM stocks)
        ORDER BY change_percent DESC 
        LIMIT %s
        """
        return self.execute_query(query, (limit,)) or []
    
    def save_stock_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """Save stock analysis results"""
        query = """
        INSERT INTO stock_analysis (
            stock_code, rsi, macd, macd_signal, macd_histogram,
            bollinger_upper, bollinger_lower, bollinger_middle,
            support_level, resistance_level, trend, momentum, volatility,
            confidence_score, recommendation, analysis_summary
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            analysis_data.get('stock_code'),
            analysis_data.get('rsi'),
            analysis_data.get('macd'),
            analysis_data.get('macd_signal'),
            analysis_data.get('macd_histogram'),
            analysis_data.get('bollinger_upper'),
            analysis_data.get('bollinger_lower'),
            analysis_data.get('bollinger_middle'),
            analysis_data.get('support_level'),
            analysis_data.get('resistance_level'),
            analysis_data.get('trend'),
            analysis_data.get('momentum'),
            analysis_data.get('volatility'),
            analysis_data.get('confidence_score'),
            analysis_data.get('recommendation'),
            analysis_data.get('analysis_summary')
        )
        
        return self.execute_query(query, params) is not None
    
    def save_news_analysis(self, news_data: Dict[str, Any]) -> bool:
        """Save news analysis results"""
        query = """
        INSERT INTO news_analysis (
            stock_code, overall_sentiment, sentiment_score, news_count,
            positive_news, negative_news, neutral_news, key_events,
            risk_factors, opportunities, recommendation, confidence, analysis_summary
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            news_data.get('stock_code'),
            news_data.get('overall_sentiment'),
            news_data.get('sentiment_score'),
            news_data.get('news_count'),
            news_data.get('positive_news'),
            news_data.get('negative_news'),
            news_data.get('neutral_news'),
            json.dumps(news_data.get('key_events', [])),
            json.dumps(news_data.get('risk_factors', [])),
            json.dumps(news_data.get('opportunities', [])),
            news_data.get('recommendation'),
            news_data.get('confidence'),
            news_data.get('analysis_summary')
        )
        
        return self.execute_query(query, params) is not None
    
    def save_recommendation(self, recommendation_data: Dict[str, Any]) -> bool:
        """Save user recommendation"""
        query = """
        INSERT INTO recommendations (
            user_id, stock_code, recommendation_type, confidence_score,
            allocation_percent, reasoning, risk_level, expected_return,
            time_horizon, expires_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            recommendation_data.get('user_id'),
            recommendation_data.get('stock_code'),
            recommendation_data.get('recommendation_type'),
            recommendation_data.get('confidence_score'),
            recommendation_data.get('allocation_percent'),
            recommendation_data.get('reasoning'),
            recommendation_data.get('risk_level'),
            recommendation_data.get('expected_return'),
            recommendation_data.get('time_horizon'),
            recommendation_data.get('expires_at')
        )
        
        return self.execute_query(query, params) is not None
    
    def get_user_investments(self, user_id: str) -> List[Dict]:
        """Get user investments"""
        query = """
        SELECT i.*, s.name as stock_name, s.sector 
        FROM investments i 
        JOIN stocks s ON i.stock_code = s.code 
        WHERE i.user_id = %s AND i.status = 'active'
        ORDER BY i.buy_date DESC
        """
        return self.execute_query(query, (user_id,)) or []
    
    def get_user_portfolio(self, user_id: str) -> Optional[Dict]:
        """Get user portfolio summary"""
        query = "SELECT * FROM portfolios WHERE user_id = %s"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None

    def save_top_performers_analysis(self, top_performers: List[Dict]) -> bool:
        """Save top performers analysis to database with advanced fields"""
        try:
            for stock in top_performers:
                technical_analysis = stock.get('technical_analysis', {})
                
                # Extract all advanced technical indicators
                rsi = technical_analysis.get('rsi', 50.0)
                stochastic_k = technical_analysis.get('stochastic_k', 50.0)
                stochastic_d = technical_analysis.get('stochastic_d', 50.0)
                williams_r = technical_analysis.get('williams_r', -50.0)
                cci = technical_analysis.get('cci', 0.0)
                roc = technical_analysis.get('roc', 0.0)
                atr = technical_analysis.get('atr', 0.0)
                
                # Moving averages
                ma_5 = technical_analysis.get('ma_5', 0.0)
                ma_10 = technical_analysis.get('ma_10', 0.0)
                ma_20 = technical_analysis.get('ma_20', 0.0)
                ma_50 = technical_analysis.get('ma_50', 0.0)
                ma_200 = technical_analysis.get('ma_200', 0.0)
                
                # MACD data
                macd_data = technical_analysis.get('macd', {})
                macd = macd_data.get('macd', 0.0)
                macd_signal = macd_data.get('signal', 0.0)
                macd_histogram = macd_data.get('histogram', 0.0)
                
                # Bollinger Bands
                bollinger_data = technical_analysis.get('bollinger_bands', {})
                bollinger_upper = bollinger_data.get('upper', 0.0)
                bollinger_lower = bollinger_data.get('lower', 0.0)
                bollinger_middle = bollinger_data.get('middle', 0.0)
                bb_position = bollinger_data.get('bb_position', 50.0)
                
                # Support and Resistance
                support_resistance = technical_analysis.get('support_resistance', {})
                support_level = support_resistance.get('support', 0.0)
                resistance_level = support_resistance.get('resistance', 0.0)
                support_distance = support_resistance.get('support_distance', 0.0)
                resistance_distance = support_resistance.get('resistance_distance', 0.0)
                
                # Trend analysis
                trend = technical_analysis.get('price_trend', 'sideways')
                trend_strength = technical_analysis.get('trend_strength', 0.0)
                trend_duration = technical_analysis.get('trend_duration', 0)
                momentum = technical_analysis.get('momentum', 0.0)
                volatility = technical_analysis.get('volatility', 0.0)
                
                # Volume analysis
                volume_analysis = technical_analysis.get('volume_analysis', {})
                volume_sma = volume_analysis.get('volume_sma', 0.0)
                volume_ratio = volume_analysis.get('volume_ratio', 1.0)
                volume_trend = volume_analysis.get('volume_trend', 'normal_volume')
                price_volume_trend = volume_analysis.get('price_volume_trend', 'neutral')
                
                # Advanced analytics
                advanced_analytics = technical_analysis.get('advanced_analytics', {})
                beta_coefficient = advanced_analytics.get('beta_coefficient', 1.0)
                sharpe_ratio = advanced_analytics.get('sharpe_ratio', 0.0)
                alpha_coefficient = advanced_analytics.get('alpha_coefficient', 0.0)
                information_ratio = advanced_analytics.get('information_ratio', 0.0)
                relative_strength_index = advanced_analytics.get('relative_strength_index', 50.0)
                
                # Risk metrics
                risk_metrics = technical_analysis.get('risk_metrics', {})
                value_at_risk = risk_metrics.get('value_at_risk', 0.0)
                maximum_drawdown = risk_metrics.get('maximum_drawdown', 0.0)
                downside_deviation = risk_metrics.get('downside_deviation', 0.0)
                
                # Performance metrics
                performance_score = stock.get('performance_score', 0.0)
                rank_position = stock.get('rank', 0)
                sector_performance_rank = stock.get('sector_rank', 0)
                
                # Basic price data
                current_price = float(stock.get('current_price', 0))
                open_price = float(stock.get('open_price', 0))
                high_price = float(stock.get('high_price', 0))
                low_price = float(stock.get('low_price', 0))
                volume = int(stock.get('volume', 0))
                change_amount = float(stock.get('change_amount', 0))
                change_percent = float(stock.get('change_percent', 0))
                
                # Calculate confidence score
                confidence_score = min(performance_score / 100.0, 0.95)
                
                # Determine recommendation
                recommendation = self._determine_advanced_recommendation(technical_analysis, performance_score)
                
                # Risk level
                risk_level = 'high' if value_at_risk > 20 else 'moderate' if value_at_risk > 10 else 'low'
                
                # Expected return and target prices
                expected_return = change_percent * 1.5
                target_price = current_price * (1 + expected_return / 100)
                stop_loss = current_price * (1 - abs(change_percent) / 100)
                
                # Create analysis summary
                analysis_summary = self._create_advanced_analysis_summary(stock, technical_analysis)
                
                # Key insights and factors
                key_insights = json.dumps({
                    'performance_rating': 'Excellent' if performance_score > 80 else 'Good' if performance_score > 60 else 'Average',
                    'technical_sentiment': 'Bullish' if rsi < 40 else 'Bearish' if rsi > 60 else 'Neutral',
                    'volume_analysis': 'High volume confirms move' if volume > 1000000 else 'Normal volume'
                })
                
                risk_factors = json.dumps([
                    "Overbought conditions" if rsi > 70 else "Oversold conditions" if rsi < 30 else "Normal conditions",
                    "High volatility" if volatility > 10 else "Normal volatility"
                ])
                
                opportunities = json.dumps([
                    "Strong momentum" if momentum > 5 else "Moderate momentum",
                    "Good volume support" if volume_ratio > 1.2 else "Normal volume"
                ])
                
                # FIXED: Corrected INSERT query with exactly 64 placeholders to match 64 columns
                query = """
                INSERT INTO stock_analysis (
                    stock_code, current_price, open_price, high_price, low_price, volume,
                    change_amount, change_percent, performance_score, rank_position, sector_performance_rank,
                    rsi, stochastic_k, stochastic_d, williams_r, cci, roc, atr,
                    ma_5, ma_10, ma_20, ma_50, ma_200,
                    macd, macd_signal, macd_histogram,
                    bollinger_upper, bollinger_lower, bollinger_middle, bb_position,
                    support_level, resistance_level, support_distance, resistance_distance,
                    trend, trend_strength, trend_duration, momentum, volatility,
                    volume_sma, volume_ratio, volume_trend, price_volume_trend,
                    beta_coefficient, sharpe_ratio, alpha_coefficient, information_ratio,
                    relative_strength_index, market_cap_rank,
                    value_at_risk, maximum_drawdown, downside_deviation,
                    confidence_score, recommendation, risk_level, expected_return, target_price, stop_loss,
                    analysis_summary, key_insights, risk_factors, opportunities,
                    analysis_version, data_quality_score
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                )
                """

                params = (
                    stock['stock_code'], current_price, open_price, high_price, low_price, volume,
                    change_amount, change_percent, performance_score, rank_position, sector_performance_rank,
                    rsi, stochastic_k, stochastic_d, williams_r, cci, roc, atr,
                    ma_5, ma_10, ma_20, ma_50, ma_200,
                    macd, macd_signal, macd_histogram,
                    bollinger_upper, bollinger_lower, bollinger_middle, bb_position,
                    support_level, resistance_level, support_distance, resistance_distance,
                    trend, trend_strength, trend_duration, momentum, volatility,
                    volume_sma, volume_ratio, volume_trend, price_volume_trend,
                    beta_coefficient, sharpe_ratio, alpha_coefficient, information_ratio,
                    relative_strength_index, 0,  # market_cap_rank
                    value_at_risk, maximum_drawdown, downside_deviation,
                    confidence_score, recommendation, risk_level, expected_return, target_price, stop_loss,
                    analysis_summary, key_insights, risk_factors, opportunities,
                    "3.0", 0.95  # analysis_version and data_quality_score
                )
                
                # Debug: Verify parameter count matches
                placeholder_count = query.count('%s')
                param_count = len(params)
                
                if placeholder_count != param_count:
                    logger.error(f"Parameter mismatch: {placeholder_count} placeholders vs {param_count} parameters")
                    return False
                
                self.execute_query(query, params)
                logger.info(f"Saved advanced analysis for {stock['stock_code']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving advanced analysis: {e}")
            return False

    def _determine_advanced_recommendation(self, technical_analysis: Dict, performance_score: float) -> str:
        """Determine advanced recommendation based on comprehensive analysis"""
        try:
            rsi = technical_analysis.get('rsi', 50.0)
            trend = technical_analysis.get('price_trend', 'sideways')
            momentum = technical_analysis.get('momentum', 0.0)
            
            # Strong buy conditions
            if (rsi < 30 and trend in ['uptrend', 'strong_uptrend'] and 
                momentum > 5 and performance_score > 70):
                return 'strong_buy'
            
            # Buy conditions
            elif (rsi < 40 and trend in ['uptrend', 'strong_uptrend'] and 
                momentum > 0 and performance_score > 50):
                return 'buy'
            
            # Strong sell conditions
            elif (rsi > 70 and trend in ['downtrend', 'strong_downtrend'] and 
                momentum < -5 and performance_score < 30):
                return 'strong_sell'
            
            # Sell conditions
            elif (rsi > 60 and trend in ['downtrend', 'strong_downtrend'] and 
                momentum < 0 and performance_score < 50):
                return 'sell'
            
            # Hold conditions
            else:
                return 'hold'
                
        except Exception as e:
            logger.warning(f"Error determining advanced recommendation: {e}")
            return 'hold'

    def _create_advanced_analysis_summary(self, stock: Dict, technical_analysis: Dict) -> str:
        """Create comprehensive analysis summary"""
        try:
            stock_code = stock['stock_code']
            stock_name = stock['stock_name']
            sector = stock['sector']
            performance_score = stock.get('performance_score', 0.0)
            change_percent = stock.get('change_percent', 0.0)
            
            rsi = technical_analysis.get('rsi', 50.0)
            trend = technical_analysis.get('price_trend', 'sideways')
            momentum = technical_analysis.get('momentum', 0.0)
            
            summary = f"""
            {stock_name} ({stock_code}) - {sector} Sector Advanced Analysis
            
            PERFORMANCE METRICS:
            - Performance Score: {performance_score:.1f}/100
            - Price Change: {change_percent:+.2f}%
            - Current Price: {stock.get('current_price', 0):.2f}
            
            TECHNICAL INDICATORS:
            - RSI: {rsi:.1f} ({'Oversold' if rsi < 30 else 'Overbought' if rsi > 70 else 'Neutral'})
            - Trend: {trend.replace('_', ' ').title()}
            - Momentum: {momentum:+.2f}%
            
            ADVANCED ANALYTICS:
            - Beta Coefficient: {technical_analysis.get('advanced_analytics', {}).get('beta_coefficient', 1.0):.2f}
            - Sharpe Ratio: {technical_analysis.get('advanced_analytics', {}).get('sharpe_ratio', 0.0):.2f}
            - Value at Risk: {technical_analysis.get('risk_metrics', {}).get('value_at_risk', 0.0):.2f}%
            
            RECOMMENDATION:
            - Action: {stock.get('recommendation', 'hold').replace('_', ' ').title()}
            - Confidence: {stock.get('confidence_score', 0.5):.1%}
            - Risk Level: {stock.get('risk_level', 'moderate').title()}
            - Expected Return: {stock.get('expected_return', 0.0):+.2f}%
            """
            
            return summary.strip()
            
        except Exception as e:
            logger.warning(f"Error creating advanced analysis summary: {e}")
            return f"Advanced analysis for {stock.get('stock_code', 'Unknown')}"
    
    def clear_news_records(self) -> bool:
        """Clear all news records from the database"""
        try:
            query = "DELETE FROM news_records"
            self.execute_query(query)
            logger.info("Successfully cleared all news records from database")
            return True
        except Exception as e:
            logger.error(f"Error clearing news records: {e}")
            return False
    
    def clear_recommendations(self) -> bool:
        """Clear all recommendations from the database"""
        try:
            query = "DELETE FROM recommendations"
            self.execute_query(query)
            logger.info("Successfully cleared all recommendations from database")
            return True
        except Exception as e:
            logger.error(f"Error clearing recommendations: {e}")
            return False
    
    def _serialize_news_sentiment(self, news_sentiment) -> Dict:
        """Properly serialize NewsAnalysisResult dataclass to dictionary"""
        try:
            if hasattr(news_sentiment, '__dict__'):
                # Convert dataclass to dictionary
                news_sentiment_dict = {}
                for key, value in news_sentiment.__dict__.items():
                    if isinstance(value, datetime):
                        news_sentiment_dict[key] = value.isoformat()
                    elif isinstance(value, (list, dict)):
                        news_sentiment_dict[key] = value
                    else:
                        news_sentiment_dict[key] = str(value) if value is not None else ''
                return news_sentiment_dict
            elif isinstance(news_sentiment, dict):
                # Already a dictionary, just ensure datetime objects are serialized
                serialized_dict = {}
                for key, value in news_sentiment.items():
                    if isinstance(value, datetime):
                        serialized_dict[key] = value.isoformat()
                    else:
                        serialized_dict[key] = value
                return serialized_dict
            else:
                # Fallback for other types
                return {'sentiment_data': str(news_sentiment)}
        except Exception as e:
            logger.error(f"Error serializing news sentiment: {e}")
            return {'error': 'Failed to serialize news sentiment data'}
    
    def ensure_user_exists(self, user_id: str, user_input: Dict = None) -> bool:
        """Ensure user exists in database, create if not"""
        try:
            # Check if user exists
            user_check = self.execute_query(
                "SELECT user_id FROM users WHERE user_id = %s",
                (user_id,)
            )
            
            if not user_check:
                # Create user if doesn't exist
                logger.info(f"Creating new user: {user_id}")
                create_user_query = """
                    INSERT INTO users (
                        user_id, name, email, password, risk_tolerance,
                        investment_goal, portfolio_value, cash_balance,
                        preferred_sectors, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                user_params = (
                    user_id,
                    f"User {user_id}",
                    f"{user_id}@example.com",
                    "default_password",  # Should be hashed in production
                    user_input.get('risk_tolerance', 'moderate') if user_input else 'moderate',
                    user_input.get('investment_goal', 'growth') if user_input else 'growth',
                    0.00,  # portfolio_value
                    0.00,  # cash_balance
                    json.dumps([user_input.get('sector_preference', 'Any')]) if user_input else json.dumps(['Any']),
                    datetime.now(),
                    datetime.now()
                )
                
                self.execute_query(create_user_query, user_params)
                logger.info(f"Successfully created user: {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring user exists: {e}")
            return False

    def save_recommendations_batch(self, recommendations: List[Dict], user_id: str, user_input: Dict = None) -> bool:
        """Save batch of recommendations to database"""
        try:
            # Ensure user exists before saving recommendations
            if not self.ensure_user_exists(user_id, user_input):
                logger.error(f"Failed to ensure user {user_id} exists")
                return False
            
            for rec in recommendations:
                # Get stock details using execute_query (same pattern as other methods)
                stock_details_result = self.execute_query(
                    "SELECT name, sector FROM stocks WHERE code = %s",
                    (rec.get('stock_code'),)
                )
                
                stock_name = ''
                sector = ''
                if stock_details_result:
                    stock_details = stock_details_result[0]
                    stock_name = stock_details.get('name', '')
                    sector = stock_details.get('sector', '')
                
                # Prepare recommendation data
                # Convert news sentiment to dictionary if it's a NewsAnalysisResult object
                news_sentiment = rec.get('news_sentiment', {})
                news_sentiment_dict = self._serialize_news_sentiment(news_sentiment)
                
                recommendation_data = {
                    'user_id': user_id,
                    'stock_code': rec.get('stock_code'),
                    'stock_name': stock_name,
                    'sector': sector,
                    'recommendation_type': rec.get('recommendation_type', 'buy'),
                    'confidence_score': float(rec.get('confidence_score', 0.5)),
                    'expected_return': float(rec.get('expected_return', 0.0)),
                    'risk_level': rec.get('risk_level', 'medium'),
                    'technical_analysis': json.dumps(rec.get('technical_analysis', {})),
                    'news_sentiment': json.dumps(news_sentiment_dict),
                    'fundamental_analysis': json.dumps(rec.get('fundamental_analysis', {})),
                    'user_budget': float(user_input.get('budget', 0)) if user_input else 0.0,
                    'user_risk_tolerance': user_input.get('risk_tolerance', 'medium') if user_input else 'medium',
                    'user_time_horizon': user_input.get('time_horizon', 'medium') if user_input else 'medium',
                    'user_sector_preference': user_input.get('sector_preference', 'Any') if user_input else 'Any',
                    'reasoning_summary': rec.get('reasoning_summary', ''),
                    'key_factors': json.dumps(rec.get('key_factors', [])),
                    'risk_factors': json.dumps(rec.get('risk_factors', [])),
                    'expires_at': None,  # Can be set based on recommendation type
                    'is_active': True,
                    'source_agent': 'agentic_framework',
                    'model_version': 'v1.0',
                    'analysis_timestamp': datetime.now()
                }
                
                # Insert recommendation using the same pattern as other save methods
                query = """
                    INSERT INTO recommendations (
                        user_id, stock_code, stock_name, sector, recommendation_type,
                        confidence_score, expected_return, risk_level, technical_analysis,
                        news_sentiment, fundamental_analysis, user_budget, user_risk_tolerance,
                        user_time_horizon, user_sector_preference, reasoning_summary,
                        key_factors, risk_factors, expires_at, is_active, source_agent,
                        model_version, analysis_timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                params = (
                    recommendation_data['user_id'],
                    recommendation_data['stock_code'],
                    recommendation_data['stock_name'],
                    recommendation_data['sector'],
                    recommendation_data['recommendation_type'],
                    recommendation_data['confidence_score'],
                    recommendation_data['expected_return'],
                    recommendation_data['risk_level'],
                    recommendation_data['technical_analysis'],
                    recommendation_data['news_sentiment'],
                    recommendation_data['fundamental_analysis'],
                    recommendation_data['user_budget'],
                    recommendation_data['user_risk_tolerance'],
                    recommendation_data['user_time_horizon'],
                    recommendation_data['user_sector_preference'],
                    recommendation_data['reasoning_summary'],
                    recommendation_data['key_factors'],
                    recommendation_data['risk_factors'],
                    recommendation_data['expires_at'],
                    recommendation_data['is_active'],
                    recommendation_data['source_agent'],
                    recommendation_data['model_version'],
                    recommendation_data['analysis_timestamp']
                )
                
                self.execute_query(query, params)
            
            logger.info(f"Successfully saved {len(recommendations)} recommendations to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving recommendations: {e}")
            return False

# Global database instance
db_config = DatabaseConfig() 