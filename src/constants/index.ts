// Application Information
export const APP_NAME = 'BullBearPK'
export const APP_DESCRIPTION = 'AI-powered investment analysis for Pakistan Stock Exchange'
export const APP_VERSION = '1.0.0'

// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api'
export const WEBSOCKET_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000'

// Pakistan Stock Exchange Constants
export const PSX_SECTORS = [
  'Technology',
  'Banking',
  'Textile',
  'Cement',
  'Energy',
  'Pharmaceutical',
  'Fertilizer',
  'Automobile',
  'Food & Personal Care',
  'Oil & Gas',
  'Power',
  'Steel',
  'Chemicals',
  'Real Estate',
  'Insurance',
  'Leasing',
  'Investment Banks',
  'Mutual Funds',
] as const

export const MAJOR_PSX_INDICES = [
  { name: 'KSE-100', symbol: 'KSE100' },
  { name: 'KSE-30', symbol: 'KSE30' },
  { name: 'KMI-30', symbol: 'KMI30' },
  { name: 'All Share', symbol: 'ALLSHR' },
] as const

// Top PSX Companies by Market Cap
export const TOP_PSX_COMPANIES = [
  { symbol: 'HUBCO', name: 'Hub Power Company Limited' },
  { symbol: 'TRG', name: 'TRG Pakistan Limited' },
  { symbol: 'LUCK', name: 'Lucky Cement Limited' },
  { symbol: 'ENGRO', name: 'Engro Corporation Limited' },
  { symbol: 'BAFL', name: 'Bank Alfalah Limited' },
  { symbol: 'MCB', name: 'MCB Bank Limited' },
  { symbol: 'UBL', name: 'United Bank Limited' },
  { symbol: 'HBL', name: 'Habib Bank Limited' },
  { symbol: 'NESTLE', name: 'Nestlé Pakistan Limited' },
  { symbol: 'PSO', name: 'Pakistan State Oil Company Limited' },
] as const

// Investment Risk Levels
export const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
} as const

export const RISK_DESCRIPTIONS = {
  [RISK_LEVELS.LOW]: 'Conservative investment with stable returns',
  [RISK_LEVELS.MEDIUM]: 'Balanced approach with moderate risk and returns',
  [RISK_LEVELS.HIGH]: 'Aggressive investment with high potential returns',
} as const

// Investment Time Horizons
export const TIME_HORIZONS = {
  SHORT: 'short',
  MEDIUM: 'medium',
  LONG: 'long',
} as const

export const TIME_HORIZON_DESCRIPTIONS = {
  [TIME_HORIZONS.SHORT]: '1-6 months',
  [TIME_HORIZONS.MEDIUM]: '6 months - 2 years',
  [TIME_HORIZONS.LONG]: '2+ years',
} as const

// Chart Time Frames
export const CHART_TIMEFRAMES = [
  { label: '1D', value: '1D' },
  { label: '1W', value: '1W' },
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '6M', value: '6M' },
  { label: '1Y', value: '1Y' },
  { label: 'ALL', value: 'ALL' },
] as const

// Currency Information
export const CURRENCIES = {
  PKR: { symbol: '₨', name: 'Pakistani Rupee' },
  USD: { symbol: '$', name: 'US Dollar' },
  EUR: { symbol: '€', name: 'Euro' },
  GBP: { symbol: '£', name: 'British Pound' },
} as const

// News Sources
export const NEWS_SOURCES = [
  'Dawn Business',
  'Business Recorder',
  'Profit by Pakistan Today',
  'The Express Tribune',
  'ARY News Business',
  'Dunya News Business',
  'Express News Business',
  'Geo News Business',
] as const

// Market Status
export const MARKET_STATUS = {
  OPEN: 'open',
  CLOSED: 'closed',
  PRE_MARKET: 'pre-market',
  AFTER_HOURS: 'after-hours',
} as const

// PSX Trading Hours (Pakistan Time)
export const PSX_TRADING_HOURS = {
  OPEN: '09:15',
  CLOSE: '15:30',
  PRE_MARKET_OPEN: '08:45',
  PRE_MARKET_CLOSE: '09:15',
} as const

// Pagination
export const DEFAULT_PAGE_SIZE = 20
export const MAX_PAGE_SIZE = 100

// Local Storage Keys
export const STORAGE_KEYS = {
  THEME: 'theme',
  AUTH_TOKEN: 'auth-token',
  USER_PREFERENCES: 'user-preferences',
  WATCHLIST: 'watchlist',
  RECENT_SEARCHES: 'recent-searches',
} as const

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    PROFILE: '/auth/profile',
  },
  STOCKS: {
    LIST: '/stocks',
    DETAILS: '/stocks/:symbol',
    SEARCH: '/stocks/search',
    HISTORICAL: '/stocks/:symbol/historical',
  },
  PORTFOLIO: {
    GET: '/portfolio',
    ADD_INVESTMENT: '/portfolio/investments',
    REMOVE_INVESTMENT: '/portfolio/investments/:id',
    ANALYTICS: '/portfolio/analytics',
  },
  NEWS: {
    LIST: '/news',
    SENTIMENT: '/news/sentiment',
    COMPANY: '/news/company/:symbol',
  },
  ANALYSIS: {
    CHAT: '/analysis/chat',
    RECOMMENDATIONS: '/analysis/recommendations',
    MARKET_SUMMARY: '/analysis/market-summary',
  },
} as const

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your internet connection.',
  INVALID_CREDENTIALS: 'Invalid email or password.',
  REGISTRATION_FAILED: 'Registration failed. Please try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  MARKET_CLOSED: 'Market is currently closed.',
  INSUFFICIENT_FUNDS: 'Insufficient funds for this investment.',
} as const

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in!',
  REGISTRATION_SUCCESS: 'Account created successfully!',
  LOGOUT_SUCCESS: 'Successfully logged out!',
  INVESTMENT_ADDED: 'Investment added to your portfolio!',
  INVESTMENT_REMOVED: 'Investment removed from your portfolio!',
  PROFILE_UPDATED: 'Profile updated successfully!',
  SETTINGS_SAVED: 'Settings saved successfully!',
} as const

// Chart Colors
export const CHART_COLORS = {
  PRIMARY: '#0ea5e9',
  SECONDARY: '#6366f1',
  SUCCESS: '#22c55e',
  DANGER: '#ef4444',
  WARNING: '#f59e0b',
  INFO: '#3b82f6',
  LIGHT: '#e5e7eb',
  DARK: '#374151',
} as const

// Sector Colors (for charts and visualizations)
export const SECTOR_COLORS = {
  Technology: '#0ea5e9',
  Banking: '#22c55e',
  Textile: '#f59e0b',
  Cement: '#6366f1',
  Energy: '#ef4444',
  Pharmaceutical: '#8b5cf6',
  Fertilizer: '#06b6d4',
  Automobile: '#84cc16',
  'Food & Personal Care': '#f97316',
  'Oil & Gas': '#ec4899',
  Power: '#14b8a6',
  Steel: '#64748b',
  Chemicals: '#a855f7',
  'Real Estate': '#10b981',
  Insurance: '#3b82f6',
  Leasing: '#f43f5e',
  'Investment Banks': '#6d28d9',
  'Mutual Funds': '#059669',
} as const

// Feature Flags
export const FEATURES = {
  REAL_TIME_DATA: false,
  ADVANCED_CHARTS: true,
  PORTFOLIO_TRACKING: true,
  NEWS_SENTIMENT: true,
  AI_RECOMMENDATIONS: true,
  PUSH_NOTIFICATIONS: false,
  DARK_MODE: true,
  MOBILE_APP: false,
} as const

// Rate Limiting
export const RATE_LIMITS = {
  API_REQUESTS_PER_MINUTE: 100,
  CHAT_MESSAGES_PER_MINUTE: 20,
  NEWS_UPDATES_PER_HOUR: 1000,
} as const

// Validation Rules
export const VALIDATION_RULES = {
  PASSWORD_MIN_LENGTH: 6,
  NAME_MIN_LENGTH: 2,
  NAME_MAX_LENGTH: 50,
  EMAIL_MAX_LENGTH: 100,
  INVESTMENT_MIN_AMOUNT: 1000, // PKR
  INVESTMENT_MAX_AMOUNT: 10000000, // PKR
} as const 