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
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  marketCap: number
  sector: string
  lastUpdated: string
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
  userId: string
  stockSymbol: string
  companyName: string
  quantity: number
  purchasePrice: number
  currentPrice: number
  purchaseDate: string
  sector: string
  status: 'active' | 'sold'
}

export interface Portfolio {
  totalValue: number
  totalInvested: number
  totalReturns: number
  returnPercentage: number
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

// Chart Data Types
export interface ChartDataPoint {
  timestamp: string
  value: number
  label?: string
}

export interface PriceHistory {
  symbol: string
  data: ChartDataPoint[]
  timeframe: '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | 'ALL'
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