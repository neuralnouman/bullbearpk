#!/usr/bin/env python3
"""
Add Sample Stock Data for Testing
=================================

This script adds sample stock data to the database for testing purposes.
"""

import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sample_stocks():
    """Add sample stock data to the database"""
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1234',
        'database': 'bullbearpk',
        'charset': 'utf8mb4'
    }
    
    sample_stocks = [
        {
            'code': 'OGDC',
            'name': 'Oil & Gas Development Company Ltd.',
            'sector': 'Oil & Gas',
            'open_price': 85.50,
            'high_price': 87.20,
            'low_price': 84.80,
            'close_price': 86.10,
            'volume': 1500000,
            'change_amount': 0.60,
            'change_percent': 0.70,
            'market_cap': 38000000000,
            'pe_ratio': 8.5,
            'dividend_yield': 5.2
        },
        {
            'code': 'HUBCO',
            'name': 'Hub Power Company Limited',
            'sector': 'Power',
            'open_price': 120.00,
            'high_price': 122.50,
            'low_price': 119.20,
            'close_price': 121.80,
            'volume': 2000000,
            'change_amount': 1.80,
            'change_percent': 1.50,
            'market_cap': 45000000000,
            'pe_ratio': 12.3,
            'dividend_yield': 4.8
        },
        {
            'code': 'LUCK',
            'name': 'Lucky Cement Limited',
            'sector': 'Cement',
            'open_price': 650.00,
            'high_price': 655.50,
            'low_price': 648.20,
            'close_price': 652.80,
            'volume': 800000,
            'change_amount': 2.80,
            'change_percent': 0.43,
            'market_cap': 28000000000,
            'pe_ratio': 15.2,
            'dividend_yield': 3.5
        },
        {
            'code': 'MCB',
            'name': 'MCB Bank Limited',
            'sector': 'Banking',
            'open_price': 180.00,
            'high_price': 182.50,
            'low_price': 179.20,
            'close_price': 181.80,
            'volume': 1200000,
            'change_amount': 1.80,
            'change_percent': 1.00,
            'market_cap': 22000000000,
            'pe_ratio': 6.8,
            'dividend_yield': 7.2
        },
        {
            'code': 'ENGRO',
            'name': 'Engro Corporation Limited',
            'sector': 'Chemicals',
            'open_price': 320.00,
            'high_price': 325.50,
            'low_price': 318.20,
            'close_price': 323.80,
            'volume': 900000,
            'change_amount': 3.80,
            'change_percent': 1.19,
            'market_cap': 35000000000,
            'pe_ratio': 18.5,
            'dividend_yield': 2.8
        }
    ]
    
    try:
        # Connect to database
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        logger.info("Connected to database successfully")
        
        # Check if stocks table exists
        cursor.execute("SHOW TABLES LIKE 'stocks'")
        stocks_exists = cursor.fetchone()
        
        if not stocks_exists:
            logger.error("Stocks table does not exist. Please run the database initialization script first.")
            return False
        
        # Clear existing stock data
        cursor.execute("DELETE FROM stocks")
        logger.info("Cleared existing stock data")
        
        # Insert sample stocks
        insert_query = """
        INSERT INTO stocks (
            code, name, sector, open_price, high_price, low_price, close_price,
            volume, change_amount, change_percent, market_cap, pe_ratio, dividend_yield, scraped_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        for stock in sample_stocks:
            params = (
                stock['code'],
                stock['name'],
                stock['sector'],
                stock['open_price'],
                stock['high_price'],
                stock['low_price'],
                stock['close_price'],
                stock['volume'],
                stock['change_amount'],
                stock['change_percent'],
                stock['market_cap'],
                stock['pe_ratio'],
                stock['dividend_yield'],
                datetime.now()
            )
            
            cursor.execute(insert_query, params)
            logger.info(f"Added stock: {stock['code']} - {stock['name']}")
        
        connection.commit()
        logger.info(f"Successfully added {len(sample_stocks)} sample stocks to the database")
        
        return True
        
    except Error as e:
        logger.error(f"Database error: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_sample_stocks() 