#!/usr/bin/env python3
"""
Mock Data Population Script for BullBearPK
==========================================

This script populates the database with realistic mock data to test and validate
backend functionality. It includes:

- User profiles with different risk tolerances and investment goals
- Portfolio entries with various stock investments
- Recommendation history with different scenarios
- Investment form submissions with edge cases
- Stock data and market information

The mock data covers multiple users, edge cases, and realistic scenarios.
"""

import sys
import os
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal
import logging

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockDataPopulator:
    """Populates database with comprehensive mock data"""
    
    def __init__(self):
        self.db = DatabaseConfig()
        self.stock_codes = [
            'HBL', 'UBL', 'OGDC', 'PPL', 'LUCK', 'DGKC', 'FFC', 'ENGRO', 
            'MCB', 'ATRL', 'PSO', 'SHEL', 'NESTLE', 'UNILEVER', 'COLGATE',
            'EFERT', 'FFBL', 'FATIMA', 'HASCOL', 'ICI', 'INDU', 'KAPCO',
            'LOTCHEM', 'MARI', 'NBP', 'NRL', 'PAKRI', 'POL', 'PTC', 'SYS'
        ]
        
        self.stock_names = {
            'HBL': 'Habib Bank Limited',
            'UBL': 'United Bank Limited', 
            'OGDC': 'Oil & Gas Development Company',
            'PPL': 'Pakistan Petroleum Limited',
            'LUCK': 'Lucky Cement Limited',
            'DGKC': 'D.G. Khan Cement Company Limited',
            'FFC': 'Fauji Fertilizer Company Limited',
            'ENGRO': 'Engro Corporation Limited',
            'MCB': 'MCB Bank Limited',
            'ATRL': 'Attock Refinery Limited',
            'PSO': 'Pakistan State Oil Company Limited',
            'SHEL': 'Shell Pakistan Limited',
            'NESTLE': 'Nestle Pakistan Limited',
            'UNILEVER': 'Unilever Pakistan Limited',
            'COLGATE': 'Colgate-Palmolive Pakistan Limited',
            'EFERT': 'Engro Fertilizers Limited',
            'FFBL': 'Fauji Fertilizer Bin Qasim Limited',
            'FATIMA': 'Fatima Fertilizer Company Limited',
            'HASCOL': 'Hascol Petroleum Limited',
            'ICI': 'ICI Pakistan Limited',
            'INDU': 'Indus Motor Company Limited',
            'KAPCO': 'Kot Addu Power Company Limited',
            'LOTCHEM': 'Lotte Chemical Pakistan Limited',
            'MARI': 'Mari Petroleum Company Limited',
            'NBP': 'National Bank of Pakistan',
            'NRL': 'National Refinery Limited',
            'PAKRI': 'Pakistan Refinery Limited',
            'POL': 'Pakistan Oilfields Limited',
            'PTC': 'Pakistan Telecommunication Company Limited',
            'SYS': 'Systems Limited'
        }
        
        self.sectors = {
            'HBL': 'Banking', 'UBL': 'Banking', 'MCB': 'Banking', 'NBP': 'Banking',
            'OGDC': 'Energy', 'PPL': 'Energy', 'ATRL': 'Energy', 'PSO': 'Energy',
            'SHEL': 'Energy', 'MARI': 'Energy', 'NRL': 'Energy', 'PAKRI': 'Energy',
            'POL': 'Energy', 'LUCK': 'Cement', 'DGKC': 'Cement',
            'FFC': 'Fertilizer', 'EFERT': 'Fertilizer', 'FFBL': 'Fertilizer',
            'FATIMA': 'Fertilizer', 'ENGRO': 'Chemical', 'NESTLE': 'Consumer Goods', 
            'UNILEVER': 'Consumer Goods', 'COLGATE': 'Consumer Goods', 'ICI': 'Chemical', 
            'LOTCHEM': 'Chemical', 'INDU': 'Automobile', 'KAPCO': 'Power', 
            'HASCOL': 'Oil & Gas', 'PTC': 'Telecommunications', 'SYS': 'Technology'
        }
        
        self.users = [
            {
                'user_id': 'user001',
                'name': 'Ahmed Khan',
                'email': 'ahmed.khan@email.com',
                'password': 'hashed_password_123',
                'risk_tolerance': 'moderate',
                'investment_goal': 'Long-term wealth building',
                'portfolio_value': 150000.00,
                'cash_balance': 25000.00,
                'preferred_sectors': json.dumps(['Banking', 'Energy', 'Cement']),
                'blacklisted_stocks': json.dumps([])
            },
            {
                'user_id': 'user002',
                'name': 'Fatima Ali',
                'email': 'fatima.ali@email.com',
                'password': 'hashed_password_456',
                'risk_tolerance': 'high',
                'investment_goal': 'Aggressive growth',
                'portfolio_value': 250000.00,
                'cash_balance': 50000.00,
                'preferred_sectors': json.dumps(['Technology', 'Energy', 'Consumer Goods']),
                'blacklisted_stocks': json.dumps(['HASCOL'])
            },
            {
                'user_id': 'user003',
                'name': 'Muhammad Hassan',
                'email': 'muhammad.hassan@email.com',
                'password': 'hashed_password_789',
                'risk_tolerance': 'low',
                'investment_goal': 'Conservative income',
                'portfolio_value': 80000.00,
                'cash_balance': 15000.00,
                'preferred_sectors': json.dumps(['Banking', 'Fertilizer']),
                'blacklisted_stocks': json.dumps(['SYS', 'PTC'])
            },
            {
                'user_id': 'user004',
                'name': 'Ayesha Rahman',
                'email': 'ayesha.rahman@email.com',
                'password': 'hashed_password_101',
                'risk_tolerance': 'moderate',
                'investment_goal': 'Balanced growth',
                'portfolio_value': 120000.00,
                'cash_balance': 30000.00,
                'preferred_sectors': json.dumps(['Consumer Goods', 'Cement', 'Banking']),
                'blacklisted_stocks': json.dumps([])
            },
            {
                'user_id': 'user005',
                'name': 'Omar Farooq',
                'email': 'omar.farooq@email.com',
                'password': 'hashed_password_202',
                'risk_tolerance': 'high',
                'investment_goal': 'Maximum returns',
                'portfolio_value': 300000.00,
                'cash_balance': 75000.00,
                'preferred_sectors': json.dumps(['Energy', 'Technology', 'Chemical']),
                'blacklisted_stocks': json.dumps([])
            }
        ]
    
    def populate_users(self):
        """Insert user profiles"""
        logger.info("Populating users table...")
        
        for user in self.users:
            query = """
            INSERT INTO users (user_id, name, email, password, risk_tolerance, 
                             investment_goal, portfolio_value, cash_balance, 
                             preferred_sectors, blacklisted_stocks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                email = VALUES(email),
                risk_tolerance = VALUES(risk_tolerance),
                investment_goal = VALUES(investment_goal),
                portfolio_value = VALUES(portfolio_value),
                cash_balance = VALUES(cash_balance),
                preferred_sectors = VALUES(preferred_sectors),
                blacklisted_stocks = VALUES(blacklisted_stocks)
            """
            
            params = (
                user['user_id'], user['name'], user['email'], user['password'],
                user['risk_tolerance'], user['investment_goal'], user['portfolio_value'],
                user['cash_balance'], user['preferred_sectors'], user['blacklisted_stocks']
            )
            
            try:
                self.db.execute_query(query, params)
                logger.info(f"User {user['user_id']} inserted/updated successfully")
            except Exception as e:
                logger.error(f"Error inserting user {user['user_id']}: {e}")
    
    def populate_stocks(self):
        """Insert stock data"""
        logger.info("Populating stocks table...")
        
        for code in self.stock_codes:
            # Generate realistic stock data
            base_price = random.uniform(50, 500)
            open_price = base_price
            high_price = open_price * random.uniform(1.02, 1.08)
            low_price = open_price * random.uniform(0.92, 0.98)
            close_price = random.uniform(low_price, high_price)
            volume = random.randint(100000, 5000000)
            change_amount = close_price - open_price
            change_percent = (change_amount / open_price) * 100
            market_cap = volume * close_price * random.uniform(0.8, 1.2)
            pe_ratio = random.uniform(8, 25)
            dividend_yield = random.uniform(0, 8)
            
            query = """
            INSERT INTO stocks (code, name, sector, open_price, high_price, low_price,
                              close_price, volume, change_amount, change_percent,
                              market_cap, pe_ratio, dividend_yield)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                sector = VALUES(sector),
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
            
            params = (
                code, self.stock_names[code], self.sectors[code],
                round(open_price, 2), round(high_price, 2), round(low_price, 2),
                round(close_price, 2), volume, round(change_amount, 2),
                round(change_percent, 2), round(market_cap, 2),
                round(pe_ratio, 2), round(dividend_yield, 2)
            )
            
            try:
                self.db.execute_query(query, params)
                logger.info(f"Stock {code} inserted/updated successfully")
            except Exception as e:
                logger.error(f"Error inserting stock {code}: {e}")
    
    def populate_portfolios(self):
        """Insert portfolio data for users"""
        logger.info("Populating portfolios table...")
        
        for user in self.users:
            # Calculate portfolio metrics
            total_invested = user['portfolio_value'] - user['cash_balance']
            total_profit_loss = random.uniform(-5000, 15000)
            profit_loss_percent = (total_profit_loss / total_invested) * 100 if total_invested > 0 else 0
            available_cash = user['cash_balance'] * random.uniform(0.8, 1.0)
            reserved_cash = user['cash_balance'] - available_cash
            
            query = """
            INSERT INTO portfolios (user_id, total_value, total_invested, total_profit_loss,
                                 profit_loss_percent, cash_balance, available_cash, reserved_cash,
                                 total_realized_pnl, total_unrealized_pnl, total_dividends_received,
                                 total_stocks_held, active_investments, sold_investments,
                                 portfolio_volatility, portfolio_beta, portfolio_sharpe_ratio, max_drawdown,
                                 sector_allocation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_value = VALUES(total_value),
                total_invested = VALUES(total_invested),
                total_profit_loss = VALUES(total_profit_loss),
                profit_loss_percent = VALUES(profit_loss_percent),
                cash_balance = VALUES(cash_balance),
                available_cash = VALUES(available_cash),
                reserved_cash = VALUES(reserved_cash)
            """
            
            # Generate sector allocation
            sector_allocation = {
                'Banking': random.uniform(20, 40),
                'Energy': random.uniform(15, 35),
                'Cement': random.uniform(10, 25),
                'Consumer Goods': random.uniform(5, 20),
                'Fertilizer': random.uniform(5, 15)
            }
            
            params = (
                user['user_id'], user['portfolio_value'], total_invested,
                round(total_profit_loss, 2), round(profit_loss_percent, 2),
                user['cash_balance'], round(available_cash, 2), round(reserved_cash, 2),
                round(total_profit_loss * 0.6, 2), round(total_profit_loss * 0.4, 2),
                round(random.uniform(500, 2000), 2), random.randint(3, 8),
                random.randint(2, 6), random.randint(1, 3),
                round(random.uniform(0.1, 0.3), 2), round(random.uniform(0.8, 1.2), 2),
                round(random.uniform(0.5, 1.5), 2), round(random.uniform(0.05, 0.15), 2),
                json.dumps(sector_allocation)
            )
            
            try:
                self.db.execute_query(query, params)
                logger.info(f"Portfolio for user {user['user_id']} inserted/updated successfully")
            except Exception as e:
                logger.error(f"Error inserting portfolio for user {user['user_id']}: {e}")
    
    def populate_investments(self):
        """Insert investment data for users"""
        logger.info("Populating investments table...")
        
        investment_scenarios = [
            # User 1 - Moderate investor with mixed portfolio
            {'user_id': 'user001', 'stocks': ['HBL', 'OGDC', 'LUCK'], 'quantities': [500, 300, 100]},
            # User 2 - Aggressive investor with tech focus
            {'user_id': 'user002', 'stocks': ['SYS', 'PTC', 'ENGRO'], 'quantities': [200, 400, 150]},
            # User 3 - Conservative investor with banking focus
            {'user_id': 'user003', 'stocks': ['HBL', 'UBL', 'FFC'], 'quantities': [300, 200, 250]},
            # User 4 - Balanced investor
            {'user_id': 'user004', 'stocks': ['NESTLE', 'LUCK', 'MCB'], 'quantities': [150, 200, 300]},
            # User 5 - High-risk investor
            {'user_id': 'user005', 'stocks': ['OGDC', 'SYS', 'LOTCHEM'], 'quantities': [400, 300, 200]}
        ]
        
        for scenario in investment_scenarios:
            user_id = scenario['user_id']
            stocks = scenario['stocks']
            quantities = scenario['quantities']
            
            for i, stock_code in enumerate(stocks):
                quantity = quantities[i]
                buy_price = random.uniform(80, 120)  # Random buy price
                total_invested = quantity * buy_price
                current_price = buy_price * random.uniform(0.8, 1.3)  # Price variation
                current_value = quantity * current_price
                profit_loss = current_value - total_invested
                profit_loss_percent = (profit_loss / total_invested) * 100
                
                # Random investment status
                status = random.choice(['active', 'active', 'active', 'sold', 'partial_sold'])
                
                query = """
                INSERT INTO investments (user_id, stock_code, stock_name, sector, quantity,
                                      buy_price, total_invested, current_quantity, current_price,
                                      current_value, market_value, profit_loss, profit_loss_percent,
                                      unrealized_pnl, realized_pnl, status, buy_date, investment_duration_days,
                                      highest_price_reached, lowest_price_reached, max_profit_reached,
                                      max_loss_reached, volatility_score, beta_coefficient, sharpe_ratio,
                                      total_dividends_received, dividend_yield, recommendation_when_bought,
                                      confidence_score_when_bought, created_by, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Calculate additional metrics
                current_quantity = quantity if status == 'active' else random.randint(0, quantity)
                unrealized_pnl = profit_loss if status == 'active' else 0
                realized_pnl = profit_loss if status in ['sold', 'partial_sold'] else 0
                investment_duration = random.randint(30, 365)
                buy_date = datetime.now() - timedelta(days=investment_duration)
                
                params = (
                    user_id, stock_code, self.stock_names[stock_code], self.sectors[stock_code],
                    quantity, round(buy_price, 2), round(total_invested, 2), current_quantity,
                    round(current_price, 2), round(current_value, 2), round(current_value, 2),
                    round(profit_loss, 2), round(profit_loss_percent, 2), round(unrealized_pnl, 2),
                    round(realized_pnl, 2), status, buy_date, investment_duration,
                    round(current_price * 1.2, 2), round(current_price * 0.8, 2),
                    round(profit_loss * 1.5, 2), round(profit_loss * 0.5, 2),
                    round(random.uniform(0.1, 0.4), 2), round(random.uniform(0.8, 1.3), 2),
                    round(random.uniform(0.5, 1.8), 2), round(random.uniform(100, 500), 2),
                    round(random.uniform(2, 6), 2), 'buy', round(random.uniform(0.6, 0.9), 2),
                    'user', 'manual'
                )
                
                try:
                    self.db.execute_query(query, params)
                    logger.info(f"Investment {stock_code} for user {user_id} inserted successfully")
                except Exception as e:
                    logger.error(f"Error inserting investment {stock_code} for user {user_id}: {e}")
    
    def populate_recommendations(self):
        """Insert recommendation history"""
        logger.info("Populating recommendations table...")
        
        recommendation_types = ['buy', 'sell', 'hold', 'strong_buy', 'strong_sell']
        risk_levels = ['low', 'medium', 'high']
        
        for user in self.users:
            # Generate 3-5 recommendations per user
            num_recommendations = random.randint(3, 5)
            
            for i in range(num_recommendations):
                stock_code = random.choice(self.stock_codes)
                recommendation_type = random.choice(recommendation_types)
                confidence_score = random.uniform(0.6, 0.95)
                expected_return = random.uniform(-10, 25)
                risk_level = random.choice(risk_levels)
                
                # Generate technical analysis JSON
                technical_analysis = {
                    'rsi': round(random.uniform(30, 70), 2),
                    'macd': round(random.uniform(-2, 2), 2),
                    'moving_average': round(random.uniform(80, 120), 2),
                    'support_level': round(random.uniform(70, 100), 2),
                    'resistance_level': round(random.uniform(110, 140), 2)
                }
                
                # Generate news sentiment JSON
                news_sentiment = {
                    'sentiment_score': round(random.uniform(-0.5, 0.8), 2),
                    'positive_news_count': random.randint(0, 10),
                    'negative_news_count': random.randint(0, 5),
                    'neutral_news_count': random.randint(5, 15)
                }
                
                # Generate fundamental analysis JSON
                fundamental_analysis = {
                    'pe_ratio': round(random.uniform(8, 25), 2),
                    'pb_ratio': round(random.uniform(0.5, 3), 2),
                    'debt_to_equity': round(random.uniform(0.1, 0.8), 2),
                    'roe': round(random.uniform(5, 25), 2),
                    'profit_margin': round(random.uniform(5, 20), 2)
                }
                
                query = """
                INSERT INTO recommendations (user_id, stock_code, stock_name, sector,
                                         recommendation_type, confidence_score, expected_return,
                                         risk_level, technical_analysis, news_sentiment,
                                         fundamental_analysis, user_budget, user_risk_tolerance,
                                         user_time_horizon, user_sector_preference, reasoning_summary,
                                         key_factors, risk_factors, created_at, expires_at, is_active,
                                         source_agent, model_version, analysis_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                reasoning_summary = f"Based on technical analysis showing {technical_analysis['rsi']} RSI and {technical_analysis['macd']} MACD, this stock appears to be in a {'bullish' if recommendation_type in ['buy', 'strong_buy'] else 'bearish'} trend."
                
                key_factors = {
                    'technical_indicators': technical_analysis,
                    'market_sentiment': news_sentiment,
                    'fundamental_metrics': fundamental_analysis
                }
                
                risk_factors = {
                    'market_volatility': round(random.uniform(0.1, 0.4), 2),
                    'sector_risk': round(random.uniform(0.2, 0.6), 2),
                    'liquidity_risk': round(random.uniform(0.1, 0.3), 2)
                }
                
                created_at = datetime.now() - timedelta(days=random.randint(1, 30))
                expires_at = created_at + timedelta(days=random.randint(7, 30))
                
                params = (
                    user['user_id'], stock_code, self.stock_names[stock_code], self.sectors[stock_code],
                    recommendation_type, round(confidence_score, 2), round(expected_return, 2),
                    risk_level, json.dumps(technical_analysis), json.dumps(news_sentiment),
                    json.dumps(fundamental_analysis), user['portfolio_value'], user['risk_tolerance'],
                    'long_term', random.choice(['Banking', 'Energy', 'Technology']), reasoning_summary,
                    json.dumps(key_factors), json.dumps(risk_factors), created_at, expires_at,
                    random.choice([True, True, False]), 'agentic_framework', 'v1.0', created_at
                )
                
                try:
                    self.db.execute_query(query, params)
                    logger.info(f"Recommendation {i+1} for user {user['user_id']} inserted successfully")
                except Exception as e:
                    logger.error(f"Error inserting recommendation for user {user['user_id']}: {e}")
    
    def populate_form_submissions(self):
        """Insert investment form submissions"""
        logger.info("Populating user_form_submissions table...")
        
        form_scenarios = [
            {
                'user_id': 'user001',
                'budget': 50000,
                'sector_preference': 'Banking',
                'risk_tolerance': 'moderate',
                'time_horizon': 'long_term',
                'target_profit': 12.5,
                'investment_goal': 'Balanced growth'
            },
            {
                'user_id': 'user002',
                'budget': 100000,
                'sector_preference': 'Technology',
                'risk_tolerance': 'high',
                'time_horizon': 'medium_term',
                'target_profit': 25.0,
                'investment_goal': 'Aggressive growth'
            },
            {
                'user_id': 'user003',
                'budget': 25000,
                'sector_preference': 'Banking',
                'risk_tolerance': 'low',
                'time_horizon': 'long_term',
                'target_profit': 8.0,
                'investment_goal': 'Conservative income'
            },
            {
                'user_id': 'user004',
                'budget': 75000,
                'sector_preference': 'Consumer Goods',
                'risk_tolerance': 'moderate',
                'time_horizon': 'medium_term',
                'target_profit': 15.0,
                'investment_goal': 'Balanced portfolio'
            },
            {
                'user_id': 'user005',
                'budget': 150000,
                'sector_preference': 'Energy',
                'risk_tolerance': 'high',
                'time_horizon': 'short_term',
                'target_profit': 30.0,
                'investment_goal': 'Maximum returns'
            }
        ]
        
        for scenario in form_scenarios:
            query = """
            INSERT INTO user_form_submissions (user_id, budget, sector_preference, risk_tolerance,
                                             time_horizon, target_profit, investment_goal,
                                             submission_date, recommendations_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            submission_date = datetime.now() - timedelta(days=random.randint(1, 60))
            recommendations_count = random.randint(3, 8)
            
            params = (
                scenario['user_id'], scenario['budget'], scenario['sector_preference'],
                scenario['risk_tolerance'], scenario['time_horizon'], scenario['target_profit'],
                scenario['investment_goal'], submission_date, recommendations_count
            )
            
            try:
                self.db.execute_query(query, params)
                logger.info(f"Form submission for user {scenario['user_id']} inserted successfully")
            except Exception as e:
                logger.error(f"Error inserting form submission for user {scenario['user_id']}: {e}")
    
    def populate_recommendations_history(self):
        """Insert recommendations history"""
        logger.info("Populating user_recommendations_history table...")
        
        # Get form submission IDs
        form_submissions = self.db.execute_query("SELECT id, user_id FROM user_form_submissions")
        
        for submission in form_submissions:
            form_id = submission['id']
            user_id = submission['user_id']
            
            # Generate 3-5 historical recommendations per submission
            num_recommendations = random.randint(3, 5)
            
            for i in range(num_recommendations):
                stock_code = random.choice(self.stock_codes)
                recommendation_type = random.choice(['buy', 'sell', 'hold'])
                confidence_score = random.uniform(0.6, 0.95)
                expected_return = random.uniform(-10, 25)
                
                # Generate reasoning
                reasoning = f"Based on analysis of {stock_code}, the stock shows {'positive' if recommendation_type == 'buy' else 'negative'} momentum with {confidence_score:.1%} confidence. Expected return: {expected_return:.1f}%"
                
                # Generate technical analysis JSON
                technical_analysis = {
                    'rsi': round(random.uniform(30, 70), 2),
                    'macd': round(random.uniform(-2, 2), 2),
                    'moving_average': round(random.uniform(80, 120), 2),
                    'volume_trend': 'increasing' if random.choice([True, False]) else 'decreasing'
                }
                
                # Generate news sentiment JSON
                news_sentiment = {
                    'sentiment_score': round(random.uniform(-0.5, 0.8), 2),
                    'news_count': random.randint(5, 20),
                    'positive_ratio': round(random.uniform(0.3, 0.8), 2)
                }
                
                query = """
                INSERT INTO user_recommendations_history (user_id, form_submission_id, stock_code,
                                                        stock_name, recommendation_type, confidence_score,
                                                        expected_return, reasoning, technical_analysis,
                                                        news_sentiment, recommendation_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                recommendation_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                params = (
                    user_id, form_id, stock_code, self.stock_names[stock_code],
                    recommendation_type, round(confidence_score, 2), round(expected_return, 2),
                    reasoning, json.dumps(technical_analysis), json.dumps(news_sentiment),
                    recommendation_date
                )
                
                try:
                    self.db.execute_query(query, params)
                    logger.info(f"Recommendation history {i+1} for submission {form_id} inserted successfully")
                except Exception as e:
                    logger.error(f"Error inserting recommendation history for submission {form_id}: {e}")
    

    
    def populate_market_summary(self):
        """Insert market summary data"""
        logger.info("Populating market_summary table...")
        
        # Generate market summary for the last 30 days
        for i in range(30):
            summary_date = datetime.now() - timedelta(days=i)
            total_volume = random.randint(100000000, 500000000)
            total_trades = random.randint(30000, 80000)
            market_cap = random.uniform(7000000000000, 9000000000000)
            kse_100_index = random.uniform(40000, 50000)
            kse_100_change = random.uniform(-3, 3)
            
            query = """
            INSERT INTO market_summary (summary_date, total_volume, total_trades, market_cap,
                                      kse_100_index, kse_100_change)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_volume = VALUES(total_volume),
                total_trades = VALUES(total_trades),
                market_cap = VALUES(market_cap),
                kse_100_index = VALUES(kse_100_index),
                kse_100_change = VALUES(kse_100_change)
            """
            
            params = (
                summary_date.date(), total_volume, total_trades, round(market_cap, 2),
                round(kse_100_index, 2), round(kse_100_change, 2)
            )
            
            try:
                self.db.execute_query(query, params)
                logger.info(f"Market summary for {summary_date.date()} inserted successfully")
            except Exception as e:
                logger.error(f"Error inserting market summary for {summary_date.date()}: {e}")
    
    def run_population(self):
        """Run the complete mock data population"""
        logger.info("Starting mock data population...")
        
        try:
            # Test database connection
            if not self.db.test_connection():
                logger.error("Database connection failed. Please check your database configuration.")
                return False
            
            # Populate tables in order (respecting foreign key constraints)
            self.populate_users()
            self.populate_stocks()
            self.populate_portfolios()
            self.populate_investments()
            self.populate_recommendations()
            self.populate_form_submissions()
            self.populate_recommendations_history()

            self.populate_market_summary()
            
            logger.info("Mock data population completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error during mock data population: {e}")
            return False

def main():
    """Main function to run the mock data population"""
    populator = MockDataPopulator()
    
    print("=" * 60)
    print("BullBearPK Mock Data Population Script")
    print("=" * 60)
    print()
    print("This script will populate the database with realistic mock data")
    print("to test and validate backend functionality.")
    print()
    print("Mock data includes:")
    print("- 5 user profiles with different risk tolerances")
    print("- 30 stock entries with realistic data")
    print("- Portfolio data for each user")
    print("- Investment history with various scenarios")
    print("- Recommendation history and form submissions")
    print("- Market summary data")
    print()
    
    response = input("Do you want to proceed with mock data population? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = populator.run_population()
        
        if success:
            print("\n✅ Mock data population completed successfully!")
            print("\nYou can now test the backend functionality with realistic data.")
            print("\nSample queries to verify data:")
            print("- SELECT * FROM users LIMIT 5;")
            print("- SELECT * FROM portfolios LIMIT 5;")
            print("- SELECT * FROM investments LIMIT 10;")
            print("- SELECT * FROM recommendations LIMIT 10;")
        else:
            print("\n❌ Mock data population failed. Check the logs for errors.")
    else:
        print("\nMock data population cancelled.")

if __name__ == "__main__":
    main() 