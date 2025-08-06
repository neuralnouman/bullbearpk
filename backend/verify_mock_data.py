#!/usr/bin/env python3
"""
Mock Data Verification Script for BullBearPK
===========================================

This script verifies that the mock data was populated correctly and displays
sample data for validation purposes.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_config import DatabaseConfig

class MockDataVerifier:
    """Verifies mock data population and displays sample data"""
    
    def __init__(self):
        self.db = DatabaseConfig()
    
    def verify_users(self):
        """Verify user data"""
        print("\n" + "="*50)
        print("USER PROFILES")
        print("="*50)
        
        users = self.db.execute_query("SELECT user_id, name, email, risk_tolerance, investment_goal, portfolio_value, cash_balance FROM users LIMIT 5")
        
        if users:
            for user in users:
                print(f"User ID: {user['user_id']}")
                print(f"Name: {user['name']}")
                print(f"Email: {user['email']}")
                print(f"Risk Tolerance: {user['risk_tolerance']}")
                print(f"Investment Goal: {user['investment_goal']}")
                print(f"Portfolio Value: ₨{user['portfolio_value']:,.2f}")
                print(f"Cash Balance: ₨{user['cash_balance']:,.2f}")
                print("-" * 30)
        else:
            print("❌ No users found in database")
    
    def verify_stocks(self):
        """Verify stock data"""
        print("\n" + "="*50)
        print("STOCK DATA")
        print("="*50)
        
        stocks = self.db.execute_query("SELECT code, name, sector, close_price, volume, change_percent FROM stocks LIMIT 10")
        
        if stocks:
            for stock in stocks:
                print(f"Code: {stock['code']}")
                print(f"Name: {stock['name']}")
                print(f"Sector: {stock['sector']}")
                print(f"Price: ₨{stock['close_price']:,.2f}")
                print(f"Volume: {stock['volume']:,}")
                print(f"Change: {stock['change_percent']:+.2f}%")
                print("-" * 30)
        else:
            print("❌ No stocks found in database")
    
    def verify_portfolios(self):
        """Verify portfolio data"""
        print("\n" + "="*50)
        print("PORTFOLIO DATA")
        print("="*50)
        
        portfolios = self.db.execute_query("SELECT user_id, total_value, total_invested, total_profit_loss, profit_loss_percent, cash_balance FROM portfolios LIMIT 5")
        
        if portfolios:
            for portfolio in portfolios:
                print(f"User ID: {portfolio['user_id']}")
                print(f"Total Value: ₨{portfolio['total_value']:,.2f}")
                print(f"Total Invested: ₨{portfolio['total_invested']:,.2f}")
                print(f"Profit/Loss: ₨{portfolio['total_profit_loss']:+,.2f}")
                print(f"Return %: {portfolio['profit_loss_percent']:+.2f}%")
                print(f"Cash Balance: ₨{portfolio['cash_balance']:,.2f}")
                print("-" * 30)
        else:
            print("❌ No portfolios found in database")
    
    def verify_investments(self):
        """Verify investment data"""
        print("\n" + "="*50)
        print("INVESTMENT DATA")
        print("="*50)
        
        investments = self.db.execute_query("""
            SELECT user_id, stock_code, stock_name, quantity, buy_price, current_price, 
                   profit_loss, profit_loss_percent, status 
            FROM investments 
            LIMIT 10
        """)
        
        if investments:
            for investment in investments:
                print(f"User: {investment['user_id']}")
                print(f"Stock: {investment['stock_code']} ({investment['stock_name']})")
                print(f"Quantity: {investment['quantity']}")
                print(f"Buy Price: ₨{investment['buy_price']:,.2f}")
                print(f"Current Price: ₨{investment['current_price']:,.2f}")
                print(f"P&L: ₨{investment['profit_loss']:+,.2f} ({investment['profit_loss_percent']:+.2f}%)")
                print(f"Status: {investment['status']}")
                print("-" * 30)
        else:
            print("❌ No investments found in database")
    
    def verify_recommendations(self):
        """Verify recommendation data"""
        print("\n" + "="*50)
        print("RECOMMENDATION DATA")
        print("="*50)
        
        recommendations = self.db.execute_query("""
            SELECT user_id, stock_code, stock_name, recommendation_type, confidence_score, 
                   expected_return, risk_level, created_at 
            FROM recommendations 
            LIMIT 10
        """)
        
        if recommendations:
            for rec in recommendations:
                print(f"User: {rec['user_id']}")
                print(f"Stock: {rec['stock_code']} ({rec['stock_name']})")
                print(f"Recommendation: {rec['recommendation_type'].upper()}")
                print(f"Confidence: {rec['confidence_score']:.1%}")
                print(f"Expected Return: {rec['expected_return']:+.1f}%")
                print(f"Risk Level: {rec['risk_level']}")
                print(f"Date: {rec['created_at'].strftime('%Y-%m-%d %H:%M')}")
                print("-" * 30)
        else:
            print("❌ No recommendations found in database")
    
    def verify_form_submissions(self):
        """Verify form submission data"""
        print("\n" + "="*50)
        print("FORM SUBMISSIONS")
        print("="*50)
        
        submissions = self.db.execute_query("""
            SELECT user_id, budget, sector_preference, risk_tolerance, time_horizon, 
                   target_profit, investment_goal, submission_date, recommendations_count 
            FROM user_form_submissions 
            LIMIT 5
        """)
        
        if submissions:
            for submission in submissions:
                print(f"User: {submission['user_id']}")
                print(f"Budget: ₨{submission['budget']:,.2f}")
                print(f"Sector: {submission['sector_preference']}")
                print(f"Risk: {submission['risk_tolerance']}")
                print(f"Time Horizon: {submission['time_horizon']}")
                print(f"Target Profit: {submission['target_profit']:.1f}%")
                print(f"Goal: {submission['investment_goal']}")
                print(f"Recommendations: {submission['recommendations_count']}")
                print(f"Date: {submission['submission_date'].strftime('%Y-%m-%d %H:%M')}")
                print("-" * 30)
        else:
            print("❌ No form submissions found in database")
    
    def verify_market_summary(self):
        """Verify market summary data"""
        print("\n" + "="*50)
        print("MARKET SUMMARY DATA")
        print("="*50)
        
        summaries = self.db.execute_query("""
            SELECT summary_date, total_volume, total_trades, market_cap, 
                   kse_100_index, kse_100_change 
            FROM market_summary 
            ORDER BY summary_date DESC 
            LIMIT 5
        """)
        
        if summaries:
            for summary in summaries:
                print(f"Date: {summary['summary_date']}")
                print(f"Volume: {summary['total_volume']:,}")
                print(f"Trades: {summary['total_trades']:,}")
                print(f"Market Cap: ₨{summary['market_cap']:,.0f}")
                print(f"KSE-100: {summary['kse_100_index']:,.2f}")
                print(f"Change: {summary['kse_100_change']:+.2f}%")
                print("-" * 30)
        else:
            print("❌ No market summary data found in database")
    
    def get_table_counts(self):
        """Get record counts for all tables"""
        print("\n" + "="*50)
        print("DATABASE RECORD COUNTS")
        print("="*50)
        
        tables = [
            'users', 'stocks', 'portfolios', 'investments', 'recommendations',
            'user_form_submissions', 'user_recommendations_history',
            'market_summary'
        ]
        
        for table in tables:
            try:
                result = self.db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['count'] if result else 0
                print(f"{table.capitalize()}: {count:,} records")
            except Exception as e:
                print(f"{table.capitalize()}: Error - {e}")
    
    def run_verification(self):
        """Run complete verification"""
        print("="*60)
        print("BullBearPK Mock Data Verification")
        print("="*60)
        
        try:
            # Test database connection
            if not self.db.test_connection():
                print("❌ Database connection failed. Please check your database configuration.")
                return False
            
            # Run all verifications
            self.get_table_counts()
            self.verify_users()
            self.verify_stocks()
            self.verify_portfolios()
            self.verify_investments()
            self.verify_recommendations()
            self.verify_form_submissions()
            self.verify_market_summary()
            
            print("\n" + "="*60)
            print("✅ Verification completed successfully!")
            print("="*60)
            return True
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return False

def main():
    """Main function to run verification"""
    verifier = MockDataVerifier()
    verifier.run_verification()

if __name__ == "__main__":
    main() 