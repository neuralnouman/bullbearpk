import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../constants';
import { Portfolio, Investment } from '../types';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Portfolio service interfaces
export interface InitializeUserParams {
  user_id: string;
  name?: string;
  email?: string;
  risk_tolerance?: string;
  investment_goal?: string;
  initial_cash?: number;
  sector_preference?: string[];
}

export interface AddInvestmentParams {
  user_id: string;
  stock_code: string;
  quantity: number;
  price: number;
  transaction_type: 'buy' | 'sell';
}

export interface UpdateInvestmentParams {
  user_id: string;
  investment_id: string;
  quantity?: number;
  price?: number;
  status?: string;
}

export interface PortfolioPerformance {
  total_value: number;
  total_invested: number;
  total_returns: number;
  return_percentage: number;
  period: string;
  timestamp: string;
}

export interface InvestmentHistory {
  investment_id: string;
  stock_code: string;
  stock_name: string;
  transaction_type: string;
  quantity: number;
  price: number;
  total_amount: number;
  transaction_date: string;
  status: string;
}

/**
 * Initialize user portfolio
 */
export const initializeUser = async (params: InitializeUserParams) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.PORTFOLIO.INITIALIZE, params);
    return response.data;
  } catch (error: any) {
    console.error('Error initializing user:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to initialize user'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to initialize user'
    };
  }
};

/**
 * Get user portfolio
 */
export const getUserPortfolio = async (userId: string): Promise<Portfolio> => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.PORTFOLIO.GET.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching portfolio:', error);
    throw error;
  }
};

/**
 * Add investment to portfolio
 */
export const addInvestment = async (params: AddInvestmentParams) => {
  try {
    const response = await apiClient.post(
      API_ENDPOINTS.PORTFOLIO.ADD_INVESTMENT.replace(':user_id', params.user_id),
      {
        stock_code: params.stock_code,
        quantity: params.quantity,
        price: params.price,
        transaction_type: params.transaction_type
      }
    );
    return response.data;
  } catch (error: any) {
    console.error('Error adding investment:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to add investment'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to add investment'
    };
  }
};

/**
 * Update investment
 */
export const updateInvestment = async (params: UpdateInvestmentParams) => {
  try {
    const response = await apiClient.put(
      API_ENDPOINTS.PORTFOLIO.UPDATE_INVESTMENT
        .replace(':user_id', params.user_id)
        .replace(':investment_id', params.investment_id),
      {
        quantity: params.quantity,
        price: params.price,
        status: params.status
      }
    );
    return response.data;
  } catch (error: any) {
    console.error('Error updating investment:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to update investment'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to update investment'
    };
  }
};

/**
 * Get portfolio performance
 */
export const getPortfolioPerformance = async (userId: string): Promise<PortfolioPerformance> => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.PORTFOLIO.PERFORMANCE.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching portfolio performance:', error);
    throw error;
  }
};

/**
 * Get investment history
 */
export const getInvestmentHistory = async (userId: string): Promise<InvestmentHistory[]> => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.PORTFOLIO.HISTORY.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching investment history:', error);
    throw error;
  }
};

/**
 * Create portfolio snapshot
 */
export const createPortfolioSnapshot = async (userId: string) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.PORTFOLIO.SNAPSHOT.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error creating portfolio snapshot:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to create portfolio snapshot'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to create portfolio snapshot'
    };
  }
};

/**
 * Get portfolio holdings
 */
export const getPortfolioHoldings = async (userId: string) => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.INVESTMENT.PORTFOLIO_HOLDINGS.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching portfolio holdings:', error);
    throw error;
  }
};

/**
 * Get sector allocation
 */
export const getSectorAllocation = async (userId: string) => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.INVESTMENT.SECTOR_ALLOCATION.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching sector allocation:', error);
    throw error;
  }
};

/**
 * Get top holdings
 */
export const getTopHoldings = async (userId: string) => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.INVESTMENT.TOP_HOLDINGS.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching top holdings:', error);
    throw error;
  }
};

/**
 * Get portfolio status
 */
export const getPortfolioStatus = async (userId: string) => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.INVESTMENT.PORTFOLIO_STATUS.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching portfolio status:', error);
    throw error;
  }
};

/**
 * Get portfolio analytics
 */
export const getPortfolioAnalytics = async (userId: string) => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.INVESTMENT.PORTFOLIO_ANALYTICS.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching portfolio analytics:', error);
    throw error;
  }
};

/**
 * Update investment status
 */
export const updateInvestmentStatus = async (userId: string, stockCode: string, status: string) => {
  try {
    const response = await apiClient.put(
      API_ENDPOINTS.INVESTMENT.UPDATE_INVESTMENT_STATUS
        .replace(':user_id', userId)
        .replace(':stock_code', stockCode),
      { status }
    );
    return response.data;
  } catch (error: any) {
    console.error('Error updating investment status:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to update investment status'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to update investment status'
    };
  }
};

/**
 * Create portfolio snapshot (investment endpoint)
 */
export const createInvestmentPortfolioSnapshot = async (userId: string) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.INVESTMENT.PORTFOLIO_SNAPSHOT.replace(':user_id', userId));
    return response.data;
  } catch (error: any) {
    console.error('Error creating investment portfolio snapshot:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to create portfolio snapshot'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to create portfolio snapshot'
    };
  }
};