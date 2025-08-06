#!/usr/bin/env python3
"""
Database Initialization Script for BullBearPK
=============================================

This script checks if the required database tables exist and creates them if needed.
"""

import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables"""
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234',
        'database': 'bullbearpk',
        'charset': 'utf8mb4'
    }
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        logger.info("Connected to database successfully")
        
        # Check if investments table exists
        cursor.execute("SHOW TABLES LIKE 'investments'")
        investments_exists = cursor.fetchone()
        
        if not investments_exists:
            logger.info("Creating investments table...")
            
            # Create investments table
            create_investments_table = """
            CREATE TABLE investments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) NOT NULL,
                stock_code VARCHAR(20) NOT NULL,
                stock_name VARCHAR(200),
                sector VARCHAR(100),
                
                -- Transaction Details
                transaction_type ENUM('buy', 'sell', 'dividend', 'split', 'bonus') DEFAULT 'buy',
                quantity INT NOT NULL,
                buy_price DECIMAL(10,2) NOT NULL,
                total_invested DECIMAL(15,2) NOT NULL,
                
                -- Current Status
                current_quantity INT DEFAULT 0,
                current_price DECIMAL(10,2) DEFAULT 0.00,
                current_value DECIMAL(15,2) DEFAULT 0.00,
                market_value DECIMAL(15,2) DEFAULT 0.00,
                
                -- Profit/Loss Tracking
                profit_loss DECIMAL(15,2) DEFAULT 0.00,
                profit_loss_percent DECIMAL(5,2) DEFAULT 0.00,
                unrealized_pnl DECIMAL(15,2) DEFAULT 0.00,
                realized_pnl DECIMAL(15,2) DEFAULT 0.00,
                
                -- Investment Status
                status ENUM('active', 'sold', 'partial_sold', 'pending', 'cancelled') DEFAULT 'active',
                investment_duration_days INT DEFAULT 0,
                
                -- Transaction Timestamps
                buy_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sell_date TIMESTAMP NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                -- Sell Details (if applicable)
                sell_price DECIMAL(10,2) NULL,
                sell_quantity INT NULL,
                sell_reason VARCHAR(100) NULL,
                
                -- Performance Metrics
                highest_price_reached DECIMAL(10,2) DEFAULT 0.00,
                lowest_price_reached DECIMAL(10,2) DEFAULT 0.00,
                max_profit_reached DECIMAL(15,2) DEFAULT 0.00,
                max_loss_reached DECIMAL(15,2) DEFAULT 0.00,
                
                -- Risk Metrics
                volatility_score DECIMAL(5,2) DEFAULT 0.00,
                beta_coefficient DECIMAL(5,2) DEFAULT 0.00,
                sharpe_ratio DECIMAL(5,2) DEFAULT 0.00,
                
                -- Dividend Tracking
                total_dividends_received DECIMAL(15,2) DEFAULT 0.00,
                dividend_yield DECIMAL(5,2) DEFAULT 0.00,
                last_dividend_date DATE NULL,
                next_dividend_date DATE NULL,
                
                -- Analysis Data
                recommendation_when_bought VARCHAR(20) NULL,
                confidence_score_when_bought DECIMAL(3,2) NULL,
                technical_analysis_when_bought JSON NULL,
                news_sentiment_when_bought JSON NULL,
                
                -- User Notes
                user_notes TEXT NULL,
                tags JSON NULL,
                
                -- Metadata
                created_by VARCHAR(50) DEFAULT 'system',
                source VARCHAR(50) DEFAULT 'manual',
                
                INDEX idx_user_stock (user_id, stock_code),
                INDEX idx_status (status),
                INDEX idx_buy_date (buy_date),
                INDEX idx_sell_date (sell_date),
                INDEX idx_transaction_type (transaction_type)
            )
            """
            
            cursor.execute(create_investments_table)
            logger.info("Investments table created successfully")
        else:
            logger.info("Investments table already exists")
        
        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        users_exists = cursor.fetchone()
        
        if not users_exists:
            logger.info("Creating users table...")
            
            create_users_table = """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                risk_tolerance ENUM('low', 'moderate', 'high') DEFAULT 'moderate',
                investment_goal VARCHAR(100),
                portfolio_value DECIMAL(15,2) DEFAULT 0.00,
                cash_balance DECIMAL(15,2) DEFAULT 0.00,
                preferred_sectors JSON NULL,
                blacklisted_stocks JSON NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            cursor.execute(create_users_table)
            logger.info("Users table created successfully")
        else:
            logger.info("Users table already exists")
        
        # Check if stocks table exists
        cursor.execute("SHOW TABLES LIKE 'stocks'")
        stocks_exists = cursor.fetchone()
        
        if not stocks_exists:
            logger.info("Creating stocks table...")
            
            create_stocks_table = """
            CREATE TABLE stocks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(20) NOT NULL,
                name VARCHAR(200) NOT NULL,
                sector VARCHAR(100),
                open_price DECIMAL(10,2),
                high_price DECIMAL(10,2),
                low_price DECIMAL(10,2),
                close_price DECIMAL(10,2),
                volume BIGINT,
                change_amount DECIMAL(10,2),
                change_percent DECIMAL(5,2),
                market_cap DECIMAL(15,2),
                pe_ratio DECIMAL(10,2),
                dividend_yield DECIMAL(5,2),
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_code (code),
                INDEX idx_sector (sector),
                INDEX idx_scraped_at (scraped_at)
            )
            """
            
            cursor.execute(create_stocks_table)
            logger.info("Stocks table created successfully")
        else:
            logger.info("Stocks table already exists")
        
        connection.commit()
        logger.info("Database initialization completed successfully")
        
    except Error as e:
        logger.error(f"Database initialization error: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

if __name__ == "__main__":
    init_database() 