import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../constants';
import { Portfolio } from '../types';

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

interface BuyStockParams {
  userId: string;
  stockSymbol: string;
  amount: number;
}

interface SellStockParams {
  userId: string;
  investmentId: string;
  quantity: number;
}

// Initialize user if not exists
const initializeUser = async (userId: string): Promise<void> => {
  try {
    // Check if user exists by trying to get their portfolio
    await apiClient.get(`${API_ENDPOINTS.PORTFOLIO.GET}?user_id=${userId}`);
  } catch (error) {
    // If user doesn't exist, create a new user with default values
    console.log('Creating new user profile...');
    await apiClient.post('/users/initialize', { userId });
  }
};

export const getUserPortfolio = async (userId: string, forceRefresh: boolean = false): Promise<Portfolio> => {
  try {
    // Make sure user exists in the system
    await initializeUser(userId);
    
    // Refresh prices if requested
    if (forceRefresh) {
      await refreshPortfolioPrices(userId);
    }
    
    // Fetch portfolio data from API
    const response = await apiClient.get(`${API_ENDPOINTS.PORTFOLIO.GET}?user_id=${userId}`);
    
    // Get the custom total value if it exists
    const storedTotalValue = localStorage.getItem(`totalValue_${userId}`);
    if (storedTotalValue) {
      const customValue = parseFloat(storedTotalValue);
      if (!isNaN(customValue) && customValue > 0) {
        // Update the backend with the custom value
        await apiClient.post(`${API_ENDPOINTS.PORTFOLIO.UPDATE_VALUE}`, {
          userId,
          totalValue: customValue
        });
        
        // Refetch the portfolio with updated values
        const updatedResponse = await apiClient.get(`${API_ENDPOINTS.PORTFOLIO.GET}?user_id=${userId}`);
        return updatedResponse.data;
      }
    }
    
    return response.data;
  } catch (error) {
    console.error('Error fetching portfolio:', error);
    throw error;
  }
};

export const refreshPortfolioPrices = async (userId: string): Promise<boolean> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.PORTFOLIO.REFRESH_PRICES}`, { userId });
    return response.data.success;
  } catch (error) {
    console.error('Error refreshing portfolio prices:', error);
    return false;
  }
};

export const buyStock = async (params: BuyStockParams) => {
  try {
    // Make sure user exists in the system
    await initializeUser(params.userId);
    
    // Map the params to match what the backend expects
    const requestData = {
      userId: params.userId,
      stockSymbol: params.stockSymbol,
      amount: params.amount
    };
    
    // Send the buy request to the backend
    const response = await apiClient.post(API_ENDPOINTS.PORTFOLIO.ADD_INVESTMENT, requestData);
    return response.data;
  } catch (error: any) {
    console.error('Error buying stock:', error);
    
    // Return a structured error response
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to buy stock'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to buy stock'
    };
  }
};

export const sellStock = async (params: SellStockParams) => {
  try {
    // Make sure user exists in the system
    await initializeUser(params.userId);
    
    // Send the sell request to the backend
    const response = await apiClient.post(
      API_ENDPOINTS.PORTFOLIO.REMOVE_INVESTMENT.replace(':id', params.investmentId), 
      params
    );
    return response.data;
  } catch (error: any) {
    console.error('Error selling stock:', error);
    
    // Return a structured error response
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to sell stock'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to sell stock'
    };
  }
};

export const updatePortfolioValue = async (userId: string, totalValue: number) => {
  try {
    console.log(`Updating portfolio value for ${userId} to ${totalValue}`);
    
    // Make sure user exists in the system
    await initializeUser(userId);
    
    // Send the update request to the backend
    const response = await apiClient.post(`${API_ENDPOINTS.PORTFOLIO.UPDATE_VALUE}`, {
      userId,
      totalValue
    });
    
    console.log('Update response:', response.data);
    
    // Clear the stored value from localStorage after successful update
    if (response.data.success) {
      localStorage.removeItem(`totalValue_${userId}`);
    }
    
    return response.data;
  } catch (error: any) {
    console.error('Error updating portfolio value:', error);
    
    // Return a structured error response
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to update portfolio value'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to update portfolio value'
    };
  }
};