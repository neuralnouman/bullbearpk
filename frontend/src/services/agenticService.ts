import axios from 'axios';
import { API_BASE_URL } from '../constants';
import { AgenticResponse, InvestmentFormData } from '../types';

// Create axios instance for agentic workflow
const agenticClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes timeout for agentic workflow
});

// Add request interceptor
agenticClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for better error handling
agenticClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Agentic Service Error:', error);
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. The agentic analysis is taking longer than expected. Please try again.');
    }
    if (error.response?.status === 408) {
      throw new Error('Request timeout. The analysis is taking longer than expected.');
    }
    if (error.response?.status === 500) {
      throw new Error('Server error in agentic workflow. Please try again later.');
    }
    if (error.response?.status === 404) {
      throw new Error('Agentic endpoint not found. Please check if the backend is running.');
    }
    if (error.code === 'ERR_NETWORK') {
      throw new Error('Network error. Please check if the backend server is running.');
    }
    throw new Error(error.response?.data?.message || error.message || 'Agentic workflow failed');
  }
);

/**
 * Submit investment form and trigger agentic workflow
 */
export const submitAgenticForm = async (
  formData: InvestmentFormData,
  userId: string,
  refreshData: boolean = false
): Promise<AgenticResponse> => {
  try {
    // Convert form data to agentic framework input
    const userInput = {
      budget: formData.budget,
      risk_tolerance: formData.risk_appetite,
      time_horizon: formData.time_horizon,
      target_profit: formData.target_profit,
      investment_goal: 'growth', // Default goal
    };

    const chatMessage = `I want to invest ${formData.budget} PKR with ${formData.risk_appetite} risk tolerance for ${formData.time_horizon} term targeting ${formData.target_profit}% profit.`;

    const response = await agenticClient.post('/hybrid', {
      user_input: userInput,
      chat_message: chatMessage,
      user_id: userId,
      refresh_data: refreshData
    });

    // The backend now returns previous_form, previous_recommendations, and recommendation_changes
    return response.data as AgenticResponse;
  } catch (error: any) {
    console.error('Error in agentic workflow:', error);
    throw new Error(error.response?.data?.message || error.message || 'Failed to process investment analysis');
  }
};

/**
 * Get user's past recommendations and analysis
 */
export const getUserHistory = async (userId: string): Promise<any> => {
  try {
    const response = await agenticClient.get(`/analysis/recommendations/history?user_id=${userId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching user history:', error);
    throw new Error('Failed to fetch user history');
  }
};

/**
 * Submit feedback for recommendations
 */
export const submitAgenticFeedback = async (
  userId: string,
  feedback: string,
  recommendations: any[]
): Promise<any> => {
  try {
    const response = await agenticClient.post('/feedback', {
      user_id: userId,
      feedback,
      recommendations
    });
    return response.data;
  } catch (error: any) {
    console.error('Error submitting feedback:', error);
    throw new Error('Failed to submit feedback');
  }
};

/**
 * Refresh market data manually
 */
export const refreshMarketData = async (): Promise<any> => {
  try {
    const response = await agenticClient.post('/scrape');
    return response.data;
  } catch (error: any) {
    console.error('Error refreshing market data:', error);
    throw new Error('Failed to refresh market data');
  }
};

/**
 * Get real-time market status
 */
export const getMarketStatus = async (): Promise<any> => {
  try {
    const response = await agenticClient.get('/market/status');
    return response.data;
  } catch (error: any) {
    console.error('Error fetching market status:', error);
    // Return a default response if the API fails
    return {
      success: true,
      isOpen: true,
      lastUpdated: new Date().toISOString(),
      nextUpdate: new Date(Date.now() + 5 * 60 * 1000).toISOString(),
      marketHours: '09:15 - 15:30'
    };
  }
};

/**
 * Get news for top performing companies
 */
export const getTopCompaniesNews = async (): Promise<any> => {
  try {
    const response = await agenticClient.get('/market/news/top-companies');
    return response.data;
  } catch (error: any) {
    console.error('Error fetching top companies news:', error);
    throw new Error('Failed to fetch news data');
  }
}; 