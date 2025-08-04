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
   * Fetch market data from the API
   * @returns Promise with market data response
   */
  getMarketData: async (filters?: any): Promise<MarketDataResponse> => {
    try {
      console.debug('Requesting market data from:', API_BASE_URL + API_ENDPOINTS.MARKET.DATA);
      
      let url = API_ENDPOINTS.MARKET.DATA;
      if (filters) {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString());
          }
        });
        url += `?${params.toString()}`;
      }
      
      const response = await apiClient.get(url);
      console.debug('Market data API response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching market data:', error);
      throw error;
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
  refreshMarketData: async (): Promise<MarketDataResponse> => {
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

