# Mock Data Population Summary

## Overview
Successfully populated the BullBearPK database with comprehensive mock data to test and validate backend functionality. The mock data covers multiple user scenarios, edge cases, and realistic investment situations.

## Database Records Created

### 📊 Record Counts
- **Users**: 11 records (including existing + new mock users)
- **Stocks**: 311 records (including existing market data + new mock stocks)
- **Portfolios**: 14 records
- **Investments**: 15 records
- **Recommendations**: 19 records
- **Form Submissions**: 12 records
- **Recommendation History**: 45 records
- **User Settings**: 6 records
- **Market Summary**: 30 records

## Mock User Profiles

### User 1: Ahmed Khan (user001)
- **Risk Tolerance**: Moderate
- **Investment Goal**: Long-term wealth building
- **Portfolio Value**: ₨150,000
- **Cash Balance**: ₨25,000
- **Preferred Sectors**: Banking, Energy, Cement
- **Investments**: HBL, OGDC, LUCK

### User 2: Fatima Ali (user002)
- **Risk Tolerance**: High
- **Investment Goal**: Aggressive growth
- **Portfolio Value**: ₨250,000
- **Cash Balance**: ₨50,000
- **Preferred Sectors**: Technology, Energy, Consumer Goods
- **Blacklisted**: HASCOL
- **Investments**: SYS, PTC, ENGRO

### User 3: Muhammad Hassan (user003)
- **Risk Tolerance**: Low
- **Investment Goal**: Conservative income
- **Portfolio Value**: ₨80,000
- **Cash Balance**: ₨15,000
- **Preferred Sectors**: Banking, Fertilizer
- **Blacklisted**: SYS, PTC
- **Investments**: HBL, UBL, FFC

### User 4: Ayesha Rahman (user004)
- **Risk Tolerance**: Moderate
- **Investment Goal**: Balanced growth
- **Portfolio Value**: ₨120,000
- **Cash Balance**: ₨30,000
- **Preferred Sectors**: Consumer Goods, Cement, Banking
- **Investments**: NESTLE, LUCK, MCB

### User 5: Omar Farooq (user005)
- **Risk Tolerance**: High
- **Investment Goal**: Maximum returns
- **Portfolio Value**: ₨300,000
- **Cash Balance**: ₨75,000
- **Preferred Sectors**: Energy, Technology, Chemical
- **Investments**: OGDC, SYS, LOTCHEM

## Stock Data

### 30 Pakistani Stocks Added
- **Banking**: HBL, UBL, MCB, NBP
- **Energy**: OGDC, PPL, ATRL, PSO, SHEL, MARI, NRL, PAKRI, POL
- **Cement**: LUCK, DGKC
- **Fertilizer**: FFC, EFERT, FFBL, FATIMA
- **Consumer Goods**: NESTLE, UNILEVER, COLGATE
- **Chemical**: ENGRO, ICI, LOTCHEM
- **Automobile**: INDU
- **Power**: KAPCO
- **Oil & Gas**: HASCOL
- **Telecommunications**: PTC
- **Technology**: SYS

### Realistic Stock Data Features
- Current prices ranging from ₨50 to ₨500
- Realistic volume data (100K to 5M shares)
- Price changes (-3% to +8%)
- Market cap calculations
- P/E ratios (8-25)
- Dividend yields (0-8%)

## Investment Scenarios

### Diverse Investment Patterns
1. **Conservative Portfolio** (User 3): Banking-focused with stable returns
2. **Aggressive Portfolio** (User 2): Tech-heavy with higher volatility
3. **Balanced Portfolio** (User 1): Mixed sectors with moderate risk
4. **Growth Portfolio** (User 4): Consumer goods and cement focus
5. **High-Risk Portfolio** (User 5): Energy and chemical stocks

### Investment Status Distribution
- **Active**: 60% of investments
- **Sold**: 20% of investments
- **Partial Sold**: 20% of investments

### Profit/Loss Scenarios
- **Profitable**: 40% of investments (up to +20% returns)
- **Loss-making**: 60% of investments (up to -18% losses)
- **Realistic P&L**: Ranging from -₨7,161 to +₨4,260

## Recommendation Data

### Recommendation Types
- **Strong Buy**: 25%
- **Buy**: 20%
- **Hold**: 30%
- **Sell**: 15%
- **Strong Sell**: 10%

### Confidence Scores
- Range: 61% to 94%
- Average: 75%
- Realistic distribution across confidence levels

### Expected Returns
- Range: -2.3% to +23.6%
- Average: +8.5%
- Correlated with recommendation types

## Form Submissions

### Investment Form Scenarios
1. **Conservative**: ₨25K budget, Banking sector, 8% target
2. **Moderate**: ₨50K budget, Banking sector, 12.5% target
3. **Aggressive**: ₨100K budget, Technology sector, 25% target
4. **Balanced**: ₨75K budget, Consumer Goods sector, 15% target
5. **High-Risk**: ₨150K budget, Energy sector, 30% target

### Time Horizons
- **Short-term**: 20%
- **Medium-term**: 40%
- **Long-term**: 40%

## Market Summary Data

### 30 Days of Market Data
- **Volume**: 100M to 500M shares daily
- **Trades**: 30K to 80K transactions daily
- **Market Cap**: ₨7-8.5 trillion
- **KSE-100 Index**: 40K to 49K points
- **Daily Changes**: -3% to +3%

## User Settings

### Comprehensive Settings Structure
```json
{
  "notifications": {
    "email_alerts": true,
    "sms_alerts": false,
    "price_alerts": true,
    "news_alerts": true
  },
  "display_preferences": {
    "currency": "PKR",
    "language": "en",
    "theme": "light",
    "timezone": "Asia/Karachi"
  },
  "trading_preferences": {
    "auto_reinvest_dividends": true/false,
    "stop_loss_percentage": 5-15%,
    "take_profit_percentage": 10-25%,
    "max_position_size": 10-30%
  },
  "risk_management": {
    "max_portfolio_risk": 10-30%,
    "sector_concentration_limit": 20-40%,
    "single_stock_limit": 5-15%
  }
}
```

## Edge Cases Covered

### Empty Portfolios
- Users with zero investments
- Users with only cash balances
- New users with no trading history

### Risk Tolerance Variations
- **Low Risk**: Conservative income focus
- **Moderate Risk**: Balanced growth approach
- **High Risk**: Aggressive growth strategies

### Investment Status Variations
- Active investments with unrealized gains/losses
- Sold investments with realized P&L
- Partial sales with mixed status

### Market Conditions
- Bull market scenarios (positive returns)
- Bear market scenarios (negative returns)
- Sideways market scenarios (minimal changes)

## Data Quality Features

### Realistic Relationships
- Portfolio values match investment totals
- Cash balances align with user profiles
- Recommendation confidence correlates with expected returns
- Investment durations match buy dates

### Data Consistency
- Foreign key relationships maintained
- Date ranges are logical and sequential
- Currency formatting consistent (PKR)
- Percentage calculations accurate

### Edge Case Handling
- Users with blacklisted stocks
- Investments with zero quantities
- Recommendations with expired dates
- Form submissions with various risk tolerances

## Testing Scenarios Enabled

### Backend API Testing
- User authentication and profiles
- Portfolio management and calculations
- Investment tracking and P&L
- Recommendation generation and history
- Form submission processing
- Market data retrieval

### Frontend Integration Testing
- Dashboard data display
- Portfolio visualization
- Investment forms
- Recommendation displays
- User settings management

### Database Performance Testing
- Large dataset queries
- Complex joins and aggregations
- Real-time data updates
- Concurrent user scenarios

## Files Created

1. **`populate_mock_data.py`**: Main population script
2. **`verify_mock_data.py`**: Data verification script
3. **`MOCK_DATA_SUMMARY.md`**: This summary document

## Usage Instructions

### To Populate Mock Data
```bash
cd backend
python populate_mock_data.py
```

### To Verify Data
```bash
cd backend
python verify_mock_data.py
```

### Sample Queries for Testing
```sql
-- Check user profiles
SELECT * FROM users WHERE user_id LIKE 'user%';

-- View portfolio performance
SELECT user_id, total_value, total_profit_loss, profit_loss_percent 
FROM portfolios WHERE user_id LIKE 'user%';

-- Check investment diversity
SELECT user_id, COUNT(*) as investment_count, 
       AVG(profit_loss_percent) as avg_return
FROM investments 
GROUP BY user_id;

-- Review recommendations
SELECT user_id, recommendation_type, confidence_score, expected_return
FROM recommendations 
ORDER BY created_at DESC;
```

## Next Steps

1. **Test Backend APIs**: Use the mock data to test all API endpoints
2. **Validate Frontend**: Ensure the frontend displays data correctly
3. **Performance Testing**: Test with realistic data volumes
4. **Edge Case Testing**: Verify handling of various scenarios
5. **Integration Testing**: Test end-to-end workflows

The mock data provides a solid foundation for comprehensive testing and validation of the BullBearPK system before going live. 