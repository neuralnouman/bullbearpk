# BullBearPK Backend

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Create database
mysql -u root -p
CREATE DATABASE bullbearpk;

# Import schema
mysql -u root -p bullbearpk < database/mysql_schema.sql
```

### 3. Configure Database
Update `database_config.py` with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'bullbearpk'
}
```

### 4. Start Server
```bash
python api_server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

- **Health Check:** `GET /`
- **Market Data:** `GET /api/market/data`
- **Recommendations:** `POST /api/analysis/recommendations`
- **Portfolio Management:** `GET/POST /api/portfolio/*`
- **Investment Decisions:** `POST /api/investment/user-decision`

## System Components

- **10 Agents** working in harmony
- **27 API Endpoints** covering all functionality
- **Complete LangGraph Workflow** orchestration
- **MySQL Database** with comprehensive schema
- **Flask API** with all necessary endpoints

## Features

- ✅ Real-time stock data scraping from PSX
- ✅ Advanced technical analysis
- ✅ News sentiment analysis
- ✅ Risk profiling and portfolio management
- ✅ Investment decision handling
- ✅ Complete agentic workflow 