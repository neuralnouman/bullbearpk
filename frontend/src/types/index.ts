// User and Authentication Types
export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  createdAt: string
  investmentProfile?: InvestmentProfile
}

export interface InvestmentProfile {
  totalInvested: number
  totalReturns: number
  riskTolerance: 'low' | 'medium' | 'high'
  preferredSectors: string[]
}

// Chat and Conversation Types
export interface Message {
  id: string
  content: string
  sender: 'user' | 'assistant'
  timestamp: Date
  metadata?: MessageMetadata
}

export interface MessageMetadata {
  stockSymbols?: string[]
  sentiment?: 'positive' | 'negative' | 'neutral'
  confidence?: number
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

// Stock Market Types
export interface StockData {
  code: string
  name: string
  sector: string
  open_price: number
  high_price: number
  low_price: number
  close_price: number
  volume: number
  change: number
  change_percent: number
  timestamp: string
}

export interface MarketIndex {
  name: string
  value: number
  change: number
  changePercent: number
  lastUpdated: string
}

// Investment Types
export interface Investment {
  id: string
  userId?: string
  user_id?: string
  stockSymbol?: string
  stock_code?: string
  companyName?: string
  stock_name?: string
  quantity?: number
  currentQuantity?: number
  current_quantity?: number
  purchasePrice?: number
  buyPrice?: number
  buy_price?: number
  currentPrice?: number
  current_price?: number
  purchaseDate?: string
  buy_date?: string
  sector: string
  status: 'active' | 'sold' | 'partial_sold' | 'pending' | 'cancelled'
}

export interface PortfolioMetrics {
  totalInvested: number
  totalReturns: number
  returnPercentage: number
  cashBalance: number
  totalHoldings: number
  activeInvestments: number
  totalValue: number
}

export interface Portfolio {
  totalValue: number
  totalInvested: number
  totalReturns: number
  returnPercentage: number
  cashBalance?: number
  investments: Investment[]
  allocation: SectorAllocation[]
}

export interface SectorAllocation {
  sector: string
  value: number
  percentage: number
  color: string
}

// News and Analysis Types
export interface NewsArticle {
  id: string
  title: string
  content: string
  source: string
  publishedAt: string
  sentiment: 'positive' | 'negative' | 'neutral'
  sentimentScore: number
  relevantCompanies: string[]
  url: string
  link: string
  imageUrl?: string
}

export interface MarketAnalysis {
  summary: string
  sentiment: 'bullish' | 'bearish' | 'neutral'
  keyFactors: string[]
  recommendations: Recommendation[]
  riskLevel: 'low' | 'medium' | 'high'
  timeHorizon: 'short' | 'medium' | 'long'
}

export interface Recommendation {
  type: 'buy' | 'sell' | 'hold'
  stockSymbol: string
  companyName: string
  targetPrice: number
  reasoning: string
  confidence: number
  sector: string
}

// Agentic Framework Types
export interface AgenticRecommendation {
  stock_code: string
  stock_name: string
  sector: string
  recommendation_type: 'buy' | 'hold' | 'sell'
  confidence_score: number
  technical_analysis: TechnicalAnalysis
  news_sentiment: NewsSentiment
  reasoning: string
  risk_level: string
  expected_return: number
  allocation_percent: number
}

export interface TechnicalAnalysis {
  stock_code: string
  stock_name: string
  sector: string
  current_price: number
  rsi: number
  macd: {
    macd: number
    signal: number
    histogram: number
  }
  bollinger_bands: {
    upper: number
    middle: number
    lower: number
  }
  support_resistance: {
    support: number
    resistance: number
  }
  price_trend: string
  momentum: number
  volatility: number
  confidence_score: number
  analysis_timestamp: string
}

export interface NewsSentiment {
  overall_sentiment: string
  sentiment_score: number
  news_count: number
  positive_news: number
  negative_news: number
  neutral_news: number
  key_events: string[]
  risk_factors: string[]
  opportunities: string[]
  recommendation: string
  confidence: number
  analysis_summary: string
}

export interface RiskProfile {
  risk_level: string
  risk_score: number
  market_volatility: number
  sentiment_impact: number
  recommendations: string
  timestamp: string
}

export interface UserHistory {
  user_id: string
  total_investments: number
  preferred_sectors: string[]
  portfolio_summary: {
    total_invested: number
    total_returns: number
    return_percentage: number
  }
  recent_activity: any[]
  timestamp: string
}

export interface PortfolioUpdate {
  user_id: string
  current_holdings: any[]
  total_invested: number
  total_profit_loss: number
  profit_loss_percentage: number
  timestamp: string
}

export interface RecommendationChangeSummary {
  new_recommendations: Array<{
    stock_code: string;
    recommendation: string;
    confidence: number;
    reason: string;
  }>;
  removed_recommendations: Array<{
    stock_code: string;
    old_recommendation: string;
    reason: string;
  }>;
  changed_recommendations: Array<{
    stock_code: string;
    old_recommendation: string;
    new_recommendation: string;
    old_confidence: number;
    new_confidence: number;
    reason: string;
  }>;
  unchanged_recommendations: Array<{
    stock_code: string;
    recommendation: string;
    confidence: number;
  }>;
}

export interface PreviousForm {
  id: number;
  user_id: string;
  budget: number;
  sector_preference: string;
  risk_tolerance: string;
  time_horizon: string;
  target_profit: number;
  investment_goal: string;
  submission_date: string;
  recommendations_count: number;
}

export interface AgenticResponse {
  success: boolean;
  message?: string;
  data: {
    recommendations: AgenticRecommendation[];
    stock_analysis: TechnicalAnalysis[];
    news_analysis: Record<string, NewsSentiment>;
    risk_profile: RiskProfile;
    portfolio_update: PortfolioUpdate;
    user_history: UserHistory;
    previous_form?: PreviousForm;
    previous_recommendations?: AgenticRecommendation[];
    recommendation_changes?: RecommendationChangeSummary;
  };
  errors?: string[];
  timestamp: string;
  user_id: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}

// Form Types
export interface LoginForm {
  email: string
  password: string
}

export interface RegisterForm {
  name: string
  email: string
  password: string
  confirmPassword: string
}

export interface InvestmentQuery {
  amount: number
  riskTolerance: 'low' | 'medium' | 'high'
  timeHorizon: 'short' | 'medium' | 'long'
  preferredSectors?: string[]
  excludedSectors?: string[]
}

export interface InvestmentFormData {
  budget: number
  sector: string
  risk_appetite: 'low' | 'medium' | 'high'
  time_horizon: 'short' | 'medium' | 'long'
  target_profit: number
}

// Theme Types
export type Theme = 'light' | 'dark'

// Error Types
export interface AppError {
  code: string
  message: string
  details?: string
}

// Utility Types
export type Status = 'idle' | 'loading' | 'success' | 'error'

export interface LoadingState {
  status: Status
  error?: string
}



// Notification Types
export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  read: boolean
  actionUrl?: string
}

// Search and Filter Types
export interface SearchFilters {
  query?: string
  sector?: string
  minPrice?: number
  maxPrice?: number
  minMarketCap?: number
  maxMarketCap?: number
  sortBy?: 'name' | 'price' | 'change' | 'volume' | 'marketCap'
  sortOrder?: 'asc' | 'desc'
}

// WebSocket Types
export interface WebSocketMessage {
  type: 'stock_update' | 'news_alert' | 'chat_response' | 'market_alert'
  data: StockData | NewsArticle | MarketAnalysis | Record<string, unknown>
  timestamp: string
}