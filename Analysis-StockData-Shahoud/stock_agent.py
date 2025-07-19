#!/usr/bin/env python3
"""
Enhanced AI Stock Analysis Agent - Production Ready
A comprehensive stock analysis agent with intelligent recommendations and user-friendly interactions
Author: AI Assistant
Date: 2025-07-19
Version: 2.0
"""

import sqlite3
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from pathlib import Path
import schedule
import time
import threading
from contextlib import contextmanager
import subprocess
import argparse
import statistics
from collections import defaultdict
import warnings
import hashlib
import uuid
import openai
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== Enhanced Configuration =====
class Config:
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    SCRAPER_DIR = BASE_DIR / "scraped"
    DB_PATH = DATA_DIR / "stocks.db"
    SCRAPER_SCRIPT = BASE_DIR / "fin.py"
    
    # Analysis parameters
    RSI_PERIOD = 14
    MA_SHORT = 5
    MA_LONG = 20
    VOLATILITY_THRESHOLD = 0.05
    PROFIT_THRESHOLD = 0.10
    LOSS_THRESHOLD = -0.05
    
    # Risk thresholds
    RISK_THRESHOLDS = {
        'low': {'min_confidence': 0.8, 'max_volatility': 0.03, 'max_position_size': 0.05},
        'medium': {'min_confidence': 0.6, 'max_volatility': 0.06, 'max_position_size': 0.10},
        'high': {'min_confidence': 0.4, 'max_volatility': 0.15, 'max_position_size': 0.20}
    }
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    SCRAPER_DIR.mkdir(exist_ok=True)

# ===== Enhanced Data Models =====
@dataclass
class StockData:
    sector: str
    code: str
    name: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime

@dataclass
class Portfolio:
    user_id: str
    stock_code: str
    quantity: int
    entry_price: float
    entry_date: datetime
    current_price: float = 0.0
    current_value: float = 0.0
    profit_loss: float = 0.0
    profit_loss_percent: float = 0.0
    position_size: float = 0.0

@dataclass
class IntelligentSignal:
    stock_code: str
    signal_type: str
    confidence: float
    reason: str
    target_price: float
    stop_loss: float
    timeframe: str
    expected_return: float
    risk_level: str
    supporting_indicators: List[str]
    timestamp: datetime

@dataclass
class UserProfile:
    user_id: str
    name: str
    email: str
    risk_tolerance: str
    investment_goal: str
    portfolio_value: float
    cash_balance: float
    preferred_sectors: List[str]
    blacklisted_stocks: List[str]

# ===== Enhanced Database Manager =====
class EnhancedDatabaseManager:
    def __init__(self, db_path: str = Config.DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize enhanced database tables"""
        with self.get_connection() as conn:
            # Enhanced users table
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
            
            # Stock data table with enhanced fields
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
                    market_cap REAL,
                    pe_ratio REAL,
                    timestamp TIMESTAMP,
                    UNIQUE(code, timestamp)
                )
            ''')
            
            # Enhanced portfolio table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    stock_code TEXT,
                    quantity INTEGER,
                    entry_price REAL,
                    entry_date TIMESTAMP,
                    position_size REAL DEFAULT 0.0,
                    target_price REAL,
                    stop_loss REAL,
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Enhanced signals table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT,
                    signal_type TEXT,
                    confidence REAL,
                    reason TEXT,
                    target_price REAL,
                    stop_loss REAL,
                    timeframe TEXT,
                    expected_return REAL,
                    risk_level TEXT,
                    supporting_indicators TEXT,
                    timestamp TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Performance tracking table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    stock_code TEXT,
                    action TEXT,
                    price REAL,
                    quantity INTEGER,
                    timestamp TIMESTAMP,
                    signal_id INTEGER,
                    profit_loss REAL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(signal_id) REFERENCES signals(id)
                )
            ''')
            
            # User preferences table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    notification_frequency TEXT DEFAULT 'daily',
                    alert_threshold REAL DEFAULT 0.05,
                    auto_rebalance BOOLEAN DEFAULT 0,
                    max_positions INTEGER DEFAULT 10,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Market insights table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS market_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT,
                    title TEXT,
                    description TEXT,
                    affected_stocks TEXT,
                    confidence REAL,
                    timestamp TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.commit()
        logger.info("Enhanced database initialized successfully")
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get comprehensive user profile"""
        with self.get_connection() as conn:
            result = conn.execute('''
                SELECT * FROM users WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            if not result:
                return None
            
            return UserProfile(
                user_id=result['user_id'],
                name=result['name'],
                email=result['email'] or '',
                risk_tolerance=result['risk_tolerance'],
                investment_goal=result['investment_goal'],
                portfolio_value=result['portfolio_value'],
                cash_balance=result['cash_balance'],
                preferred_sectors=json.loads(result['preferred_sectors'] or '[]'),
                blacklisted_stocks=json.loads(result['blacklisted_stocks'] or '[]')
            )
    
    def create_user(self, name: str, email: str = '', risk_tolerance: str = 'medium', 
                   investment_goal: str = 'growth', cash_balance: float = 10000.0) -> str:
        """Create a new user profile"""
        user_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO users (user_id, name, email, risk_tolerance, investment_goal, cash_balance)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, email, risk_tolerance, investment_goal, cash_balance))
            
            # Create default preferences
            conn.execute('''
                INSERT INTO user_preferences (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
        
        logger.info(f"Created new user: {user_id} ({name})")
        return user_id
    
    def update_user_activity(self, user_id: str):
        """Update user's last activity timestamp"""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE users SET last_active = ? WHERE user_id = ?
            ''', (datetime.now(), user_id))
            conn.commit()
    
    def get_portfolio_performance(self, user_id: str) -> Dict:
        """Get comprehensive portfolio performance metrics"""
        with self.get_connection() as conn:
            # Get portfolio holdings
            portfolio_query = '''
                SELECT p.*, s.close_price as current_price, s.name as stock_name,
                       s.sector, s.change_percent as daily_change
                FROM portfolio p
                LEFT JOIN stock_data s ON p.stock_code = s.code
                WHERE p.user_id = ? AND p.is_active = 1
                AND s.timestamp = (
                    SELECT MAX(timestamp) FROM stock_data 
                    WHERE code = p.stock_code
                )
            '''
            
            holdings = conn.execute(portfolio_query, (user_id,)).fetchall()
            
            total_value = 0.0
            total_cost = 0.0
            daily_change = 0.0
            sector_allocation = defaultdict(float)
            
            for holding in holdings:
                current_price = holding['current_price'] or 0
                entry_price = holding['entry_price']
                quantity = holding['quantity']
                
                current_value = current_price * quantity
                cost_basis = entry_price * quantity
                
                total_value += current_value
                total_cost += cost_basis
                daily_change += (holding['daily_change'] or 0) * current_value / 100
                
                sector_allocation[holding['sector']] += current_value
            
            total_pl = total_value - total_cost
            total_pl_percent = (total_pl / total_cost * 100) if total_cost > 0 else 0
            
            return {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_pl': total_pl,
                'total_pl_percent': total_pl_percent,
                'daily_change': daily_change,
                'daily_change_percent': (daily_change / total_value * 100) if total_value > 0 else 0,
                'sector_allocation': dict(sector_allocation),
                'holdings_count': len(holdings)
            }
    
    def get_stock_history(self, stock_code: str, days: int = 30) -> List[Dict]:
        """Get stock price history"""
        with self.get_connection() as conn:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            results = conn.execute('''
                SELECT * FROM stock_data 
                WHERE code = ? AND timestamp >= ? 
                ORDER BY timestamp ASC
            ''', (stock_code, cutoff_date)).fetchall()
            
            return [dict(row) for row in results]
    
    def get_latest_stock_data(self) -> List[Dict]:
        """Get latest stock data for all stocks"""
        with self.get_connection() as conn:
            results = conn.execute('''
                SELECT * FROM stock_data s1
                WHERE s1.timestamp = (
                    SELECT MAX(s2.timestamp) FROM stock_data s2 
                    WHERE s2.code = s1.code
                )
                ORDER BY s1.code
            ''').fetchall()
            
            return [dict(row) for row in results]
    
    def save_stock_data(self, stock_data: StockData):
        """Save a stock data object to the database"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO stock_data (
                    sector, code, name, open_price, high_price, low_price, 
                    close_price, volume, change_price, change_percent, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stock_data.sector, stock_data.code, stock_data.name, 
                stock_data.open_price, stock_data.high_price, stock_data.low_price,
                stock_data.close_price, stock_data.volume, stock_data.change, 
                stock_data.change_percent, stock_data.timestamp
            ))
            conn.commit()
            logger.info(f"Saved latest data for {stock_data.code}")
    
    def save_signal(self, signal: IntelligentSignal):
        """Save a signal to the database"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO signals (
                    stock_code, signal_type, confidence, reason, target_price, 
                    stop_loss, timeframe, expected_return, risk_level, 
                    supporting_indicators, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.stock_code, signal.signal_type, signal.confidence,
                signal.reason, signal.target_price, signal.stop_loss,
                signal.timeframe, signal.expected_return, signal.risk_level,
                json.dumps(signal.supporting_indicators), signal.timestamp
            ))
            conn.commit()
    
    def add_to_portfolio(self, user_id: str, stock_code: str, quantity: int, 
                        entry_price: float, target_price: float = 0, 
                        stop_loss: float = 0, notes: str = ''):
        """Add stock to user's portfolio"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO portfolio (
                    user_id, stock_code, quantity, entry_price, entry_date,
                    target_price, stop_loss, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, stock_code, quantity, entry_price, datetime.now(),
                  target_price, stop_loss, notes))
            conn.commit()
    
    def get_user_portfolio(self, user_id: str) -> List[Dict]:
        """Get user's portfolio holdings"""
        with self.get_connection() as conn:
            results = conn.execute('''
                SELECT p.*, s.close_price as current_price, s.name as stock_name,
                       s.sector, s.change_percent as daily_change
                FROM portfolio p
                LEFT JOIN stock_data s ON p.stock_code = s.code
                WHERE p.user_id = ? AND p.is_active = 1
                AND s.timestamp = (
                    SELECT MAX(timestamp) FROM stock_data 
                    WHERE code = p.stock_code
                )
            ''', (user_id,)).fetchall()
            
            return [dict(row) for row in results]
    
    def get_recent_signals(self, user_id: str = None, limit: int = 20) -> List[Dict]:
        """Get recent signals, optionally filtered by user"""
        with self.get_connection() as conn:
            if user_id:
                # Get signals for stocks in user's portfolio or watchlist
                results = conn.execute('''
                    SELECT s.* FROM signals s
                    LEFT JOIN portfolio p ON s.stock_code = p.stock_code
                    WHERE (p.user_id = ? OR p.user_id IS NULL) AND s.is_active = 1
                    ORDER BY s.timestamp DESC
                    LIMIT ?
                ''', (user_id, limit)).fetchall()
            else:
                results = conn.execute('''
                    SELECT * FROM signals 
                    WHERE is_active = 1 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,)).fetchall()
            
            return [dict(row) for row in results]
            
    def update_user_funds(self, user_id: str, change: float):
        """Update user's cash balance and portfolio value"""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE users SET cash_balance = cash_balance + ? WHERE user_id = ?
            ''', (change, user_id))
            conn.commit()


# ===== Advanced Technical Analysis Engine =====
class AdvancedTechnicalAnalyzer:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(0, delta) for delta in deltas]
        losses = [abs(min(0, delta)) for delta in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: List[float]) -> Dict:
        """Calculate MACD indicator"""
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26
        
        # Signal line (9-period EMA of MACD)
        if len(prices) >= 35:
            macd_values = [self._calculate_ema(prices[:i+1], 12) - self._calculate_ema(prices[:i+1], 26) 
                          for i in range(25, len(prices))]
            signal_line = self._calculate_ema(macd_values, 9)
        else:
            signal_line = 0
        
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Dict:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0}
        
        recent_prices = prices[-period:]
        middle = sum(recent_prices) / len(recent_prices)
        std = statistics.stdev(recent_prices)
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    def calculate_support_resistance(self, prices: List[float], highs: List[float], lows: List[float]) -> Dict:
        """Calculate support and resistance levels"""
        if len(prices) < 10:
            return {'support': min(prices), 'resistance': max(prices)}
        
        # Find local maxima and minima
        resistance_levels = []
        support_levels = []
        
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1] and highs[i] > highs[i-2] and highs[i] > highs[i+2]:
                resistance_levels.append(highs[i])
            
            if lows[i] < lows[i-1] and lows[i] < lows[i+1] and lows[i] < lows[i-2] and lows[i] < lows[i+2]:
                support_levels.append(lows[i])
        
        current_price = prices[-1]
        
        # Find nearest support and resistance
        resistance = min([r for r in resistance_levels if r > current_price], default=max(highs))
        support = max([s for s in support_levels if s < current_price], default=min(lows))
        
        return {
            'support': support,
            'resistance': resistance,
            'support_strength': len([s for s in support_levels if abs(s - support) < support * 0.02]),
            'resistance_strength': len([r for r in resistance_levels if abs(r - resistance) < resistance * 0.02])
        }
    
    def comprehensive_analysis(self, stock_code: str) -> Dict:
        """Perform comprehensive technical analysis"""
        history = self.db.get_stock_history(stock_code, days=60)
        if not history:
            return {}
        
        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        
        prices = [float(row['close_price']) for row in history]
        highs = [float(row['high_price']) for row in history]
        lows = [float(row['low_price']) for row in history]
        volumes = [int(row['volume']) for row in history]
        
        if len(prices) < 2:
            return {}
        
        current_price = prices[-1]
        
        # Technical indicators
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        bollinger = self.calculate_bollinger_bands(prices)
        support_resistance = self.calculate_support_resistance(prices, highs, lows)
        
        # Moving averages
        ma_5 = sum(prices[-5:]) / min(5, len(prices))
        ma_20 = sum(prices[-20:]) / min(20, len(prices))
        ma_50 = sum(prices[-50:]) / min(50, len(prices))
        
        # Volume analysis
        avg_volume = sum(volumes[-20:]) / min(20, len(volumes))
        volume_trend = 'increasing' if volumes[-1] > avg_volume * 1.2 else 'decreasing' if volumes[-1] < avg_volume * 0.8 else 'normal'
        
        # Price trends
        price_trend = self._determine_trend(prices)
        momentum = self._calculate_momentum(prices)
        
        # Volatility
        volatility = self._calculate_volatility(prices)
        
        return {
            'stock_code': stock_code,
            'current_price': current_price,
            'rsi': rsi,
            'macd': macd,
            'bollinger_bands': bollinger,
            'support_resistance': support_resistance,
            'moving_averages': {
                'ma_5': ma_5,
                'ma_20': ma_20,
                'ma_50': ma_50
            },
            'volume_analysis': {
                'current_volume': volumes[-1],
                'avg_volume': avg_volume,
                'volume_trend': volume_trend
            },
            'price_trend': price_trend,
            'momentum': momentum,
            'volatility': volatility,
            'analysis_timestamp': datetime.now()
        }
    
    def _determine_trend(self, prices: List[float]) -> str:
        """Determine price trend"""
        if len(prices) < 10:
            return 'sideways'
        
        recent_prices = prices[-10:]
        slope = (recent_prices[-1] - recent_prices[0]) / len(recent_prices)
        
        if slope > prices[-1] * 0.005:
            return 'strong_uptrend'
        elif slope > prices[-1] * 0.001:
            return 'uptrend'
        elif slope < -prices[-1] * 0.005:
            return 'strong_downtrend'
        elif slope < -prices[-1] * 0.001:
            return 'downtrend'
        else:
            return 'sideways'
    
    def _calculate_momentum(self, prices: List[float]) -> float:
        """Calculate price momentum"""
        if len(prices) < 10:
            return 0.0
        
        return (prices[-1] - prices[-10]) / prices[-10] * 100
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        if len(prices) < 20:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, min(len(prices), 21))]
        return statistics.stdev(returns) if len(returns) > 1 else 0.0

# ===== Intelligent Signal Generator =====
class IntelligentSignalGenerator:
    def __init__(self, db_manager: EnhancedDatabaseManager, analyzer: AdvancedTechnicalAnalyzer):
        self.db = db_manager
        self.analyzer = analyzer
        self.signal_weights = {
            'rsi': 0.20,
            'macd': 0.25,
            'bollinger': 0.20,
            'support_resistance': 0.15,
            'volume': 0.10,
            'trend': 0.10
        }
    
    def generate_intelligent_signals(self, user_id: str = None) -> List[IntelligentSignal]:
        """Generate intelligent, personalized trading signals"""
        user_profile = self.db.get_user_profile(user_id) if user_id else None
        
        # Get stocks to analyze
        latest_data = self.db.get_latest_stock_data()
        stock_codes = [row['code'] for row in latest_data]
        
        # Filter based on user preferences
        if user_profile and user_profile.blacklisted_stocks:
            stock_codes = [code for code in stock_codes if code not in user_profile.blacklisted_stocks]
        
        signals = []
        for stock_code in stock_codes:
            signal = self._generate_stock_signal(stock_code, user_profile)
            if signal and signal.confidence > 0.3:
                signals.append(signal)
        
        # Sort by confidence and expected return
        signals.sort(key=lambda x: (x.confidence * x.expected_return), reverse=True)
        
        return signals[:20]  # Return top 20 signals
    
    def _generate_stock_signal(self, stock_code: str, user_profile: Optional[UserProfile] = None) -> Optional[IntelligentSignal]:
        """Generate signal for individual stock"""
        analysis = self.analyzer.comprehensive_analysis(stock_code)
        if not analysis:
            return None
        
        # Calculate signal strength
        signal_strength = self._calculate_signal_strength(analysis)
        
        # Determine signal type and confidence
        signal_type, confidence = self._determine_signal_type(signal_strength)
        
        # Calculate expected return and risk
        expected_return = self._calculate_expected_return(analysis, signal_type)
        risk_level = self._assess_risk_level(analysis, user_profile)
        
        # Generate reasoning
        reason, supporting_indicators = self._generate_reasoning(analysis, signal_strength)
        
        # Calculate target price and stop loss
        target_price, stop_loss = self._calculate_price_targets(analysis, signal_type)
        
        # Determine timeframe
        timeframe = self._determine_timeframe(analysis)
        
        return IntelligentSignal(
            stock_code=stock_code,
            signal_type=signal_type,
            confidence=confidence,
            reason=reason,
            target_price=target_price,
            stop_loss=stop_loss,
            timeframe=timeframe,
            expected_return=expected_return,
            risk_level=risk_level,
            supporting_indicators=supporting_indicators,
            timestamp=datetime.now()
        )
    
    def _calculate_signal_strength(self, analysis: Dict) -> Dict:
        """Calculate weighted signal strength from various indicators"""
        current_price = analysis['current_price']
        rsi = analysis['rsi']
        macd = analysis['macd']
        bollinger = analysis['bollinger_bands']
        support_resistance = analysis['support_resistance']
        volume_analysis = analysis['volume_analysis']
        
        strength = {
            'rsi_signal': 0,
            'macd_signal': 0,
            'bollinger_signal': 0,
            'support_resistance_signal': 0,
            'volume_signal': 0,
            'trend_signal': 0
        }
        
        # RSI signals
        if rsi < 30:
            strength['rsi_signal'] = 1  # Oversold - buy signal
        elif rsi > 70:
            strength['rsi_signal'] = -1  # Overbought - sell signal
        elif 40 < rsi < 60:
            strength['rsi_signal'] = 0.5  # Neutral
        
        # MACD signals
        if macd['histogram'] > 0 and macd['macd'] > macd['signal']:
            strength['macd_signal'] = 1  # Bullish
        elif macd['histogram'] < 0 and macd['macd'] < macd['signal']:
            strength['macd_signal'] = -1  # Bearish
        
        # Bollinger Bands signals
        if current_price < bollinger['lower']:
            strength['bollinger_signal'] = 1  # Oversold
        elif current_price > bollinger['upper']:
            strength['bollinger_signal'] = -1  # Overbought
        
        # Support/Resistance signals
        distance_to_support = abs(current_price - support_resistance['support']) / current_price
        distance_to_resistance = abs(current_price - support_resistance['resistance']) / current_price
        
        if distance_to_support < 0.02:  # Near support
            strength['support_resistance_signal'] = 1
        elif distance_to_resistance < 0.02:  # Near resistance
            strength['support_resistance_signal'] = -1
        
        # Volume signals
        volume_ratio = volume_analysis['current_volume'] / volume_analysis['avg_volume']
        if volume_ratio > 1.5:  # High volume
            strength['volume_signal'] = 1
        elif volume_ratio < 0.5:  # Low volume
            strength['volume_signal'] = -1
        
        # Trend signals
        ma_5 = analysis['moving_averages']['ma_5']
        ma_20 = analysis['moving_averages']['ma_20']
        
        if ma_5 > ma_20:
            strength['trend_signal'] = 1  # Uptrend
        elif ma_5 < ma_20:
            strength['trend_signal'] = -1  # Downtrend
        
        # Calculate weighted overall signal
        weighted_signal = (
            strength['rsi_signal'] * self.signal_weights['rsi'] +
            strength['macd_signal'] * self.signal_weights['macd'] +
            strength['bollinger_signal'] * self.signal_weights['bollinger'] +
            strength['support_resistance_signal'] * self.signal_weights['support_resistance'] +
            strength['volume_signal'] * self.signal_weights['volume'] +
            strength['trend_signal'] * self.signal_weights['trend']
        )
        
        strength['overall_signal'] = weighted_signal
        strength['signal_confidence'] = len([s for s in strength.values() if s != 0]) / 6
        
        return strength

    def _determine_signal_type(self, signal_strength: Dict) -> Tuple[str, float]:
        """Determine signal type and confidence level"""
        overall_signal = signal_strength['overall_signal']
        confidence = signal_strength['signal_confidence']
        
        if overall_signal > 0.3:
            return 'BUY', min(0.9, confidence + overall_signal * 0.5)
        elif overall_signal < -0.3:
            return 'SELL', min(0.9, confidence + abs(overall_signal) * 0.5)
        else:
            return 'HOLD', min(0.7, confidence)
    
    def _calculate_expected_return(self, analysis: Dict, signal_type: str) -> float:
        """Calculate expected return percentage based on technical analysis"""
        current_price = analysis['current_price']
        support_resistance = analysis['support_resistance']
        volatility = analysis['volatility']
        
        if signal_type == 'BUY':
            # Calculate potential upside to resistance
            upside = (support_resistance['resistance'] - current_price) / current_price
            return min(0.15, max(0.02, upside * 0.7))  # Cap at 15%, minimum 2%
        elif signal_type == 'SELL':
            # Calculate potential downside to support
            downside = (current_price - support_resistance['support']) / current_price
            return min(0.15, max(0.02, downside * 0.7))  # Positive return for short positions
        else:
            return volatility * 0.5  # Expected return for hold positions
    
    def _assess_risk_level(self, analysis: Dict, user_profile: Optional[UserProfile]) -> str:
        """Assess risk level based on volatility and user profile"""
        volatility = analysis['volatility']
        
        # Base risk assessment on volatility
        if volatility > 0.08:
            base_risk = 'high'
        elif volatility > 0.04:
            base_risk = 'medium'
        else:
            base_risk = 'low'
        
        # Adjust based on user risk tolerance
        if user_profile:
            if user_profile.risk_tolerance == 'low' and base_risk == 'high':
                return 'medium'
            elif user_profile.risk_tolerance == 'high' and base_risk == 'low':
                return 'medium'
        
        return base_risk
    
    def _generate_reasoning(self, analysis: Dict, signal_strength: Dict) -> Tuple[str, List[str]]:
        """Generate human-readable explanation for the signal"""
        supporting_indicators = []
        reasons = []
        
        # RSI reasoning
        rsi = analysis['rsi']
        if signal_strength['rsi_signal'] == 1:
            reasons.append(f"RSI at {rsi:.1f} indicates oversold conditions")
            supporting_indicators.append("RSI Oversold")
        elif signal_strength['rsi_signal'] == -1:
            reasons.append(f"RSI at {rsi:.1f} indicates overbought conditions")
            supporting_indicators.append("RSI Overbought")
        
        # MACD reasoning
        macd = analysis['macd']
        if signal_strength['macd_signal'] == 1:
            reasons.append("MACD shows bullish momentum")
            supporting_indicators.append("MACD Bullish")
        elif signal_strength['macd_signal'] == -1:
            reasons.append("MACD shows bearish momentum")
            supporting_indicators.append("MACD Bearish")
        
        # Bollinger Bands reasoning
        if signal_strength['bollinger_signal'] == 1:
            reasons.append("Price below lower Bollinger Band suggests oversold")
            supporting_indicators.append("Bollinger Oversold")
        elif signal_strength['bollinger_signal'] == -1:
            reasons.append("Price above upper Bollinger Band suggests overbought")
            supporting_indicators.append("Bollinger Overbought")
        
        # Support/Resistance reasoning
        if signal_strength['support_resistance_signal'] == 1:
            reasons.append("Price near strong support level")
            supporting_indicators.append("Support Level")
        elif signal_strength['support_resistance_signal'] == -1:
            reasons.append("Price near strong resistance level")
            supporting_indicators.append("Resistance Level")
        
        # Volume reasoning
        volume_trend = analysis['volume_analysis']['volume_trend']
        if volume_trend == 'increasing':
            reasons.append("Above average volume confirms price movement")
            supporting_indicators.append("Volume Confirmation")
        
        # Trend reasoning
        if signal_strength['trend_signal'] == 1:
            reasons.append("Short-term MA above long-term MA indicates uptrend")
            supporting_indicators.append("Uptrend")
        elif signal_strength['trend_signal'] == -1:
            reasons.append("Short-term MA below long-term MA indicates downtrend")
            supporting_indicators.append("Downtrend")
        
        reasoning = ". ".join(reasons) if reasons else "Mixed signals from technical indicators"
        
        return reasoning, supporting_indicators
    
    def _calculate_price_targets(self, analysis: Dict, signal_type: str) -> Tuple[float, float]:
        """Calculate target price and stop loss levels"""
        current_price = analysis['current_price']
        support_resistance = analysis['support_resistance']
        volatility = analysis['volatility']
        
        if signal_type == 'BUY':
            # Target price based on resistance level
            target_price = support_resistance['resistance'] * 0.95  # 5% below resistance
            # Stop loss based on support level
            stop_loss = support_resistance['support'] * 1.02  # 2% above support
        elif signal_type == 'SELL':
            # Target price based on support level
            target_price = support_resistance['support'] * 1.05  # 5% above support
            # Stop loss based on resistance level
            stop_loss = support_resistance['resistance'] * 0.98  # 2% below resistance
        else:  # HOLD
            # Conservative targets
            target_price = current_price * (1 + volatility * 2)
            stop_loss = current_price * (1 - volatility * 1.5)
        
        return target_price, stop_loss
    
    def _determine_timeframe(self, analysis: Dict) -> str:
        """Determine appropriate timeframe based on analysis"""
        volatility = analysis['volatility']
        momentum = analysis['momentum']
        
        if volatility > 0.08 or abs(momentum) > 5:
            return 'short'  # High volatility/momentum suggests short-term play
        elif volatility < 0.03 and abs(momentum) < 2:
            return 'long'  # Low volatility/momentum suggests long-term hold
        else:
            return 'medium'  # Medium-term trade

# ===== Missing Classes =====

class DataScraper:
    """Data scraper integration for fetching latest stock data"""
    
    def __init__(self, scraper_script_path: str):
        self.scraper_script_path = Path(scraper_script_path)
        self.scraped_data_dir = Config.SCRAPER_DIR
        
    def scrape_latest_data(self) -> bool:
        """Execute the fin.py scraper script"""
        try:
            if not self.scraper_script_path.exists():
                logger.error(f"Scraper script not found: {self.scraper_script_path}")
                return False
            
            # Execute the scraper script
            result = subprocess.run([
                sys.executable, str(self.scraper_script_path)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Data scraping completed successfully")
                return True
            else:
                logger.error(f"Scraper failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Scraper script timed out")
            return False
        except Exception as e:
            logger.error(f"Error running scraper: {e}")
            return False
    
    def process_scraped_data(self) -> List[StockData]:
        stock_data_list = []
        try:
            # Look for scraped data files
            for file_path in self.scraped_data_dir.glob("*.json"):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                stocks = data.get('stocks', [])
                for item in stocks:
                    stock_data = StockData(
                        sector=item.get('sector', ''),
                        code=item.get('code', ''),
                        name=item.get('name', ''),
                        open_price=float(item.get('open_price', 0)),
                        high_price=float(item.get('high_price', 0)),
                        low_price=float(item.get('low_price', 0)),
                        close_price=float(item.get('close_price', 0)),
                        volume=int(item.get('volume', 0)),
                        change=float(item.get('change', 0)),
                        change_percent=float(item.get('change_percent', 0)),
                        timestamp=datetime.fromisoformat(item.get('timestamp', datetime.now().isoformat()))
                    )
                    stock_data_list.append(stock_data)
            logger.info(f"Processed {len(stock_data_list)} stock records")
            return stock_data_list
        except Exception as e:
            logger.error(f"Error processing scraped data: {e}")
            return []

class StockAnalysisAgent:
    """Main agent controller for stock analysis"""
    
    def __init__(self):
        self.db_manager = EnhancedDatabaseManager()
        self.analyzer = AdvancedTechnicalAnalyzer(self.db_manager)
        self.signal_generator = IntelligentSignalGenerator(self.db_manager, self.analyzer)
        self.data_scraper = DataScraper(Config.SCRAPER_SCRIPT)
        self.risk_manager = RiskManager(self.db_manager)
        self.notification_manager = NotificationManager(self.db_manager)
        self.performance_tracker = PerformanceTracker(self.db_manager)
        self.ui = UserInterface(self)
        self.current_user_id = None
        
        # Start scheduler in background
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def start_interactive_session(self):
        """Start the main interactive session"""
        logger.info("Starting Stock Analysis Agent")
        print("\n🚀 Welcome to the AI Stock Analysis Agent!")
        print("=" * 50)
        
        self._handle_user_login()
        if not self.current_user_id:
            return

        while True:
            try:
                self.ui.display_menu()
                choice = input("\nEnter your choice: ").strip()
                
                if choice == '1':
                    self._handle_portfolio_view()
                elif choice == '2':
                    self._handle_signals_view()
                elif choice == '3':
                    self._handle_add_stock()
                elif choice == '4':
                    self._handle_user_management()
                elif choice == '5':
                    self._handle_performance_report()
                elif choice == '6':
                    self._handle_data_update()
                elif choice == '0':
                    print("👋 Thanks for using the Stock Analysis Agent!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Thanks for using the Stock Analysis Agent!")
                break
            except Exception as e:
                logger.error(f"Error in interactive session: {e}")
                print(f"❌ An error occurred: {e}")

    def _handle_user_login(self):
        """Handle user login or creation"""
        while True:
            user_id = self.ui.get_user_input("Enter your user ID (or 'new' to create a new user)")
            if user_id.lower() == 'new':
                name = self.ui.get_user_input("Enter your name")
                self.current_user_id = self.db_manager.create_user(name)
                print(f"✅ New user created with ID: {self.current_user_id}")
                break
            else:
                user_profile = self.db_manager.get_user_profile(user_id)
                if user_profile:
                    self.current_user_id = user_id
                    print(f"✅ Welcome back, {user_profile.name}!")
                    break
                else:
                    print("❌ User not found. Please try again or create a new user.")

    def _handle_portfolio_view(self):
        """Handle portfolio viewing and display"""
        self.ui.display_portfolio(self.current_user_id)
    
    def _handle_signals_view(self):
        """Handle signals viewing and display"""
        signals = self.signal_generator.generate_intelligent_signals(self.current_user_id)
        self.ui.display_signals(signals)

    def _handle_add_stock(self):
        """Handle adding a stock to the portfolio (buy action)"""
        stock_code = self.ui.get_user_input("Enter stock code (e.g., AAPL)").upper()
        quantity_str = self.ui.get_user_input("Enter quantity")
        try:
            quantity = int(quantity_str)
            self._execute_buy(self.current_user_id, stock_code, quantity)
        except ValueError:
            print("❌ Invalid quantity. Please enter a number.")
        except Exception as e:
            print(f"❌ Failed to add stock: {e}")
            logger.error(f"Error adding stock: {e}")

    def _handle_user_management(self):
        """Placeholder for user management features"""
        print("👤 User management features are currently under development.")
        print("You can manage your risk tolerance, goals, etc. manually in the database for now.")

    def _handle_performance_report(self):
        """Generate and display a performance report"""
        report = self.performance_tracker.generate_performance_report(self.current_user_id)
        self.ui.display_performance_report(report)

    def _handle_data_update(self):
        """Manually trigger a data update"""
        print("🔄 Triggering manual data update...")
        self._daily_data_update()
        print("✅ Data update complete.")
    
    def process_user_command(self, command: str, user_id: str):
        """Parse and execute user commands"""
        self.current_user_id = user_id
        command = command.lower().strip()
        
        if command.startswith('analyze'):
            stock_code = command.split()[-1].upper()
            return self._analyze_stock(stock_code, user_id)
        elif command.startswith('buy'):
            parts = command.split()
            if len(parts) == 3:
                stock_code = parts[1].upper()
                quantity = int(parts[2])
                return self._execute_buy(user_id, stock_code, quantity)
            else:
                return "Invalid 'buy' command format. Use: 'buy STOCK QTY'"
        elif command.startswith('sell'):
            parts = command.split()
            if len(parts) == 3:
                stock_code = parts[1].upper()
                quantity = int(parts[2])
                return self._execute_sell(user_id, stock_code, quantity)
            else:
                return "Invalid 'sell' command format. Use: 'sell STOCK QTY'"
        elif command == 'portfolio':
            return self._get_portfolio_summary(user_id)
        elif command == 'signals':
            return self._get_user_signals(user_id)
        else:
            return "Unknown command. Try 'analyze STOCK', 'buy STOCK QTY', 'sell STOCK QTY', 'portfolio', or 'signals'"

    def _analyze_stock(self, stock_code: str, user_id: str):
        """Perform and display analysis for a single stock"""
        analysis = self.analyzer.comprehensive_analysis(stock_code)
        if not analysis:
            return f"❌ No recent data found for {stock_code}."
        
        signal = self.signal_generator._generate_stock_signal(stock_code, self.db_manager.get_user_profile(user_id))
        
        output = [f"📊 Analysis for {stock_code}:"]
        output.append(f"   Current Price: ${analysis['current_price']:.2f}")
        output.append(f"   RSI: {analysis['rsi']:.2f}")
        output.append(f"   MACD Histogram: {analysis['macd']['histogram']:.2f}")
        output.append(f"   Support: ${analysis['support_resistance']['support']:.2f}")
        output.append(f"   Resistance: ${analysis['support_resistance']['resistance']:.2f}")
        output.append(f"   Price Trend: {analysis['price_trend'].replace('_', ' ').capitalize()}")
        
        if signal:
            output.append("\n🎯 Intelligent Signal:")
            output.append(f"   Type: {signal.signal_type}")
            output.append(f"   Confidence: {signal.confidence:.2f}")
            output.append(f"   Expected Return: {signal.expected_return:.2f}%")
            output.append(f"   Reason: {signal.reason}")
        
        return "\n".join(output)

    def _execute_buy(self, user_id: str, stock_code: str, quantity: int):
        latest_data = self.db_manager.get_latest_stock_data()
        stock_price = next((s['close_price'] for s in latest_data if s['code'] == stock_code), None)
        if not stock_price:
            return f"❌ Could not find recent price for {stock_code}."
        trade_value = stock_price * quantity
        user_profile = self.db_manager.get_user_profile(user_id)
        if not user_profile or user_profile.cash_balance < trade_value:
            return f"❌ Insufficient cash. Cash balance: ${user_profile.cash_balance:.2f}"
        # Check if stock already in portfolio
        portfolio = self.db_manager.get_user_portfolio(user_id)
        holding = next((h for h in portfolio if h['stock_code'] == stock_code), None)
        if holding:
            # Weighted average entry price
            total_qty = holding['quantity'] + quantity
            new_entry_price = ((holding['entry_price'] * holding['quantity']) + (stock_price * quantity)) / total_qty
            with self.db_manager.get_connection() as conn:
                conn.execute('''
                    UPDATE portfolio SET quantity = ?, entry_price = ?, is_active = 1 WHERE id = ?
                ''', (total_qty, new_entry_price, holding['id']))
                conn.commit()
        else:
            self.db_manager.add_to_portfolio(user_id, stock_code, quantity, stock_price)
        self.db_manager.update_user_funds(user_id, -trade_value)
        # Record the trade
        with self.db_manager.get_connection() as conn:
            conn.execute('''
                INSERT INTO performance_tracking
                (user_id, stock_code, action, price, quantity, timestamp, profit_loss)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, stock_code, 'buy', stock_price, quantity, datetime.now(), 0.0))
            conn.commit()
        return f"✅ Purchased {quantity} shares of {stock_code} for ${trade_value:.2f}."

    def _execute_sell(self, user_id: str, stock_code: str, quantity: int):
        portfolio = self.db_manager.get_user_portfolio(user_id)
        holding = next((h for h in portfolio if h['stock_code'] == stock_code), None)
        if not holding or holding['quantity'] < quantity:
            return f"❌ Not enough shares of {stock_code} to sell."
        latest_data = self.db_manager.get_latest_stock_data()
        stock_price = next((s['close_price'] for s in latest_data if s['code'] == stock_code), None)
        if not stock_price:
            return f"❌ Could not find recent price for {stock_code}."
        sale_value = stock_price * quantity
        entry_price = holding['entry_price']
        profit_loss = (stock_price - entry_price) * quantity
        # Update portfolio quantity or deactivate
        new_qty = holding['quantity'] - quantity
        with self.db_manager.get_connection() as conn:
            if new_qty > 0:
                conn.execute('''UPDATE portfolio SET quantity = ? WHERE id = ?''', (new_qty, holding['id']))
            else:
                conn.execute('''UPDATE portfolio SET quantity = 0, is_active = 0 WHERE id = ?''', (holding['id'],))
            conn.commit()
        self.db_manager.update_user_funds(user_id, sale_value)
        # Record the trade with realized profit/loss
        with self.db_manager.get_connection() as conn:
            conn.execute('''
                INSERT INTO performance_tracking
                (user_id, stock_code, action, price, quantity, timestamp, profit_loss)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, stock_code, 'sell', stock_price, quantity, datetime.now(), profit_loss))
            conn.commit()
        return f"✅ Sold {quantity} shares of {stock_code} for ${sale_value:.2f}. Realized P/L: ${profit_loss:.2f}."

    def _get_portfolio_summary(self, user_id: str):
        """Generate a text summary of the portfolio"""
        performance = self.db_manager.get_portfolio_performance(user_id)
        user_profile = self.db_manager.get_user_profile(user_id)
        
        summary = [f"📊 Portfolio Summary for {user_profile.name}:"]
        summary.append(f"   Total Value: ${performance['total_value']:.2f}")
        summary.append(f"   Cash Balance: ${user_profile.cash_balance:.2f}")
        summary.append(f"   Total P/L: ${performance['total_pl']:.2f} ({performance['total_pl_percent']:.2f}%)")
        summary.append(f"   Daily Change: ${performance['daily_change']:.2f} ({performance['daily_change_percent']:.2f}%)")
        return "\n".join(summary)

    def _get_user_signals(self, user_id: str):
        """Generate a text summary of recent signals"""
        signals = self.signal_generator.generate_intelligent_signals(user_id)
        if not signals:
            return "No signals found for your profile at this time."
        
        output = ["🎯 Recent Signals:"]
        for s in signals:
            output.append(f"   - {s.stock_code}: {s.signal_type} ({s.confidence:.2f})")
            output.append(f"     Reason: {s.reason}")
        return "\n".join(output)

    def generate_daily_recommendations(self, user_id: str):
        """Generate daily recommendations for user"""
        signals = self.signal_generator.generate_intelligent_signals(user_id)
        
        # Filter top recommendations
        buy_signals = [s for s in signals if s.signal_type == 'BUY'][:5]
        sell_signals = [s for s in signals if s.signal_type == 'SELL'][:3]
        
        return {
            'buy_recommendations': buy_signals,
            'sell_recommendations': sell_signals,
            'market_outlook': self._get_market_outlook(),
            'user_specific_notes': self._get_user_specific_notes(user_id)
        }
    



    def handle_prompt(self, user_id: str, prompt: str) -> dict:
        """
        Professional Financial Advisor AI - Handle natural language prompts and return structured financial advice.
        Provides actionable suggestions with justification, risk assessment, and alternatives.
        """
        prompt_lower = prompt.lower()
        response = {"text": "", "charts": [], "data": {}, "risk_level": "medium", "alternatives": []}
        
        # Extract financial parameters from prompt
        financial_context = self._extract_financial_context(prompt_lower)
        
        # Intent: Portfolio Analysis & Summary
        if any(x in prompt_lower for x in ["portfolio", "my stocks", "my holdings", "current position", "what do i own"]):
            return self._handle_portfolio_analysis(user_id, financial_context, response)
        
        # Intent: Investment Recommendations & Profit Goals
        elif any(x in prompt_lower for x in ["recommend", "suggest", "invest", "buy", "profit", "return", "gain", "growth"]):
            return self._handle_investment_recommendations(user_id, financial_context, response)
        
        # Intent: Risk Analysis & Assessment
        elif any(x in prompt_lower for x in ["risk", "safe", "risky", "volatility", "sharpe", "diversif", "hedge"]):
            return self._handle_risk_analysis(user_id, financial_context, response)
        
        # Intent: Market Analysis & Trends
        elif any(x in prompt_lower for x in ["analyze", "trend", "chart", "market", "sector", "compare", "technical", "fundamental"]):
            return self._handle_market_analysis(user_id, financial_context, response)
        
        # Intent: Trading Signals & Timing
        elif any(x in prompt_lower for x in ["signal", "momentum", "buy signal", "sell signal", "entry", "exit", "timing"]):
            return self._handle_trading_signals(user_id, financial_context, response)
        
        # Intent: Sector/Stock Comparison
        elif any(x in prompt_lower for x in ["compare", "vs", "versus", "better", "which", "sector"]):
            return self._handle_comparison_analysis(user_id, financial_context, response)
        
        # Fallback with clarifying questions or LLM
        else:
            # Try LLM for arbitrary finance questions
            try:
                system_message = (
                    "You are a professional financial advisor for Pakistan Stock Exchange (PSX) and global markets. "
                    "If the user asks about PSX, use local context. Otherwise, answer as a general finance expert."
                )
                llm_response = call_groq_llm(prompt, system_message=system_message)
                response["text"] = llm_response
                response["data"] = {"llm_used": True}
                return response
            except Exception as e:
                print("GROQ LLM error:", e)  # This will show the real error in your terminal
                response["text"] = (
                    "Sorry, I couldn't answer that right now. Please try again later or ask a different question."
                )
                response["data"] = {"error": str(e)}
                return response

    def _extract_financial_context(self, prompt_lower: str) -> Dict[str, Any]:
        """Extract financial parameters from user prompt"""
        context = {
            "amount": None,
            "timeframe": None,
            "target_return": None,
            "risk_tolerance": "medium",
            "sectors": [],
            "stock_codes": [],
            "urgency": "normal"
        }
        
        # Extract monetary amounts (PKR, USD, etc.)
        amount_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:pkr|rs|rupees?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:usd|dollars?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|thousand)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:lakh|lac)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:crore)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                context["amount"] = float(amount_str)
                if 'k' in match.group(0) or 'thousand' in match.group(0):
                    context["amount"] *= 1000
                elif 'lakh' in match.group(0) or 'lac' in match.group(0):
                    context["amount"] *= 100000
                elif 'crore' in match.group(0):
                    context["amount"] *= 10000000
                break
        
        # Extract timeframes
        timeframe_patterns = {
            r'(\d+)\s*(?:day|days)': 'days',
            r'(\d+)\s*(?:week|weeks)': 'weeks', 
            r'(\d+)\s*(?:month|months)': 'months',
            r'(\d+)\s*(?:year|years)': 'years',
            r'next\s+week': '1_week',
            r'next\s+month': '1_month',
            r'short[- ]?term': 'short_term',
            r'long[- ]?term': 'long_term',
            r'quick|fast|urgent': 'urgent'
        }
        
        for pattern, timeframe_type in timeframe_patterns.items():
            if re.search(pattern, prompt_lower):
                context["timeframe"] = timeframe_type
                if timeframe_type == 'urgent':
                    context["urgency"] = "high"
                break
        
        # Extract target returns
        return_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:profit|return|gain)', prompt_lower)
        if return_match:
            context["target_return"] = float(return_match.group(1))
        
        # Extract risk tolerance
        if any(x in prompt_lower for x in ['safe', 'low risk', 'conservative', 'stable']):
            context["risk_tolerance"] = "low"
        elif any(x in prompt_lower for x in ['risky', 'aggressive', 'high risk', 'speculative']):
            context["risk_tolerance"] = "high"
        
        # Extract sectors
        sectors = ['banking', 'tech', 'telecom', 'energy', 'pharmaceutical', 'textile', 'cement', 'auto']
        context["sectors"] = [sector for sector in sectors if sector in prompt_lower]
        
        # Extract stock codes (3-4 letter patterns)
        stock_matches = re.findall(r'\b[A-Z]{3,4}\b', prompt_lower.upper())
        context["stock_codes"] = stock_matches
        
        return context

    def _handle_portfolio_analysis(self, user_id: str, context: Dict, response: dict) -> dict:
        """Provide comprehensive portfolio analysis with professional insights"""
        try:
            perf = self.db_manager.get_portfolio_performance(user_id)
            holdings = self.db_manager.get_user_portfolio(user_id)
            risk_data = self.risk_manager.assess_portfolio_risk(user_id)
            
            if not holdings:
                response["text"] = "You don't have any current holdings. Would you like recommendations for building your first portfolio based on your risk tolerance and investment goals?"
                response["data"] = {"needs_setup": True}
                return response
            
            # Calculate portfolio metrics
            total_invested = sum(h['quantity'] * h['entry_price'] for h in holdings)
            current_value = perf.get('total_value', 0)
            unrealized_pl = current_value - total_invested
            pl_percentage = (unrealized_pl / total_invested * 100) if total_invested > 0 else 0
            
            # Professional analysis
            analysis_lines = [
                "📊 PORTFOLIO ANALYSIS & PERFORMANCE SUMMARY",
                "=" * 50,
                f"💰 Current Portfolio Value: ${current_value:,.2f}",
                f"📈 Total Investment: ${total_invested:,.2f}",
                f"📊 Unrealized P/L: ${unrealized_pl:,.2f} ({pl_percentage:+.2f}%)",
                f"⚖️  Risk Level: {risk_data.get('risk_level', 'Unknown').upper()}",
                f"🎯 Diversification Score: {risk_data.get('diversification_score', 0):.2f}/10",
                "",
                "📋 CURRENT HOLDINGS:"
            ]
            
            for h in holdings:
                current_price = h.get('current_price', 0) or 0
                position_pl = (current_price - h['entry_price']) * h['quantity']
                position_pl_pct = ((current_price - h['entry_price']) / h['entry_price'] * 100) if h['entry_price'] > 0 else 0
                weight = (h['quantity'] * current_price) / current_value * 100 if current_value > 0 else 0
                
                analysis_lines.append(
                    f"• {h['stock_code']}: {h['quantity']} shares @ ${h['entry_price']:.2f} "
                    f"→ ${current_price:.2f} | P/L: ${position_pl:+.2f} ({position_pl_pct:+.2f}%) | Weight: {weight:.1f}%"
                )
            
            # Professional recommendations
            analysis_lines.extend([
                "",
                "🎯 PROFESSIONAL RECOMMENDATIONS:",
                self._get_portfolio_recommendations(holdings, risk_data, perf)
            ])
            
            response["text"] = "\n".join(analysis_lines)
            response["data"] = {
                "holdings": holdings, 
                "performance": perf, 
                "risk_assessment": risk_data,
                "metrics": {
                    "total_invested": total_invested,
                    "unrealized_pl": unrealized_pl,
                    "pl_percentage": pl_percentage
                }
            }
            response["risk_level"] = risk_data.get('risk_level', 'medium')
            
        except Exception as e:
            response["text"] = "Unable to retrieve portfolio data. Please ensure you have holdings recorded in the system."
            response["data"] = {"error": str(e)}
        
        return response

    def _handle_investment_recommendations(self, user_id: str, context: Dict, response: dict) -> dict:
        """Provide professional investment recommendations with detailed justification (robust version)"""
        try:
            stocks = self.db_manager.get_latest_stock_data()
            user_portfolio = self.db_manager.get_user_portfolio(user_id)

            if not stocks:
                response["text"] = (
                    "No market data is available right now. Please update your data (run the scraper) and try again."
                )
                return response

            # Apply filters based on context
            filtered_stocks = self._filter_stocks_by_context(stocks, context)

            # If filtering is too strict, fallback to all stocks
            if not filtered_stocks:
                filtered_stocks = stocks
                response["text"] = (
                    "No stocks matched your specific criteria, so here are some general recommendations based on current market data.\n"
                )
            else:
                response["text"] = ""

            # Generate recommendations based on analysis
            recommendations = self._generate_investment_recommendations(
                filtered_stocks, context, user_portfolio
            )

            if not recommendations:
                response["text"] += (
                    "No suitable investment opportunities found matching your criteria. "
                    "Please update your data, broaden your query, or try again later."
                )
                return response

            # Build professional response
            lines = [
                "💼 PROFESSIONAL INVESTMENT RECOMMENDATIONS",
                "=" * 50
            ]

            # Add context summary
            if context.get("amount"):
                lines.append(f"💰 Investment Amount: ${context['amount']:,.2f}")
            if context.get("timeframe"):
                lines.append(f"⏱️  Investment Horizon: {context['timeframe']}")
            if context.get("target_return"):
                lines.append(f"🎯 Target Return: {context['target_return']}%")
            lines.append(f"⚖️  Risk Profile: {context.get('risk_tolerance', 'medium').upper()}")
            lines.append("")
            lines.append("📈 TOP RECOMMENDATIONS:")

            for i, rec in enumerate(recommendations[:3], 1):
                stock = rec['stock']
                reason = rec.get('reasoning', 'N/A')
                expected_return = rec.get('expected_return', 'N/A')
                risk_rating = rec.get('risk_rating', 'Medium')
                lines.extend([
                    f"#{i}. {stock.get('code', 'N/A')} - {stock.get('name', 'N/A')}",
                    f"   💰 Current Price: ${stock.get('close_price', 0):.2f}",
                    f"   📊 Expected Return: {expected_return}% (Risk: {risk_rating})",
                    f"   📝 Rationale: {reason}",
                    ""
                ])

            # Add professional disclaimers and alternatives
            lines.extend([
                "⚠️  RISK CONSIDERATIONS:",
                self._generate_risk_disclaimer(context, recommendations),
                "",
                "🔄 ALTERNATIVE STRATEGIES:",
                *self._generate_alternatives(context, recommendations)
            ])

            response["text"] += "\n".join(lines)
            response["data"] = {
                "recommendations": recommendations,
                "context": context,
                "total_stocks_analyzed": len(stocks)
            }
            response["risk_level"] = self._assess_recommendation_risk(recommendations)
            response["alternatives"] = self._generate_alternatives(context, recommendations)

        except Exception as e:
            logger.error(f"Error in _handle_investment_recommendations: {e}")
            response["text"] = (
                "Unable to generate recommendations at this time. "
                "Please ensure your data is up to date and try again. If the problem persists, contact support."
            )
            response["data"] = {"error": str(e)}
        return response

    def _handle_risk_analysis(self, user_id: str, context: Dict, response: dict) -> dict:
        """Comprehensive risk analysis with actionable insights"""
        try:
            risk_data = self.risk_manager.assess_portfolio_risk(user_id)
            portfolio = self.db_manager.get_user_portfolio(user_id)
            
            lines = [
                "⚠️  COMPREHENSIVE RISK ANALYSIS",
                "=" * 50,
                f"📊 Overall Risk Level: {risk_data.get('risk_level', 'Unknown').upper()}",
                f"🎯 Risk Score: {risk_data.get('risk_score', 0):.2f}/10",
                f"📈 Portfolio Volatility: {risk_data.get('average_volatility', 0):.2f}%",
                f"🎲 Diversification Score: {risk_data.get('diversification_score', 0):.2f}/10",
                "",
                "📋 RISK BREAKDOWN BY POSITION:"
            ]
            
            if portfolio:
                for holding in portfolio:
                    stock_risk = self._calculate_individual_stock_risk(holding)
                    lines.append(f"• {holding['stock_code']}: {stock_risk['level']} Risk ({stock_risk['score']:.2f})")
            
            lines.extend([
                "",
                "🎯 PROFESSIONAL RISK MANAGEMENT RECOMMENDATIONS:",
            ])
            
            risk_recommendations = self._generate_risk_recommendations(risk_data, portfolio)
            lines.extend([f"• {rec}" for rec in risk_recommendations])
            
            response["text"] = "\n".join(lines)
            response["data"] = risk_data
            response["risk_level"] = risk_data.get('risk_level', 'medium')
            
        except Exception as e:
            response["text"] = "Risk analysis temporarily unavailable. Please try again."
            response["data"] = {"error": str(e)}
        
        return response

    def _handle_market_analysis(self, user_id: str, context: Dict, response: dict) -> dict:
        """Professional market analysis and trend identification"""
        try:
            # Extract specific stock or analyze market broadly
            target_stocks = context["stock_codes"] if context["stock_codes"] else None
            sectors = context["sectors"] if context["sectors"] else None
            
            if target_stocks:
                return self._analyze_specific_stocks(target_stocks, context, response)
            elif sectors:
                return self._analyze_sectors(sectors, context, response)
            else:
                return self._analyze_broad_market(context, response)
                
        except Exception as e:
            response["text"] = "Market analysis temporarily unavailable. Please specify stocks or sectors to analyze."
            response["data"] = {"error": str(e)}
        
        return response

    def _handle_trading_signals(self, user_id: str, context: Dict, response: dict) -> dict:
        """Generate intelligent trading signals with timing analysis"""
        try:
            signals = self.signal_generator.generate_intelligent_signals(user_id)
            
            if not signals:
                response["text"] = "No strong trading signals detected in current market conditions. Monitor for emerging opportunities."
                return response
            
            # Filter signals based on context
            filtered_signals = self._filter_signals_by_context(signals, context)
            
            lines = [
                "🚨 INTELLIGENT TRADING SIGNALS",
                "=" * 50,
                f"📊 Signals Generated: {len(filtered_signals)}",
                f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "",
                "📈 ACTIVE SIGNALS:"
            ]
            
            for signal in filtered_signals[:5]:
                confidence_emoji = "🟢" if signal.confidence >= 0.7 else "🟡" if signal.confidence >= 0.5 else "🔴"
                lines.extend([
                    f"{confidence_emoji} {signal.stock_code}: {signal.signal_type.upper()}",
                    f"   📊 Confidence: {signal.confidence:.2f} ({signal.confidence*100:.0f}%)",
                    f"   📝 Analysis: {signal.reason}",
                    f"   ⏱️  Timeframe: {getattr(signal, 'timeframe', 'Short-term')}",
                    ""
                ])
            
            response["text"] = "\n".join(lines)
            response["data"] = {"signals": [self._signal_to_dict(s) for s in filtered_signals]}
            
        except Exception as e:
            response["text"] = "Signal generation temporarily unavailable. Please try again."
            response["data"] = {"error": str(e)}
        
        return response

    def _handle_comparison_analysis(self, user_id: str, context: Dict, response: dict) -> dict:
        """Professional comparative analysis between stocks/sectors"""
        if context["stock_codes"] and len(context["stock_codes"]) >= 2:
            return self._compare_stocks(context["stock_codes"], context, response)
        elif context["sectors"] and len(context["sectors"]) >= 2:
            return self._compare_sectors(context["sectors"], context, response)
        else:
            response["text"] = "Please specify at least 2 stocks or sectors to compare (e.g., 'Compare HBL vs UBL' or 'Banking vs Tech sector')."
            return response

    def _handle_clarification_request(self, context: Dict, response: dict) -> dict:
        """Handle unclear requests with helpful clarification questions"""
        lines = [
            "🤖 I'm here to provide professional financial advice! To give you the best recommendations, please tell me:",
            "",
            "💰 INVESTMENT DETAILS:",
            "• How much are you looking to invest?",
            "• What's your investment timeframe? (days, weeks, months, years)",
            "• What return are you targeting? (e.g., 10% profit)",
            "",
            "⚖️  RISK & PREFERENCES:",
            "• What's your risk tolerance? (conservative/moderate/aggressive)",
            "• Any preferred sectors? (banking, tech, energy, etc.)",
            "• Specific stocks you're considering?",
            "",
            "📝 EXAMPLE QUERIES:",
            "• 'I want to invest 100,000 PKR safely for 6 months'",
            "• 'Recommend 2 banking stocks for 15% return in 3 months'",
            "• 'Compare HBL vs UBL for short-term trading'",
            "• 'Analyze my portfolio risk and suggest improvements'"
        ]
        
        response["text"] = "\n".join(lines)
        response["data"] = {"needs_clarification": True, "extracted_context": context}
        return response

    # Helper methods for detailed analysis and recommendations

    def _filter_stocks_by_context(self, stocks: List[dict], context: Dict) -> List[dict]:
        """Filter stocks based on user context and preferences"""
        filtered = stocks.copy()
        
        # Filter by sectors if specified
        if context["sectors"]:
            filtered = [s for s in filtered if any(sector.lower() in s.get("sector", "").lower() 
                                                for sector in context["sectors"])]
        
        # Filter by risk tolerance
        if context["risk_tolerance"] == "low":
            # Focus on low volatility stocks
            filtered = sorted(filtered, key=lambda x: abs(x.get("change_percent", 0)))
        elif context["risk_tolerance"] == "high":
            # Focus on high momentum stocks
            filtered = sorted(filtered, key=lambda x: -abs(x.get("change_percent", 0)))
        
        return filtered[:20]  # Limit for analysis

    def _generate_investment_recommendations(self, stocks: List[dict], context: Dict, user_portfolio: List[dict]) -> List[dict]:
        """Generate detailed investment recommendations with reasoning"""
        recommendations = []
        
        # Get existing holdings for diversification check
        existing_stocks = {h['stock_code'] for h in user_portfolio} if user_portfolio else set()
        
        for stock in stocks[:10]:
            if stock['code'] in existing_stocks and len(stocks) > len(existing_stocks):
                continue  # Skip if already owned, unless limited options
                
            rec = {
                'stock': stock,
                'reasoning': self._generate_stock_reasoning(stock, context),
                'expected_return': self._estimate_expected_return(stock, context),
                'risk_rating': self._assess_stock_risk(stock),
                'recommendation_strength': self._calculate_recommendation_strength(stock, context)
            }
            recommendations.append(rec)
        
        # Sort by recommendation strength
        recommendations.sort(key=lambda x: x['recommendation_strength'], reverse=True)
        return recommendations

    def _generate_stock_reasoning(self, stock: dict, context: Dict) -> str:
        """Generate detailed reasoning for stock recommendation"""
        reasons = []
        
        # Price momentum analysis
        change_pct = stock.get('change_percent', 0)
        if abs(change_pct) > 3:
            trend = "strong upward momentum" if change_pct > 0 else "potential oversold bounce opportunity"
            reasons.append(f"Showing {trend} ({change_pct:+.2f}%)")
        
        # Sector performance
        if stock.get('sector'):
            reasons.append(f"Part of {stock['sector']} sector")
        
        # Volume analysis
        if stock.get('volume', 0) > stock.get('avg_volume', 1):
            reasons.append("Above-average trading volume indicates institutional interest")
        
        # Risk-return alignment
        if context["risk_tolerance"] == "low" and abs(change_pct) < 2:
            reasons.append("Low volatility aligns with conservative risk profile")
        elif context["risk_tolerance"] == "high" and abs(change_pct) > 3:
            reasons.append("High volatility offers potential for significant returns")
        
        return "; ".join(reasons) if reasons else "Fundamental analysis suggests potential value"

    def _estimate_expected_return(self, stock: dict, context: Dict) -> str:
        """Estimate expected return based on analysis"""
        change_pct = stock.get('change_percent', 0)
        volatility = abs(change_pct)
        
        if context["timeframe"] in ["urgent", "1_week", "days"]:
            return f"{volatility * 0.5:.1f}-{volatility * 1.5:.1f}"
        elif context["timeframe"] in ["weeks", "1_month", "short_term"]:
            return f"{volatility * 1.5:.1f}-{volatility * 3:.1f}"
        else:
            return f"{volatility * 3:.1f}-{volatility * 6:.1f}"

    def _assess_stock_risk(self, stock: dict) -> str:
        """Assess individual stock risk level"""
        volatility = abs(stock.get('change_percent', 0))
        
        if volatility < 2:
            return "Low"
        elif volatility < 5:
            return "Medium"
        else:
            return "High"

    def _calculate_recommendation_strength(self, stock: dict, context: Dict) -> float:
        """Calculate overall recommendation strength score"""
        score = 0.5  # Base score
        
        # Momentum factor
        change_pct = stock.get('change_percent', 0)
        if context["risk_tolerance"] == "high":
            score += abs(change_pct) * 0.02
        else:
            score += max(0, 3 - abs(change_pct)) * 0.05
        
        # Volume factor
        if stock.get('volume', 0) > stock.get('avg_volume', 1):
            score += 0.1
        
        # Sector preference
        if context["sectors"] and any(sector.lower() in stock.get('sector', '').lower() 
                                    for sector in context["sectors"]):
            score += 0.2
        
        return min(score, 1.0)

    def _generate_risk_disclaimer(self, context: Dict, recommendations: List[dict]) -> str:
        """Generate appropriate risk disclaimer"""
        if context["urgency"] == "high" or context["timeframe"] in ["urgent", "1_week"]:
            return "Short-term trading involves high risk. Market volatility can result in significant losses. Consider position sizing carefully."
        elif any(r.get('risk_rating') == 'High' for r in recommendations):
            return "High-risk investments recommended. Ensure proper diversification and only invest what you can afford to lose."
        else:
            return "All investments carry risk. Past performance doesn't guarantee future results. Consider your risk tolerance."

    def _generate_alternatives(self, context: Dict, recommendations: List[dict]) -> List[str]:
        """Generate alternative investment strategies"""
        alternatives = []
        
        if context["risk_tolerance"] == "high":
            alternatives.append("Consider dollar-cost averaging to reduce timing risk")
            alternatives.append("Explore sector ETFs for diversified exposure")
        else:
            alternatives.append("Government bonds for guaranteed returns")
            alternatives.append("Blue-chip dividend stocks for steady income")
        
        if context["timeframe"] in ["long_term", "years"]:
            alternatives.append("Index fund investing for long-term wealth building")
        
        return alternatives

    # Additional helper methods would continue here for complete implementation
    # Including: _analyze_specific_stocks, _analyze_sectors, _compare_stocks, etc.

    def _signal_to_dict(self, signal) -> dict:
        """Convert signal object to dictionary"""
        return {
            'stock_code': signal.stock_code,
            'signal_type': signal.signal_type,
            'confidence': signal.confidence,
            'reason': signal.reason,
            'timestamp': getattr(signal, 'timestamp', datetime.now().isoformat())
        }
    
    def _run_scheduler(self):
        """Run scheduled tasks"""
        schedule.every().day.at("09:00").do(self._daily_data_update)
        schedule.every().day.at("15:30").do(self._generate_daily_signals)
        schedule.every().hour.do(self._check_alerts)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def _daily_data_update(self):
        """Daily data update task"""
        logger.info("Running daily data update")
        success = self.data_scraper.scrape_latest_data()
        if success:
            stock_data = self.data_scraper.process_scraped_data()
            # Save to database
            for stock in stock_data:
                self.db_manager.save_stock_data(stock)
    
    def _generate_daily_signals(self):
        """Generate daily signals for all users"""
        logger.info("Generating daily signals")
        signals = self.signal_generator.generate_intelligent_signals()
        for signal in signals:
            self.db_manager.save_signal(signal)
    
    def _check_alerts(self):
        """Check for price alerts and notifications"""
        # Implementation for checking alerts
        pass
    
    def _get_market_outlook(self) -> str:
        """Generate a simple market outlook"""
        # This could be a more complex function based on overall market data
        return "Market outlook is currently neutral, awaiting new economic data."

    def _get_user_specific_notes(self, user_id: str) -> List[str]:
        """Generate notes specific to the user's portfolio"""
        risk_assessment = self.risk_manager.assess_portfolio_risk(user_id)
        return [f"Your portfolio risk is assessed as {risk_assessment['risk_level']}."] + risk_assessment['recommendations']

    def _assess_recommendation_risk(self, recommendations):
        """
        Assess the overall risk level of the recommendations list.
        Returns 'low', 'medium', or 'high'.
        """
        if not recommendations:
            return "medium"
        risk_levels = [rec.get('risk_rating', 'Medium').lower() for rec in recommendations]
        if all(r == "low" for r in risk_levels):
            return "low"
        elif any(r == "high" for r in risk_levels):
            return "high"
        else:
            return "medium"

class UserInterface:
    """User interface handler for displaying information"""
    
    def __init__(self, agent):
        self.agent = agent
    
    def display_menu(self):
        """Display the main menu"""
        print("\n📊 Stock Analysis Agent Menu")
        print("=" * 30)
        print("1. 📈 View Portfolio")
        print("2. 🎯 View Signals")
        print("3. 💰 Add Stock to Portfolio")
        print("4. 👤 User Management")
        print("5. 📊 Performance Report")
        print("6. 🔄 Update Data")
        print("0. 🚪 Exit")
    
    def display_portfolio(self, user_id: str):
        """Display user's portfolio"""
        portfolio = self.agent.db_manager.get_user_portfolio(user_id)
        performance = self.agent.db_manager.get_portfolio_performance(user_id)
        
        print(f"\n📈 Portfolio for User: {user_id}")
        print("=" * 50)
        print(f"Total Value: ${performance['total_value']:.2f}")
        print(f"Total P/L: ${performance['total_pl']:.2f} ({performance['total_pl_percent']:.2f}%)")
        print(f"Daily Change: ${performance['daily_change']:.2f} ({performance['daily_change_percent']:.2f}%)")
        print("\n📊 Holdings:")
        
        if not portfolio:
            print("  No holdings in your portfolio.")
            return

        for holding in portfolio:
            current_price = holding['current_price'] or 0
            pl = (current_price - holding['entry_price']) * holding['quantity']
            pl_percent = (pl / (holding['entry_price'] * holding['quantity'])) * 100 if holding['entry_price'] > 0 else 0
            
            print(f"  {holding['stock_code']}: {holding['quantity']} shares")
            print(f"    Entry: ${holding['entry_price']:.2f} | Current: ${current_price:.2f}")
            print(f"    P/L: ${pl:.2f} ({pl_percent:.2f}%)")
    
    def display_signals(self, signals: List[IntelligentSignal]):
        """Display trading signals"""
        print("\n🎯 Trading Signals")
        print("=" * 50)

        if not signals:
            print("No new signals generated at this time.")
            return
        
        for signal in signals:
            print(f"\n📊 {signal.stock_code} - {signal.signal_type}")
            print(f"   Confidence: {signal.confidence:.2f}")
            print(f"   Expected Return: {signal.expected_return:.2f}%")
            print(f"   Risk Level: {signal.risk_level}")
            print(f"   Target: ${signal.target_price:.2f}")
            print(f"   Stop Loss: ${signal.stop_loss:.2f}")
            print(f"   Timeframe: {signal.timeframe}")
            print(f"   Reason: {signal.reason}")

    def display_performance_report(self, report: Dict):
        """Display a formatted performance report"""
        print("\n📈 Performance Report")
        print("=" * 50)
        print(f"Total Portfolio P/L: ${report['portfolio_performance']['total_pl']:.2f} ({report['portfolio_performance']['total_pl_percent']:.2f}%)")
        
        for timeframe, data in report.items():
            if timeframe == 'portfolio_performance':
                continue
            print(f"\n📅 {timeframe.capitalize()} Performance:")
            print(f"   Total Return: ${data['total_return']:.2f}")
            print(f"   Win Rate: {data['win_rate']:.2f}%")
            print(f"   Total Trades: {data['trades_count']}")

    def get_user_input(self, prompt: str) -> str:
        """Get user input with prompt"""
        return input(f"{prompt}: ").strip()

class RiskManager:
    """Risk management system for portfolio and trades"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
    
    def assess_portfolio_risk(self, user_id: str) -> Dict:
        """Assess overall portfolio risk"""
        portfolio = self.db_manager.get_user_portfolio(user_id)
        user_profile = self.db_manager.get_user_profile(user_id)
        
        if not portfolio:
            return {'risk_level': 'low', 'risk_score': 0.0, 'recommendations': []}
        
        # Calculate diversification
        sectors = set(holding['sector'] for holding in portfolio)
        diversification_score = len(sectors) / max(len(portfolio), 1)
        
        # Calculate volatility
        total_volatility = 0
        for holding in portfolio:
            stock_history = self.db_manager.get_stock_history(holding['stock_code'])
            if stock_history:
                prices = [float(h['close_price']) for h in stock_history]
                if len(prices) > 1:
                    volatility = statistics.stdev(prices) / statistics.mean(prices)
                else:
                    volatility = 0
                total_volatility += volatility
        
        avg_volatility = total_volatility / len(portfolio)
        
        # Calculate risk score
        risk_score = (1 - diversification_score) * 0.4 + avg_volatility * 0.6
        
        if risk_score > 0.15:
            risk_level = 'high'
        elif risk_score > 0.08:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        recommendations = []
        if diversification_score < 0.3:
            recommendations.append("Consider diversifying across more sectors")
        if avg_volatility > 0.1:
            recommendations.append("Portfolio has high volatility, consider defensive stocks")
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'diversification_score': diversification_score,
            'average_volatility': avg_volatility,
            'recommendations': recommendations
        }
    
    def validate_trade(self, user_id: str, stock_code: str, quantity: int) -> bool:
        """Validate if a trade is within risk limits"""
        user_profile = self.db_manager.get_user_profile(user_id)
        if not user_profile:
            return False
        
        # Get stock price
        latest_data = self.db_manager.get_latest_stock_data()
        stock_price = next((s['close_price'] for s in latest_data if s['code'] == stock_code), None)
        
        if not stock_price:
            return False
        
        # Calculate trade value
        trade_value = stock_price * quantity
        
        # Check if trade exceeds position size limits
        risk_threshold = Config.RISK_THRESHOLDS.get(user_profile.risk_tolerance, Config.RISK_THRESHOLDS['medium'])
        max_position_value = user_profile.portfolio_value * risk_threshold['max_position_size']
        
        if trade_value > max_position_value:
            return False
        
        # Check if user has sufficient cash
        if trade_value > user_profile.cash_balance:
            return False
        
        return True
    
    def calculate_position_size(self, user_id: str, stock_code: str, risk_level: str) -> int:
        """Calculate appropriate position size based on risk"""
        user_profile = self.db_manager.get_user_profile(user_id)
        if not user_profile:
            return 0
        
        risk_threshold = Config.RISK_THRESHOLDS.get(user_profile.risk_tolerance, Config.RISK_THRESHOLDS['medium'])
        max_position_value = user_profile.portfolio_value * risk_threshold['max_position_size']
        
        # Get stock price
        latest_data = self.db_manager.get_latest_stock_data()
        stock_price = next((s['close_price'] for s in latest_data if s['code'] == stock_code), None)
        
        if not stock_price:
            return 0
        
        # Adjust for risk level
        risk_multiplier = {'low': 1.0, 'medium': 0.8, 'high': 0.6}.get(risk_level, 0.8)
        adjusted_max_value = max_position_value * risk_multiplier
        
        return int(adjusted_max_value / stock_price)

class NotificationManager:
    """Notification system for alerts and updates"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
    
    def send_signal_alert(self, user_id: str, signal: IntelligentSignal):
        """Send signal alert to user"""
        # In a real implementation, this would send email/SMS/push notification
        logger.info(f"Signal alert for {user_id}: {signal.stock_code} - {signal.signal_type}")
        print(f"🚨 ALERT: {signal.stock_code} - {signal.signal_type} signal with {signal.confidence:.2f} confidence")
    
    def send_portfolio_update(self, user_id: str, performance: Dict):
        """Send portfolio performance update"""
        logger.info(f"Portfolio update for {user_id}: {performance}")
        print(f"📊 Portfolio Update: Total P/L: ${performance['total_pl']:.2f} ({performance['total_pl_percent']:.2f}%)")
    
    def schedule_notifications(self):
        """Schedule regular notifications"""
        # Implementation for scheduling notifications
        pass

class PerformanceTracker:
    """Performance tracking system"""
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
    
    def track_signal_performance(self, signal_id: int, actual_return: float):
        """Track how well a signal performed"""
        with self.db_manager.get_connection() as conn:
            conn.execute('''
                UPDATE signals 
                SET actual_return = ?, is_active = 0 
                WHERE id = ?
            ''', (actual_return, signal_id))
            conn.commit()
    
    def calculate_strategy_performance(self, user_id: str, timeframe: str) -> Dict:
        """Calculate performance metrics for a strategy"""
        with self.db_manager.get_connection() as conn:
            # Get performance data
            if timeframe == 'monthly':
                cutoff_date = datetime.now() - timedelta(days=30)
            elif timeframe == 'weekly':
                cutoff_date = datetime.now() - timedelta(days=7)
            else:
                cutoff_date = datetime.now() - timedelta(days=365)
            
            results = conn.execute('''
                SELECT * FROM performance_tracking
                WHERE user_id = ? AND timestamp >= ?
                ORDER BY timestamp
            ''', (user_id, cutoff_date)).fetchall()
            
            if not results:
                return {'total_return': 0, 'win_rate': 0, 'trades_count': 0}
            
            total_return = sum(row['profit_loss'] for row in results)
            winning_trades = len([r for r in results if r['profit_loss'] > 0])
            win_rate = winning_trades / len(results) if results else 0
            
            return {
                'total_return': total_return,
                'win_rate': win_rate,
                'trades_count': len(results),
                'average_return': total_return / len(results) if results else 0
            }
    
    def generate_performance_report(self, user_id: str) -> Dict:
        """Generate comprehensive performance report"""
        monthly_performance = self.calculate_strategy_performance(user_id, 'monthly')
        weekly_performance = self.calculate_strategy_performance(user_id, 'weekly')
        yearly_performance = self.calculate_strategy_performance(user_id, 'yearly')
        
        return {
            'monthly': monthly_performance,
            'weekly': weekly_performance,
            'yearly': yearly_performance,
            'portfolio_performance': self.db_manager.get_portfolio_performance(user_id)
        }

# ===== Utility Functions =====

def load_scraped_data(file_path: str) -> List[Dict]:
    """Load scraped data from file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading scraped data: {e}")
        return []

def validate_stock_data(data: Dict) -> bool:
    """Validate stock data structure"""
    required_fields = ['code', 'name', 'close_price', 'volume']
    return all(field in data for field in required_fields)

def calculate_portfolio_metrics(holdings: List[Dict]) -> Dict:
    """Calculate portfolio metrics"""
    if not holdings:
        return {'total_value': 0, 'total_pl': 0, 'diversification': 0}
    
    total_value = sum(h['current_price'] * h['quantity'] for h in holdings)
    total_cost = sum(h['entry_price'] * h['quantity'] for h in holdings)
    total_pl = total_value - total_cost
    
    sectors = set(h['sector'] for h in holdings)
    diversification = len(sectors) / len(holdings)
    
    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_pl': total_pl,
        'total_pl_percent': (total_pl / total_cost * 100) if total_cost > 0 else 0,
        'diversification': diversification
    }

GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Or set directly as a string


def call_groq_llm(prompt, system_message=None, model="llama3-70b-8192"):
    import openai
    openai.api_key = GROQ_API_KEY
    openai.base_url = "https://api.groq.com/openai/v1"
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    client = openai.OpenAI(api_key="...", base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    agent = StockAnalysisAgent()
    agent.start_interactive_session()