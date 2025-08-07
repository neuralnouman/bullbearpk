-- Migration: Add portfolio tracking columns to users table
-- Run this script to add missing columns to existing databases

USE bullbearpk;

-- Add total_invested column if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS total_invested DECIMAL(15,2) DEFAULT 0.00 AFTER cash_balance;

-- Add total_returns column if it doesn't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS total_returns DECIMAL(15,2) DEFAULT 0.00 AFTER total_invested;

-- Update existing users with calculated values
UPDATE users u 
SET 
    total_invested = (
        SELECT COALESCE(SUM(total_invested), 0) 
        FROM investments i 
        WHERE i.user_id = u.user_id AND i.status = 'active'
    ),
    total_returns = (
        SELECT COALESCE(SUM(realized_pnl), 0) + COALESCE(SUM(current_value - total_invested), 0)
        FROM investments i 
        WHERE i.user_id = u.user_id AND i.status = 'active'
    )
WHERE user_id IN (SELECT DISTINCT user_id FROM investments);

-- Update portfolio_value to include cash_balance
UPDATE users 
SET portfolio_value = COALESCE(total_invested, 0) + COALESCE(total_returns, 0) + COALESCE(cash_balance, 0)
WHERE portfolio_value = 0 OR portfolio_value IS NULL;

-- Show the updated structure
DESCRIBE users; 