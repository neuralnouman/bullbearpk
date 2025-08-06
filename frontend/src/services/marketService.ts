import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../constants';
import { StockData } from '../types';

// Define MarketDataResponse interface based on the current implementation
interface MarketSummary {
  top_gainer: StockData;
  top_loser: StockData;
  highest_volume: StockData;
}

interface ScrapeInfo {
  timestamp: string;
  total_stocks: number;
  gainers: number;
  losers: number;
  unchanged: number;
}

interface MarketDataResponse {
  scrape_info: ScrapeInfo;
  market_summary: MarketSummary;
  stocks: StockData[];
}

interface StockDetailsResponse {
  stock: StockData;
  analysis?: any;
  news?: any;
}

interface SectorData {
  sector: string;
  stocks: StockData[];
  total_market_cap: number;
  avg_change: number;
}

interface TopMoversResponse {
  gainers: StockData[];
  losers: StockData[];
  highest_volume: StockData[];
}

interface MarketDataOptions {
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
  sector?: string;
  min_change?: number;
  max_change?: number;
  min_volume?: number;
  max_volume?: number;
  min_market_cap?: number;
  max_market_cap?: number;
  search_query?: string;
}

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

// Market data service functions
export const marketService = {
  /**
   * Get all available stocks
   * @returns Promise with an array of all stocks
   */
  getAllStocks: async (): Promise<StockData[]> => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.MARKET.ALL_STOCKS);
      return response.data.stocks || [];
    } catch (error: any) {
      console.error('Error fetching all stocks:', error);
      return [];
    }
  },

  /**
   * Get market data with optional filtering
   * @param options Filtering and sorting options
   * @returns Promise with market data
   */
  getMarketData: async (options: MarketDataOptions = {}): Promise<MarketDataResponse> => {
    try {
      let url = API_ENDPOINTS.MARKET.DATA;
      
      // Add query parameters if provided
      if (Object.keys(options).length > 0) {
        const params = new URLSearchParams();
        Object.entries(options).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString());
          }
        });
        url += `?${params.toString()}`;
      }
      
      const response = await apiClient.get(url);
      console.debug('Market data API response:', response.data);
      
      // Check if the response indicates an error
      if (response.data && response.data.success === false) {
        const errorMessage = response.data.message || 'Unknown error occurred';
        const errorType = response.data.error || 'UNKNOWN_ERROR';
        
        // Handle specific error types
        if (errorType === 'DATABASE_CONNECTION_ERROR') {
          throw new Error('Database connection failed. Please check if MySQL is running and credentials are correct.');
        } else if (errorType === 'NO_DATA_AVAILABLE') {
          throw new Error('No market data available. The database may be empty or the stocks table does not exist.');
        } else {
          throw new Error(errorMessage);
        }
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching market data:', error);
      
      // Provide more specific error messages based on the error
      if (error.response?.status === 503) {
        throw new Error('Database service unavailable. Please check if MySQL is running.');
      } else if (error.response?.status === 404) {
        throw new Error('No market data available. The database may be empty.');
      } else if (error.response?.status === 500) {
        throw new Error('Server error occurred while fetching market data.');
      } else if (error.code === 'ERR_NETWORK') {
        throw new Error('Network error. Please check if the backend server is running.');
      } else {
        throw new Error(error.message || 'Failed to fetch market data');
      }
    }
  },

  /**
   * Search for stocks by query
   * @param query Search query string
   * @returns Promise with filtered stock data
   */
  searchStocks: async (query: string): Promise<MarketDataResponse> => {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.MARKET.SEARCH}?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Error searching stocks:', error);
      throw error;
    }
  },

  /**
   * Get stock details by symbol
   * @param symbol Stock symbol/code
   * @returns Promise with stock details
   */
  getStockDetails: async (symbol: string): Promise<StockDetailsResponse> => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.MARKET.STOCK_DETAILS.replace(':symbol', symbol));
      return response.data;
    } catch (error) {
      console.error(`Error fetching details for stock ${symbol}:`, error);
      throw error;
    }
  },
  
  /**
   * Refresh market data by triggering a new scrape
   * @returns Promise with fresh market data
   */
  refreshMarketData: async (): Promise<any> => {
    try {
      console.debug('Refreshing market data...');
      const response = await apiClient.post(API_ENDPOINTS.MARKET.REFRESH);
      console.debug('Market data refresh response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error refreshing market data:', error);
      throw error;
    }
  },

  /**
   * Get market sectors data
   * @returns Promise with sector data
   */
  getSectors: async (): Promise<SectorData[]> => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.MARKET.SECTORS);
      return response.data;
    } catch (error) {
      console.error('Error fetching sectors data:', error);
      throw error;
    }
  },

  /**
   * Get top movers (gainers and losers)
   * @returns Promise with top movers data
   */
  getTopMovers: async (): Promise<TopMoversResponse> => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.MARKET.TOP_MOVERS);
      return response.data;
    } catch (error) {
      console.error('Error fetching top movers:', error);
      throw error;
    }
  },
};

// Export individual functions for easier use
export const getMarketData = marketService.getMarketData;
export const searchStocks = marketService.searchStocks;
export const getStockDetails = marketService.getStockDetails;
export const refreshMarketData = marketService.refreshMarketData;
export const getSectors = marketService.getSectors;
export const getTopMovers = marketService.getTopMovers;

