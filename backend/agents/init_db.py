#!/usr/bin/env python3
"""
Database initialization script for BullBearPK
"""

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "agents" / "data"
DB_PATH = DATA_DIR / "stocks.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def init_database():
    """Initialize the database with required tables"""
    print(f"Initializing database at {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            risk_tolerance TEXT DEFAULT 'medium',
            investment_goal TEXT DEFAULT 'growth',
            portfolio_value REAL DEFAULT 0.0,
            cash_balance REAL DEFAULT 10000.0,
            preferred_sectors TEXT DEFAULT '[]',
            blacklisted_stocks TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create stock_data table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector TEXT,
            code TEXT NOT NULL,
            name TEXT,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            volume INTEGER,
            change_price REAL,
            change_percent REAL,
            timestamp TIMESTAMP,
            UNIQUE(code, timestamp)
        )
    ''')
    
    # Create investments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            stock_symbol TEXT NOT NULL,
            company_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            purchase_price REAL NOT NULL,
            current_price REAL NOT NULL,
            purchase_date TIMESTAMP NOT NULL,
            sector TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Create recommendations table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            stock_symbol TEXT NOT NULL,
            company_name TEXT NOT NULL,
            recommendation_type TEXT NOT NULL,
            reason TEXT,
            risk_level TEXT,
            expected_return REAL,
            allocation_amount REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Create feedback table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL,
            recommendation_ids TEXT,
            comments TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Create user_preferences table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            budget REAL DEFAULT 10000.0,
            sector TEXT,
            risk_appetite TEXT DEFAULT 'medium',
            time_horizon TEXT DEFAULT 'medium',
            target_profit REAL DEFAULT 15.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Insert demo user if not exists
    conn.execute('''
        INSERT OR IGNORE INTO users (
            user_id, name, email, risk_tolerance, investment_goal,
            portfolio_value, cash_balance, preferred_sectors, blacklisted_stocks
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'demo_user', 'Demo User', 'demo@example.com', 'medium', 'growth',
        10000.0, 10000.0, '[]', '[]'
    ))
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully")

if __name__ == "__main__":
    init_database()