# BullBearPK Frontend

A modern React TypeScript frontend for the BullBearPK investment analysis platform, designed to work seamlessly with the agentic backend system.

## 🚀 Features

- **AI-Powered Investment Recommendations**: Get personalized stock recommendations based on your investment preferences
- **Real-time Portfolio Management**: Track your investments with live updates
- **Investment Decision Handling**: Buy, sell, hold, or mark stocks as pending directly from recommendations
- **Market Data Visualization**: View market trends and stock performance
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Dark Mode Support**: Toggle between light and dark themes

## 🏗️ Architecture

### Core Components

#### 1. **Investment Decision System**
- `InvestmentDecisionCard`: Handles user decisions (buy/sell/hold/pending) for recommended stocks
- `InvestmentFormPage`: Main interface for submitting investment preferences and viewing recommendations
- Real-time integration with `manager_record_agent.py` backend

#### 2. **Portfolio Management**
- `PortfolioPage`: Complete portfolio overview with performance tracking
- `PortfolioSummary`: Key portfolio metrics and summary


#### 3. **Market Data**
- `MarketDataPage`: Real-time market data and stock information
- Integration with PSX (Pakistan Stock Exchange) data

### Service Layer

#### `investmentService.ts`
Handles all investment-related API calls:
- `submitInvestmentForm()`: Submit investment preferences for AI analysis
- `handleUserDecision()`: Process user investment decisions
- `buyStockFromRecommendation()`: Buy stocks based on recommendations
- `sellStock()`: Sell existing holdings
- `holdStock()`: Mark stocks as hold
- `markStockAsPending()`: Mark stocks for future consideration

#### `portfolioService.ts`
Manages portfolio data and operations:
- `getUserPortfolio()`: Fetch user portfolio data
- `initializeUser()`: Create new user portfolio
- `getPortfolioPerformance()`: Get performance metrics
- `getInvestmentHistory()`: Fetch transaction history
- `getPortfolioHoldings()`: Get current holdings
- `getSectorAllocation()`: Get sector distribution

#### `marketService.ts`
Handles market data operations:
- `getMarketData()`: Fetch current market data
- `searchStocks()`: Search for specific stocks
- `getStockDetails()`: Get detailed stock information
- `refreshMarketData()`: Trigger market data refresh
- `getSectors()`: Get sector information
- `getTopMovers()`: Get top gainers and losers

## 🔄 API Integration

### Backend Endpoints

The frontend is fully aligned with the backend API structure:

#### Investment Decisions
- `POST /api/investment/user-decision`: Handle single investment decision
- `POST /api/investment/user-decisions/batch`: Handle multiple decisions
- `POST /api/investment/portfolio/create`: Create new portfolio
- `GET /api/investment/portfolio/:user_id/status`: Get portfolio status

#### Portfolio Management
- `POST /api/portfolio/initialize`: Initialize user portfolio
- `GET /api/portfolio/:user_id`: Get user portfolio
- `POST /api/portfolio/:user_id/investments`: Add investment
- `GET /api/portfolio/:user_id/performance`: Get performance data
- `GET /api/portfolio/:user_id/history`: Get investment history

#### Market Data
- `GET /api/market/data`: Get market data
- `GET /api/market/stocks/search`: Search stocks
- `GET /api/market/stock/:symbol`: Get stock details
- `POST /api/market/refresh`: Refresh market data
- `GET /api/market/sectors`: Get sector data
- `GET /api/market/top-movers`: Get top movers

#### Analysis & Recommendations
- `POST /api/analysis/recommendations`: Get AI recommendations
- `GET /api/analysis/recommendations/history`: Get recommendation history
- `GET /api/analysis/recommendations/:stock_code`: Get specific stock recommendation
- `GET /api/analysis/recommendations/analytics`: Get recommendation analytics

## 🎯 User Workflow

### 1. Investment Form Submission
1. User fills out investment preferences (budget, risk tolerance, sector preference, etc.)
2. Form data is sent to `/api/analysis/recommendations`
3. Backend agentic system processes the request
4. AI recommendations are returned and displayed

### 2. Investment Decision Making
1. User views AI recommendations with detailed analysis
2. For each recommendation, user can:
   - **Buy**: Purchase the recommended stock
   - **Sell**: Sell existing holdings
   - **Hold**: Mark as hold for current holdings
   - **Pending**: Mark for future consideration
3. Decisions are sent to `/api/investment/user-decision`
4. `manager_record_agent.py` processes the decision
5. Portfolio is automatically updated

### 3. Portfolio Management
1. User can view their portfolio with real-time data
2. Performance metrics are displayed
3. Investment history and transaction records are available
4. Portfolio can be refreshed to get latest data

## 🛠️ Technology Stack

- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **React Router**: Client-side routing
- **Zustand**: Lightweight state management
- **Axios**: HTTP client for API calls
- **React Hot Toast**: Toast notifications


## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── InvestmentDecisionCard.tsx
│   │   ├── InvestmentForm.tsx
│   │   ├── PortfolioSummary.tsx
│   │   └── ...
│   ├── pages/              # Page components
│   │   ├── InvestmentFormPage.tsx
│   │   ├── PortfolioPage.tsx
│   │   ├── MarketDataPage.tsx
│   │   └── ...
│   ├── services/           # API service layer
│   │   ├── investmentService.ts
│   │   ├── portfolioService.ts
│   │   └── marketService.ts
│   ├── store/              # State management
│   │   └── authStore.ts
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts
│   ├── constants/          # App constants and config
│   │   └── index.ts
│   └── utils/              # Utility functions
├── public/                 # Static assets
└── package.json
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend server running on `http://localhost:5000`

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Preview
```bash
npm run preview
```

## 🔧 Configuration

### API Configuration
Update `src/constants/index.ts` to match your backend:
```typescript
export const API_BASE_URL = 'http://localhost:5000/api';
```

### Environment Variables
Create `.env.local` for environment-specific config:
```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_NAME=BullBearPK
```

## 🎨 Customization

### Styling
The app uses Tailwind CSS for styling. Custom styles can be added in:
- `src/index.css`: Global styles
- Component-specific styles in each component
- `tailwind.config.js`: Tailwind configuration

### Theming
Dark mode is supported through the `ThemeContext`. Toggle themes using:
```typescript
const { theme, toggleTheme } = useTheme();
```

## 🔍 Key Features

### Investment Decision Flow
1. **Recommendation Display**: AI recommendations are shown with detailed analysis
2. **Decision Options**: Each recommendation has buy/sell/hold/pending buttons
3. **Real-time Processing**: Decisions are processed immediately
4. **Portfolio Updates**: Portfolio is automatically updated after decisions
5. **Success Feedback**: Toast notifications confirm successful actions

### Portfolio Tracking
1. **Real-time Data**: Portfolio data is fetched from backend
2. **Performance Metrics**: Total value, returns, allocation percentages
3. **Portfolio Analytics**: Performance metrics and sector allocation
4. **Transaction History**: Complete history of all transactions
5. **Quick Actions**: Easy access to buy, sell, analyze, and recommend

### Market Data
1. **Live Market Data**: Real-time PSX market data
2. **Stock Search**: Search for specific stocks
3. **Stock Details**: Detailed information for each stock
4. **Sector Analysis**: Sector-wise market analysis
5. **Top Movers**: Gainers and losers tracking

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure backend server is running on `http://localhost:5000`
   - Check CORS configuration in backend
   - Verify API endpoints in `constants/index.ts`

2. **Portfolio Not Loading**
   - Check if user is properly initialized
   - Verify database connection in backend
   - Check browser console for errors

3. **Investment Decisions Failing**
   - Ensure user is authenticated
   - Check if stock data exists in database
   - Verify decision parameters are correct

### Debug Mode
Enable debug logging by setting:
```typescript
localStorage.setItem('debug', 'true');
```

## 📈 Performance

- **Lazy Loading**: Components are loaded on demand
- **Optimized Bundles**: Vite provides fast builds
- **Caching**: API responses are cached where appropriate
- **Error Boundaries**: Graceful error handling
- **Loading States**: Smooth loading experiences

## 🔒 Security

- **Input Validation**: All user inputs are validated
- **API Security**: Requests include proper headers
- **Error Handling**: Sensitive information is not exposed
- **CORS**: Proper CORS configuration with backend

## 🤝 Contributing

1. Follow the existing code structure
2. Use TypeScript for all new code
3. Add proper error handling
4. Include loading states
5. Test with the backend API
6. Update documentation as needed

## 📄 License

MIT License - see LICENSE file for details 