-- Enhanced tables for agentic workflow tracking

CREATE TABLE IF NOT EXISTS user_form_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    budget DECIMAL(15,2),
    sector_preference VARCHAR(50),
    risk_tolerance VARCHAR(20),
    time_horizon VARCHAR(20),
    target_profit DECIMAL(5,2),
    investment_goal VARCHAR(100),
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommendations_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS user_recommendations_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    form_submission_id INT,
    stock_code VARCHAR(20),
    stock_name VARCHAR(100),
    recommendation_type VARCHAR(20),
    confidence_score DECIMAL(5,2),
    expected_return DECIMAL(5,2),
    reasoning TEXT,
    technical_analysis JSON,
    news_sentiment JSON,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (form_submission_id) REFERENCES user_form_submissions(id)
);