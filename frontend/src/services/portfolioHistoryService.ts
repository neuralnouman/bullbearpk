import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../constants';

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

export interface PortfolioHistoryDataPoint {
  date: string;
  value: number;
  invested?: number;
  cash_balance?: number;
}

export interface TimeframeOption {
  value: string;
  label: string;
}

export const timeframeOptions: TimeframeOption[] = [
  { value: '1D', label: 'Today' },
  { value: '1W', label: 'Week' },
  { value: '1M', label: 'Month' },
  { value: '3M', label: '3 Months' },
  { value: '6M', label: '6 Months' },
  { value: '1Y', label: 'Year' },
  { value: 'ALL', label: 'All Time' },
];

/**
 * Get portfolio performance history by timeframe
 */
export const getPortfolioHistory = async (
  userId: string,
  timeframe: string = '1M'
): Promise<PortfolioHistoryDataPoint[]> => {
  try {
    const response = await apiClient.get(
      API_ENDPOINTS.PORTFOLIO.HISTORY_PERFORMANCE
        .replace(':user_id', userId)
        .replace(':timeframe', timeframe)
    );
    
    return response.data.data || [];
  } catch (error: any) {
    console.error('Error fetching portfolio history:', error);
    
    if (error.response && error.response.status === 404) {
      // If no history data yet, return empty array
      return [];
    }
    
    throw error;
  }
};

/**
 * Get portfolio value and invested amount history
 */
export const getPortfolioValueHistory = async (
  userId: string,
  timeframe: string = '1M'
): Promise<{
  date: string;
  invested: number;
  value: number;
}[]> => {
  try {
    const response = await apiClient.get(
      API_ENDPOINTS.PORTFOLIO.VALUE_HISTORY
        .replace(':user_id', userId)
        .replace(':timeframe', timeframe)
    );
    
    return response.data.data || [];
  } catch (error: any) {
    console.error('Error fetching portfolio value history:', error);
    
    if (error.response && error.response.status === 404) {
      // If no history data yet, return empty array
      return [];
    }
    
    throw error;
  }
};

// Sample data generation functions removed - portfolio now uses only real user data
