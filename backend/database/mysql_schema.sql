-- BullBearPK MySQL Database Schema
-- Database: bullbearpk
-- Username: root
-- Password: 123456


show databases;
-- Create database if not exists
CREATE DATABASE IF NOT EXISTS bullbearpk;
USE bullbearpk;

-- Users table
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
);

-- Stock data table
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
);

-- Stock historical data
CREATE TABLE stock_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stock_date (stock_code, date),
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE
);

-- User portfolios - Complete portfolio tracking
CREATE TABLE portfolios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    
    -- Portfolio Summary
    total_value DECIMAL(15,2) DEFAULT 0.00,
    total_invested DECIMAL(15,2) DEFAULT 0.00,
    total_profit_loss DECIMAL(15,2) DEFAULT 0.00,
    profit_loss_percent DECIMAL(5,2) DEFAULT 0.00,
    
    -- Cash Management
    cash_balance DECIMAL(15,2) DEFAULT 0.00,
    available_cash DECIMAL(15,2) DEFAULT 0.00,
    reserved_cash DECIMAL(15,2) DEFAULT 0.00,  -- For pending orders
    
    -- Performance Metrics
    total_realized_pnl DECIMAL(15,2) DEFAULT 0.00,
    total_unrealized_pnl DECIMAL(15,2) DEFAULT 0.00,
    total_dividends_received DECIMAL(15,2) DEFAULT 0.00,
    
    -- Portfolio Statistics
    total_stocks_held INT DEFAULT 0,
    active_investments INT DEFAULT 0,
    sold_investments INT DEFAULT 0,
    average_investment_duration_days DECIMAL(5,2) DEFAULT 0.00,
    
    -- Risk Metrics
    portfolio_volatility DECIMAL(5,2) DEFAULT 0.00,
    portfolio_beta DECIMAL(5,2) DEFAULT 0.00,
    portfolio_sharpe_ratio DECIMAL(5,2) DEFAULT 0.00,
    max_drawdown DECIMAL(5,2) DEFAULT 0.00,
    
    -- Sector Allocation
    sector_allocation JSON NULL,  -- {'Banking': 30.5, 'Technology': 25.2, ...}
    top_holdings JSON NULL,  -- Top 5 holdings with percentages
    
    -- Performance History
    best_performing_stock VARCHAR(20) NULL,
    worst_performing_stock VARCHAR(20) NULL,
    best_trade_pnl DECIMAL(15,2) DEFAULT 0.00,
    worst_trade_pnl DECIMAL(15,2) DEFAULT 0.00,
    
    -- Investment Goals Tracking
    target_portfolio_value DECIMAL(15,2) DEFAULT 0.00,
    progress_towards_goal DECIMAL(5,2) DEFAULT 0.00,  -- Percentage
    goal_deadline DATE NULL,
    
    -- Portfolio Health
    diversification_score DECIMAL(3,2) DEFAULT 0.00,  -- 0-1 score
    risk_score DECIMAL(3,2) DEFAULT 0.00,  -- 0-1 score
    rebalancing_needed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    portfolio_date DATE NOT NULL,  -- Date of this portfolio snapshot
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- User Preferences (snapshot)
    risk_tolerance_snapshot ENUM('low', 'moderate', 'high') DEFAULT 'moderate',
    investment_goal_snapshot VARCHAR(100) NULL,
    preferred_sectors_snapshot JSON NULL,
    
    -- Metadata
    snapshot_type ENUM('daily', 'weekly', 'monthly', 'manual', 'transaction') DEFAULT 'daily',
    notes TEXT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, portfolio_date),
    INDEX idx_user_date (user_id, portfolio_date),
    INDEX idx_portfolio_date (portfolio_date)
);

-- User investments - Comprehensive tracking
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
    current_quantity INT DEFAULT 0,  -- Remaining shares after partial sells
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
    sell_reason VARCHAR(100) NULL,  -- 'profit_taking', 'stop_loss', 'rebalancing', 'manual'
    
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
    recommendation_when_bought VARCHAR(20) NULL,  -- 'buy', 'hold', 'sell'
    confidence_score_when_bought DECIMAL(3,2) NULL,
    technical_analysis_when_bought JSON NULL,
    news_sentiment_when_bought JSON NULL,
    
    -- User Notes
    user_notes TEXT NULL,
    tags JSON NULL,  -- ['long_term', 'dividend_stock', 'growth_stock', etc.]
    
    -- Metadata
    created_by VARCHAR(50) DEFAULT 'system',  -- 'user', 'system', 'recommendation'
    source VARCHAR(50) DEFAULT 'manual',  -- 'manual', 'recommendation', 'auto_invest'
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE,
    INDEX idx_user_stock (user_id, stock_code),
    INDEX idx_status (status),
    INDEX idx_buy_date (buy_date),
    INDEX idx_sell_date (sell_date),
    INDEX idx_transaction_type (transaction_type)
);

-- Enhanced stock analysis with advanced technical indicators
CREATE TABLE stock_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Basic Price Data
    current_price DECIMAL(10,2),
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    volume BIGINT,
    change_amount DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    
    -- Performance Metrics
    performance_score DECIMAL(5,2),
    rank_position INT,
    sector_performance_rank INT,
    
    -- Advanced Technical Indicators
    rsi DECIMAL(5,2),
    stochastic_k DECIMAL(5,2),
    stochastic_d DECIMAL(5,2),
    williams_r DECIMAL(5,2),
    cci DECIMAL(5,2),
    roc DECIMAL(5,2),
    atr DECIMAL(10,2),
    
    -- Moving Averages
    ma_5 DECIMAL(10,2),
    ma_10 DECIMAL(10,2),
    ma_20 DECIMAL(10,2),
    ma_50 DECIMAL(10,2),
    ma_200 DECIMAL(10,2),
    
    -- MACD Analysis
    macd DECIMAL(10,2),
    macd_signal DECIMAL(10,2),
    macd_histogram DECIMAL(10,2),
    
    -- Bollinger Bands
    bollinger_upper DECIMAL(10,2),
    bollinger_lower DECIMAL(10,2),
    bollinger_middle DECIMAL(10,2),
    bb_position DECIMAL(5,2), -- Position within Bollinger Bands (0-100)
    
    -- Support and Resistance
    support_level DECIMAL(10,2),
    resistance_level DECIMAL(10,2),
    support_distance DECIMAL(5,2), -- Distance from support (%)
    resistance_distance DECIMAL(5,2), -- Distance from resistance (%)
    
    -- Trend Analysis
    trend VARCHAR(20),
    trend_strength DECIMAL(3,2),
    trend_duration INT, -- Days in current trend
    momentum DECIMAL(5,2),
    volatility DECIMAL(5,2),
    
    -- Volume Analysis
    volume_sma DECIMAL(10,2), -- Volume Simple Moving Average
    volume_ratio DECIMAL(5,2), -- Current volume / Average volume
    volume_trend VARCHAR(20),
    price_volume_trend VARCHAR(20),
    
    -- Advanced Analytics
    beta_coefficient DECIMAL(5,2), -- Market correlation
    sharpe_ratio DECIMAL(5,2), -- Risk-adjusted return
    alpha_coefficient DECIMAL(5,2), -- Excess return
    information_ratio DECIMAL(5,2),
    
    -- Market Position
    relative_strength_index DECIMAL(5,2), -- vs market
    sector_rank INT,
    market_cap_rank INT,
    
    -- Risk Metrics
    value_at_risk DECIMAL(5,2),
    maximum_drawdown DECIMAL(5,2),
    downside_deviation DECIMAL(5,2),
    
    -- Confidence and Recommendations
    confidence_score DECIMAL(3,2),
    recommendation ENUM('strong_buy', 'buy', 'hold', 'sell', 'strong_sell'),
    risk_level ENUM('low', 'moderate', 'high'),
    expected_return DECIMAL(5,2),
    target_price DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    
    -- Analysis Summary
    analysis_summary TEXT,
    key_insights JSON NULL,
    risk_factors JSON NULL,
    opportunities JSON NULL,
    
    -- Metadata
    analysis_version VARCHAR(10),
    data_quality_score DECIMAL(3,2),
    
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE,
    INDEX idx_stock_date (stock_code, analysis_date),
    INDEX idx_performance (performance_score DESC),
    INDEX idx_recommendation (recommendation),
    INDEX idx_sector_rank (sector_rank),
    INDEX idx_rank_position (rank_position)
);

-- Raw news records (scraped news data)
CREATE TABLE news_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    link TEXT NOT NULL,
    published_date TIMESTAMP NULL,
    source VARCHAR(100),
    content_hash VARCHAR(64) UNIQUE,  -- To prevent duplicates
    sentiment VARCHAR(20) DEFAULT 'neutral',
    sentiment_score DECIMAL(3,2) DEFAULT 0.0,
    keywords JSON NULL,
    company_mentions JSON NULL,
    financial_impact VARCHAR(50) DEFAULT 'neutral',
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE,
    INDEX idx_stock_date (stock_code, published_date),
    INDEX idx_content_hash (content_hash),
    INDEX idx_is_processed (is_processed),
    INDEX idx_sentiment (sentiment)
);

-- News analysis results
CREATE TABLE news_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_sentiment ENUM('bullish', 'bearish', 'neutral'),
    sentiment_score DECIMAL(3,2),
    news_count INT DEFAULT 0,
    positive_news INT DEFAULT 0,
    negative_news INT DEFAULT 0,
    neutral_news INT DEFAULT 0,
    key_events JSON NULL,
    risk_factors JSON NULL,
    opportunities JSON NULL,
    recommendation TEXT,
    confidence DECIMAL(3,2),
    analysis_summary TEXT,
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE,
    INDEX idx_stock_date (stock_code, analysis_date)
);



-- User feedback
CREATE TABLE user_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    feedback_type ENUM('recommendation', 'analysis', 'system'),
    feedback_text TEXT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    recommendations_data JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- System logs
CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_level ENUM('INFO', 'WARNING', 'ERROR', 'DEBUG'),
    component VARCHAR(50),
    message TEXT,
    user_id VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level_component (log_level, component),
    INDEX idx_created_at (created_at)
);

-- Market summary
CREATE TABLE market_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL,
    total_volume BIGINT,
    total_trades INT,
    market_cap DECIMAL(20,2),
    kse_100_index DECIMAL(10,2),
    kse_100_change DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (summary_date)
);

-- Recommendations table for storing all generated recommendations
CREATE TABLE recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    sector VARCHAR(50),
    
    -- Recommendation details
    recommendation_type ENUM('buy', 'sell', 'hold', 'strong_buy', 'strong_sell') NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL,
    expected_return DECIMAL(5,2),
    risk_level ENUM('low', 'medium', 'high') DEFAULT 'medium',
    
    -- Analysis data
    technical_analysis JSON,
    news_sentiment JSON,
    fundamental_analysis JSON,
    
    -- User preferences when recommendation was made
    user_budget DECIMAL(15,2),
    user_risk_tolerance VARCHAR(20),
    user_time_horizon VARCHAR(20),
    user_sector_preference VARCHAR(50),
    
    -- Recommendation reasoning
    reasoning_summary TEXT,
    key_factors JSON,
    risk_factors JSON,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    source_agent VARCHAR(50) DEFAULT 'agentic_framework',
    model_version VARCHAR(20),
    analysis_timestamp TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_code) REFERENCES stocks(code) ON DELETE CASCADE,
    INDEX idx_user_recommendations (user_id, created_at),
    INDEX idx_stock_recommendations (stock_code, created_at),
    INDEX idx_active_recommendations (is_active, created_at),
    INDEX idx_recommendation_type (recommendation_type, confidence_score)
);

show tables;

select * from stocks;

-- Insert sample data for testing
INSERT INTO users (user_id, name, email, password, risk_tolerance, investment_goal, portfolio_value, cash_balance) VALUES
('user001', 'Test User', 'test@example.com', 'password123', 'moderate', 'Growth', 100000.00, 25000.00),
('user002', 'Demo User', 'demo@example.com', 'password123', 'high', 'Aggressive Growth', 150000.00, 50000.00);

-- Insert sample stocks
INSERT INTO stocks (code, name, sector, open_price, high_price, low_price, close_price, volume, change_amount, change_percent) VALUES
('HBL', 'Habib Bank Limited', 'Banking', 100.50, 102.30, 99.80, 101.20, 1500000, 0.70, 0.70),
('UBL', 'United Bank Limited', 'Banking', 95.20, 97.10, 94.50, 96.80, 1200000, 1.60, 1.68),
('OGDC', 'Oil & Gas Development Company', 'Energy', 85.40, 87.20, 84.90, 86.50, 2000000, 1.10, 1.29),
('PPL', 'Pakistan Petroleum Limited', 'Energy', 78.30, 80.10, 77.80, 79.60, 1800000, 1.30, 1.66),
('LUCK', 'Lucky Cement Limited', 'Cement', 450.00, 455.50, 448.20, 453.80, 500000, 3.80, 0.84);

-- Insert sample portfolio
INSERT INTO portfolios (user_id, total_value, total_invested, total_profit_loss, profit_loss_percent) VALUES
('user001', 100000.00, 95000.00, 5000.00, 5.26);

-- Insert sample investments
INSERT INTO investments (user_id, stock_code, quantity, buy_price, total_invested, current_value, profit_loss, profit_loss_percent) VALUES
('user001', 'HBL', 500, 100.00, 50000.00, 50600.00, 600.00, 1.20),
('user001', 'UBL', 300, 95.00, 28500.00, 29040.00, 540.00, 1.89);

-- Insert sample market summary
INSERT INTO market_summary (summary_date, total_volume, total_trades, market_cap, kse_100_index, kse_100_change) VALUES
(CURDATE(), 150000000, 45000, 8500000000000.00, 45000.50, 1.25); 


show tables;


select * from stocks;
select * from investments;
select * from recommendations;
select * from portfolios;
