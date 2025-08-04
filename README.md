# 🎯 **Complete BullBearPK Agentic System - Files, Usage & Flow**

## 📁 **System Architecture Overview**

```
Frontend (React) → Backend (Flask API) → LangGraph Agentic Framework → MySQL Database
```

---

## 🤖 **Complete Agentic Workflow**

### **1. User Input Phase**
```
User fills form → Input Taker Agent → LangGraph Framework
```

### **2. Data Collection Phase**
```
Stock Scraper → Stock Analyzer → News Scraper → News Analyzer
```

### **3. Analysis Phase**
```
Risk Checker → Past Investments Checker → Portfolio Checker
```

### **4. Decision Phase**
```
Recommendation Agent → Manager Record Agent → Database Updates
```

---

## 📁 **File Structure & Purpose**

### **🏗️ Core Framework Files**

| File | Purpose | Status |
|------|---------|--------|
| `agentic_framework.py` | **Main LangGraph orchestrator** - Manages entire workflow | ✅ Active |
| `api_server.py` | **Flask API server** - Handles HTTP requests | ✅ Active |
| `database_config.py` | **Database connection manager** - MySQL operations | ✅ Active |

### **🤖 Agent Files**

| Agent | File | Purpose | Status |
|-------|------|---------|--------|
| **Input Taker** | `agents/input_taker.py` | **User input validation & processing** | ✅ Active |
| **Stock Scraper** | `agents/fin_scraper.py` | **Scrapes PSX stock data** | ✅ Active |
| **Stock Analyzer** | `agents/advanced_stock_analyzer.py` | **Advanced technical analysis** | ✅ Active |
| **News Scraper** | `agents/news_scraper.py` | **Scrapes news for top stocks** | ✅ Active |
| **News Analyzer** | `agents/news_analyzer.py` | **News sentiment analysis** | ✅ Active |
| **Risk Checker** | `agents/risk_checker.py` | **User risk profile analysis** | ✅ Active |
| **Past Investments** | `agents/past_investments_checker.py` | **Investment history analysis** | ✅ Active |
| **Portfolio Checker** | `agents/portfolio_checker.py` | **Current portfolio analysis** | ✅ Active |
| **Recommendation** | `agents/recommendation_agent.py` | **Generates final recommendations** | ✅ Active |
| **Manager Record** | `agents/manager_record_agent.py` | **Handles user investment decisions** | ✅ Active |

### **🌐 API Files**

| File | Purpose | Status |
|------|---------|--------|
| `api/investment_routes.py` | **Investment management endpoints** | ✅ Active |
| `api/recommendation_routes.py` | **Recommendation endpoints** | ✅ Active |

### **🗄️ Database Files**

| File | Purpose | Status |
|------|---------|--------|
| `database/mysql_schema.sql` | **Complete MySQL schema** | ✅ Active |
| `portfolio_manager.py` | **Portfolio management utilities** | ✅ Active |

---

## 🔄 **Detailed Workflow Flow**

### **Phase 1: User Input & Validation**
```
1. User fills investment form
2. Input Taker Agent validates input
3. Creates user profile if new user
4. Passes data to LangGraph framework
```

### **Phase 2: Data Collection**
```
5. Stock Scraper Agent:
   - Scrapes PSX website
   - Gets current stock prices
   - Saves to stocks table
   - Clears old data first

6. Stock Analyzer Agent:
   - Performs technical analysis
   - Calculates 60+ indicators
   - Ranks top 10 performers
   - Saves to stock_analysis table
```

### **Phase 3: News Analysis**
```
7. News Scraper Agent:
   - Takes top 10 stocks
   - Scrapes RSS feeds & Google News
   - Saves to news_records table
   - Clears old news data

8. News Analyzer Agent:
   - Analyzes sentiment for each stock
   - Calculates impact scores
   - Saves to news_analysis table
```

### **Phase 4: User Analysis**
```
9. Risk Checker Agent:
   - Analyzes user's past behavior
   - Calculates risk tolerance
   - Considers portfolio risk
   - Returns comprehensive risk profile

10. Past Investments Checker Agent:
    - Analyzes investment history
    - Calculates performance metrics
    - Identifies patterns
    - Returns investment insights

11. Portfolio Checker Agent:
    - Analyzes current holdings
    - Calculates portfolio health
    - Identifies new vs existing users
    - Returns portfolio status
```

### **Phase 5: Recommendation Generation**
```
12. Recommendation Agent:
    - Combines all analysis data
    - Generates personalized recommendations
    - Saves to recommendations table
    - Returns detailed recommendations
```

### **Phase 6: User Decision Handling**
```
13. Manager Record Agent:
    - Handles user investment decisions
    - Updates investments table
    - Updates portfolios table
    - Tracks transaction history
```

---

## 📊 **Database Tables & Purpose**

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | **User profiles** | user_id, risk_tolerance, investment_goal |
| `stocks` | **Current stock data** | code, name, close_price, sector |
| `stock_analysis` | **Technical analysis results** | 60+ technical indicators |
| `news_records` | **Raw scraped news** | stock_code, title, content, link |
| `news_analysis` | **News sentiment analysis** | sentiment_score, key_events |
| `investments` | **User investment records** | transaction_type, quantity, P&L |
| `portfolios` | **Portfolio snapshots** | total_value, performance metrics |
| `recommendations` | **Generated recommendations** | stock_code, reasoning, confidence |

---

## 🎯 **Agent Capabilities Summary**

### **Input Taker Agent**
- ✅ Validates user input
- ✅ Creates user profiles
- ✅ Formats data for framework
- ✅ Interactive terminal interface

### **Stock Scraper Agent**
- ✅ Scrapes PSX website
- ✅ Handles WebDriver setup
- ✅ Clears old data
- ✅ Saves to database

### **Stock Analyzer Agent**
- ✅ 60+ technical indicators
- ✅ Performance ranking
- ✅ Risk metrics
- ✅ Top 10 filtering

### **News Scraper Agent**
- ✅ RSS feed scraping
- ✅ Google News scraping
- ✅ Duplicate removal
- ✅ Content hashing

### **News Analyzer Agent**
- ✅ Sentiment analysis
- ✅ Impact assessment
- ✅ Key events extraction
- ✅ Risk factor identification

### **Risk Checker Agent**
- ✅ Behavioral analysis
- ✅ Portfolio risk assessment
- ✅ Comprehensive risk scoring
- ✅ Risk profile generation

### **Past Investments Checker Agent**
- ✅ Performance analysis
- ✅ Pattern recognition
- ✅ Sector analysis
- ✅ Investment recommendations

### **Portfolio Checker Agent**
- ✅ Portfolio health analysis
- ✅ New user detection
- ✅ Performance tracking
- ✅ Diversification analysis

### **Recommendation Agent**
- ✅ Multi-factor analysis
- ✅ Personalized recommendations
- ✅ Confidence scoring
- ✅ Database storage

### **Manager Record Agent**
- ✅ Buy/Sell/Hold decisions
- ✅ Transaction tracking
- ✅ Portfolio updates
- ✅ P&L calculation

---

## 🔗 **API Endpoints**

### **Investment Management**
- `POST /api/investment/user-decision` - Handle single decision
- `POST /api/investment/user-decisions/batch` - Handle multiple decisions
- `GET /api/investment/portfolio/<user_id>/status` - Portfolio status
- `GET /api/investment/portfolio/<user_id>/history` - Investment history

### **Recommendations**
- `POST /api/analysis/recommendations` - Generate recommendations
- `GET /api/analysis/recommendations/history` - Recommendation history

---

## 🚀 **System Benefits**

1. **🎯 End-to-End Automation** - Complete investment workflow
2. **⚡ Real-time Analysis** - Live data processing
3. **🤖 AI-Powered Decisions** - Multi-agent intelligence
4. **📈 Performance Tracking** - Comprehensive analytics
5. **🔄 Scalable Architecture** - Modular agent system
6. **🔒 Data Integrity** - Proper database management
7. **🌐 API Ready** - Frontend integration ready
8. **🧪 Tested** - Comprehensive testing suite

---

## 🎯 **Current Status: PRODUCTION READY**

The BullBearPK system is now **complete and production-ready** with:

- ✅ **9 Active Agents** working in harmony
- ✅ **Complete LangGraph Workflow** orchestration
- ✅ **MySQL Database** with comprehensive schema
- ✅ **Flask API** with all necessary endpoints
- ✅ **Manager Record Agent** for decision handling
- ✅ **Comprehensive Testing** and error handling

**The system can now handle the complete investment lifecycle from data collection to decision execution!** 🚀

---

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- MySQL 8.0+
- Node.js 16+ (for frontend)

### **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

### **Database Setup**
```bash
# Create database
mysql -u root -p
CREATE DATABASE bullbearpk;

# Import schema
mysql -u root -p bullbearpk < database/mysql_schema.sql
```

### **Configuration**
Update `database_config.py` with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'bullbearpk'
}
```

### **Running the System**
```bash
# Start the API server
python api_server.py

# Test the agentic framework
python agents/input_taker.py
```

---

## 📝 **Usage Examples**

### **Generate Recommendations**
```python
from agentic_framework import AgenticFramework

framework = AgenticFramework()
result = await framework.run_workflow({
    'user_id': 'user123',
    'budget': 10000,
    'risk_tolerance': 'moderate',
    'investment_goal': 'growth'
})
```

### **Handle User Decision**
```python
from agents.manager_record_agent import handle_user_investment_decision

result = await handle_user_investment_decision(
    user_id='user123',
    decision_type='buy',
    stock_code='OGDC',
    quantity=100,
    price=85.50
)
```

---

## 🤝 **Contributing**

This is a comprehensive AI-powered investment analysis platform for the Pakistan Stock Exchange (PSX). The system uses advanced agentic frameworks to provide personalized investment recommendations.

---

## 📄 **License**

This project is proprietary software for BullBearPK investment platform. 