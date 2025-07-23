#!/usr/bin/env python3
"""
Restructured AI Stock Analysis Agent for Multi-Agent Pipeline
Author: AI Assistant
Date: 2025-07-19
Version: 2.1
"""

import sqlite3
import json
import logging
import os
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import statistics
import uuid

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

# Function to get latest stock data for the API
def get_latest_stock_data() -> Dict[str, Any]:
    """
    Retrieves the latest stock data from the scraped JSON file
    Returns a dictionary containing scrape_info, market_summary, and stocks data
    """
    try:
        # Find the most recent scraped data file
        scraper_dir = Config.SCRAPER_DIR if 'Config' in globals() else Path(__file__).parent.parent / "scraped"
        
        # Ensure the directory exists
        if not os.path.exists(scraper_dir):
            logger.error(f"Scraper directory not found: {scraper_dir}")
            return {}
            
        # List all JSON files in the directory
        json_files = [f for f in os.listdir(scraper_dir) if f.endswith('.json')]
        
        if not json_files:
            logger.warning("No stock data files found")
            return {}
            
        # Sort by modification time (most recent first)
        latest_file = sorted(
            json_files,
            key=lambda x: os.path.getmtime(os.path.join(scraper_dir, x)),
            reverse=True
        )[0]
        
        # Load the data from the file
        with open(os.path.join(scraper_dir, latest_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Return the complete data object
        return data
        
    except Exception as e:
        logger.error(f"Error retrieving latest stock data: {str(e)}")
        return {}

# ===== Configuration =====
class Config:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "agents" / "data"
    SCRAPER_DIR = BASE_DIR / "agents" / "scraped"
    DB_PATH = DATA_DIR / "stocks.db"
    SCRAPER_SCRIPT = BASE_DIR / "fin_scraper.py"
    # Analysis parameters
    RSI_PERIOD = 14
    MA_SHORT = 5
    MA_LONG = 20
    # Risk thresholds
    RISK_THRESHOLDS = {
        'low': {'min_confidence': 0.8, 'max_volatility': 0.03, 'max_position_size': 0.05},
        'medium': {'min_confidence': 0.6, 'max_volatility': 0.06, 'max_position_size': 0.10},
        'high': {'min_confidence': 0.4, 'max_volatility': 0.15, 'max_position_size': 0.20}
    }
    DATA_DIR.mkdir(exist_ok=True)
    SCRAPER_DIR.mkdir(exist_ok=True)

# ===== Data Models =====
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

# ===== Database Manager =====
class EnhancedDatabaseManager:
    def __init__(self, db_path: str = Config.DB_PATH):
        self.db_path = db_path
        logger.info(f"DB path: {self.db_path}")
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        with self.get_connection() as conn:
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
            conn.execute('''
                CREATE TABLE IF NOT EXISTS investments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    stock_symbol TEXT NOT NULL,
                    company_name TEXT,
                    quantity INTEGER NOT NULL,
                    purchase_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    purchase_date TEXT,
                    sector TEXT,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    stock_symbol TEXT NOT NULL,
                    company_name TEXT,
                    recommendation_type TEXT,
                    reason TEXT,
                    risk_level TEXT,
                    expected_return TEXT,
                    allocation_amount REAL,
                    timestamp TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    budget REAL DEFAULT 10000.0,
                    sector TEXT,
                    risk_appetite TEXT DEFAULT 'medium',
                    time_horizon TEXT DEFAULT 'medium',
                    target_profit REAL DEFAULT 15.0,
                    last_updated TEXT
                )
            ''')
            conn.commit()
        logger.info("Database initialized successfully")
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        with self.get_connection() as conn:
            result = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
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
    
    def get_latest_stock_data(self) -> List[Dict]:
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
    
    def get_stock_history(self, stock_code: str, days: int = 30) -> List[Dict]:
        with self.get_connection() as conn:
            cutoff_date = datetime.now() - timedelta(days=days)
            results = conn.execute('''
                SELECT * FROM stock_data 
                WHERE code = ? AND timestamp >= ? 
                ORDER BY timestamp ASC
            ''', (stock_code, cutoff_date)).fetchall()
            return [dict(row) for row in results]
    
    def save_stock_data(self, stock_data: StockData):
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
    
# ===== Technical Analysis =====
class AdvancedTechnicalAnalyzer:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
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
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26
        if len(prices) >= 35:
            macd_values = [self._calculate_ema(prices[:i+1], 12) - self._calculate_ema(prices[:i+1], 26) 
                          for i in range(25, len(prices))]
            signal_line = self._calculate_ema(macd_values, 9)
        else:
            signal_line = 0
        histogram = macd_line - signal_line
        return {'macd': macd_line, 'signal': signal_line, 'histogram': histogram}
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Dict:
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0}
        recent_prices = prices[-period:]
        middle = sum(recent_prices) / len(recent_prices)
        std = statistics.stdev(recent_prices)
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return {'upper': upper, 'middle': middle, 'lower': lower}
    
    def calculate_support_resistance(self, prices: List[float], highs: List[float], lows: List[float]) -> Dict:
        if len(prices) < 10:
            return {'support': min(prices), 'resistance': max(prices)}
        resistance_levels = []
        support_levels = []
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1] and highs[i] > highs[i-2] and highs[i] > highs[i+2]:
                resistance_levels.append(highs[i])
            if lows[i] < lows[i-1] and lows[i] < lows[i+1] and lows[i] < lows[i-2] and lows[i] < lows[i+2]:
                support_levels.append(lows[i])
        current_price = prices[-1]
        resistance = min([r for r in resistance_levels if r > current_price], default=max(highs))
        support = max([s for s in support_levels if s < current_price], default=min(lows))
        return {'support': support, 'resistance': resistance}
    
    def comprehensive_analysis(self, stock_code: str) -> Dict:
        history = self.db.get_stock_history(stock_code, days=60)
        if not history:
            return {}
        history.sort(key=lambda x: x['timestamp'])
        prices = [float(row['close_price']) for row in history]
        highs = [float(row['high_price']) for row in history]
        lows = [float(row['low_price']) for row in history]
        volumes = [int(row['volume']) for row in history]
        if len(prices) < 2:
            return {}
        current_price = prices[-1]
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        bollinger = self.calculate_bollinger_bands(prices)
        support_resistance = self.calculate_support_resistance(prices, highs, lows)
        ma_5 = sum(prices[-5:]) / min(5, len(prices))
        ma_20 = sum(prices[-20:]) / min(20, len(prices))
        ma_50 = sum(prices[-50:]) / min(50, len(prices))
        avg_volume = sum(volumes[-20:]) / min(20, len(volumes))
        volume_trend = 'increasing' if volumes[-1] > avg_volume * 1.2 else 'decreasing' if volumes[-1] < avg_volume * 0.8 else 'normal'
        price_trend = self._determine_trend(prices)
        momentum = self._calculate_momentum(prices)
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
        if len(prices) < 10:
            return 0.0
        return (prices[-1] - prices[-10]) / prices[-10] * 100
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        if len(prices) < 20:
            return 0.0
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, min(len(prices), 21))]
        return statistics.stdev(returns) if len(returns) > 1 else 0.0

# ===== Signal Generator =====
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
    
    def generate_intelligent_signals(self, user_id: str = None) -> List[Dict]:
        user_profile = self.db.get_user_profile(user_id) if user_id else None
        latest_data = self.db.get_latest_stock_data()
        stock_codes = [row['code'] for row in latest_data]
        if user_profile and user_profile.blacklisted_stocks:
            stock_codes = [code for code in stock_codes if code not in user_profile.blacklisted_stocks]
        signals = []
        for stock_code in stock_codes:
            signal = self._generate_stock_signal(stock_code, user_profile)
            if signal and signal['confidence'] > 0.3:
                signals.append(signal)
        signals.sort(key=lambda x: (x['confidence'] * x['expected_return']), reverse=True)
        return signals[:20]

    def _generate_stock_signal(self, stock_code: str, user_profile: Optional[UserProfile] = None) -> Optional[Dict]:
        analysis = self.analyzer.comprehensive_analysis(stock_code)
        if not analysis:
            return None
        rsi = analysis.get('rsi', 50)
        macd = analysis.get('macd', {})
        bollinger = analysis.get('bollinger_bands', {})
        support_resistance = analysis.get('support_resistance', {})
        volume_analysis = analysis.get('volume_analysis', {})
        price_trend = analysis.get('price_trend', 'sideways')
        current_price = analysis.get('current_price', 0)
        signals = []
        reasons = []
        if rsi < 30:
            signals.append('BUY')
            reasons.append(f"RSI {rsi:.1f} (oversold)")
        elif rsi > 70:
            signals.append('SELL')
            reasons.append(f"RSI {rsi:.1f} (overbought)")
        if macd and macd.get('histogram', 0) > 0 and macd.get('macd', 0) > macd.get('signal', 0):
            signals.append('BUY')
            reasons.append("MACD bullish crossover")
        elif macd and macd.get('histogram', 0) < 0 and macd.get('macd', 0) < macd.get('signal', 0):
            signals.append('SELL')
            reasons.append("MACD bearish crossover")
        if bollinger and current_price < bollinger.get('lower', 0):
            signals.append('BUY')
            reasons.append("Price below lower Bollinger Band (potential rebound)")
        elif bollinger and current_price > bollinger.get('upper', 0):
            signals.append('SELL')
            reasons.append("Price above upper Bollinger Band (potential pullback)")
        if support_resistance:
            support = support_resistance.get('support', 0)
            resistance = support_resistance.get('resistance', 0)
            if abs(current_price - support) / current_price < 0.02:
                signals.append('BUY')
                reasons.append("Price near strong support")
            if abs(current_price - resistance) / current_price < 0.02:
                signals.append('SELL')
                reasons.append("Price near strong resistance")
        volume_ratio = volume_analysis.get('current_volume', 1) / max(volume_analysis.get('avg_volume', 1), 1)
        if volume_ratio > 1.5:
            reasons.append("High volume confirms move")
        elif volume_ratio < 0.5:
            reasons.append("Low volume, weak conviction")
        if price_trend in ['strong_uptrend', 'uptrend']:
            signals.append('BUY')
            reasons.append("Uptrend detected")
        elif price_trend in ['strong_downtrend', 'downtrend']:
            signals.append('SELL')
            reasons.append("Downtrend detected")
        buy_votes = signals.count('BUY')
        sell_votes = signals.count('SELL')
        total_votes = buy_votes + sell_votes
        if total_votes == 0:
            signal_type = 'HOLD'
            confidence = 0.5
            main_reason = "No strong consensus among indicators."
        elif buy_votes > sell_votes:
            signal_type = 'BUY'
            confidence = 0.6 + 0.1 * (buy_votes - sell_votes)
            main_reason = "; ".join([r for r in reasons if 'BUY' in signals or 'Uptrend' in r or 'support' in r])
        elif sell_votes > buy_votes:
            signal_type = 'SELL'
            confidence = 0.6 + 0.1 * (sell_votes - buy_votes)
            main_reason = "; ".join([r for r in reasons if 'SELL' in signals or 'Downtrend' in r or 'resistance' in r])
        else:
            signal_type = 'HOLD'
            confidence = 0.5
            main_reason = "Mixed signals from technical indicators."
        confidence = min(confidence, 0.95)
        expected_return = abs(analysis.get('momentum', 0))
        risk_level = 'Medium'
        return {
            'stock_code': stock_code,
            'signal_type': signal_type,
            'confidence': confidence,
            'reason': main_reason,
            'expected_return': expected_return,
            'risk_level': risk_level,
            'supporting_indicators': reasons,
            'timestamp': datetime.now().isoformat()
        }

# ===== Risk Manager =====
class RiskManager:
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db_manager = db_manager
    def assess_portfolio_risk(self, user_id: str) -> Dict:
        portfolio = self.db_manager.get_user_portfolio(user_id)
        user_profile = self.db_manager.get_user_profile(user_id)
        if not portfolio:
            return {'risk_level': 'low', 'risk_score': 0.0, 'recommendations': []}
        sectors = set(holding['sector'] for holding in portfolio)
        diversification_score = len(sectors) / max(len(portfolio), 1)
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
    
# ===== Main Agent Wrapper =====
class StockAnalysisAgent:
    def __init__(self):
        self.db_manager = EnhancedDatabaseManager()
        self.analyzer = AdvancedTechnicalAnalyzer(self.db_manager)
        self.signal_generator = IntelligentSignalGenerator(self.db_manager, self.analyzer)
        self.risk_manager = RiskManager(self.db_manager)