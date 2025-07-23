import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../constants';
import { InvestmentFormData } from '../components/InvestmentForm';

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

export const submitInvestmentForm = async (formData: InvestmentFormData, userId: string, refreshData: boolean = false) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.ANALYSIS.RECOMMENDATIONS, {
      user_input: {
        budget: formData.budget,
        sector_preference: formData.sector,
        risk_tolerance: formData.risk_appetite,
        time_horizon: formData.time_horizon,
        target_profit: formData.target_profit,
      },
      user_id: userId,
      refresh_data: refreshData
    });
    
    return response.data;
  } catch (error: any) {
    console.error('Error submitting investment form:', error);
    
    // Return a structured error response
    if (error.response && error.response.data) {
      return {
        success: false,
        error: error.response.data.message || 'Failed to get recommendations'
      };
    }
    
    return {
      success: false,
      error: error.message || 'Failed to get recommendations'
    };
  }
};

export const getRecommendationHistory = async (userId: string) => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.ANALYSIS.RECOMMENDATIONS}/history?user_id=${userId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching recommendation history:', error);
    
    // Return a structured error response
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to fetch recommendation history'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to fetch recommendation history'
    };
  }
};

export const submitFeedback = async (userId: string, feedback: string, recommendations: any[]) => {
  try {
    const response = await apiClient.post('/feedback', {
      user_id: userId,
      feedback,
      recommendations
    });
    return response.data;
  } catch (error: any) {
    console.error('Error submitting feedback:', error);
    
    // Return a structured error response
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to submit feedback'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to submit feedback'
    };
  }
};