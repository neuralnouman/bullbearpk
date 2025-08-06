import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../constants';
import { InvestmentFormData } from '../types';

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

// Investment Decision Types
export type DecisionType = 'buy' | 'sell' | 'hold' | 'pending';

export interface UserDecision {
  user_id: string;
  decision_type: DecisionType;
  stock_code: string;
  quantity?: number;
  price?: number;
  recommendation_id?: string;
}

export interface BatchUserDecisions {
  user_id: string;
  decisions: UserDecision[];
}

export interface DecisionResponse {
  success: boolean;
  message: string;
  transaction_id?: string;
  transaction_type?: string;
  portfolio_updated?: boolean;
  portfolio_summary?: any;
  timestamp?: string;
  status?: string;
  error?: string;
}

export interface BatchDecisionResponse {
  success: boolean;
  user_id: string;
  total_decisions: number;
  successful_decisions: number;
  failed_decisions: number;
  results: Array<{
    decision: UserDecision;
    result: DecisionResponse;
    status?: string;
    message?: string;
  }>;
}

/**
 * Submit investment form and get AI recommendations
 */
export const submitInvestmentForm = async (formData: InvestmentFormData, userId: string) => {
  try {
    // Convert form data to match our agentic framework's expected input
    const userInput = {
      budget: formData.budget,
      sector_preference: formData.sector,
      risk_tolerance: formData.risk_appetite,
      time_horizon: formData.time_horizon,
      target_profit: formData.target_profit,
      investment_goal: 'growth', // Default goal
    };

    const chatMessage = `I want to invest ${formData.budget} PKR in ${formData.sector} sector with ${formData.risk_appetite} risk tolerance for ${formData.time_horizon} term targeting ${formData.target_profit}% profit.`;

    const response = await apiClient.post(API_ENDPOINTS.ANALYSIS.RECOMMENDATIONS, {
      user_input: userInput,
      chat_message: chatMessage,
      user_id: userId
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

/**
 * Get recommendation history for a user
 */
export const getRecommendationHistory = async (userId: string, limit?: number, days?: number) => {
  try {
    const params = new URLSearchParams({ user_id: userId });
    if (limit) params.append('limit', limit.toString());
    if (days) params.append('days', days.toString());
    
    const response = await apiClient.get(`${API_ENDPOINTS.ANALYSIS.RECOMMENDATION_HISTORY}?${params}`);
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

/**
 * Get specific stock recommendation
 */
export const getStockRecommendation = async (stockCode: string) => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.ANALYSIS.STOCK_RECOMMENDATION.replace(':stock_code', stockCode));
    return response.data;
  } catch (error: any) {
    console.error('Error fetching stock recommendation:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to fetch stock recommendation'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to fetch stock recommendation'
    };
  }
};

/**
 * Get recommendation analytics
 */
export const getRecommendationAnalytics = async () => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.ANALYSIS.RECOMMENDATION_ANALYTICS);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching recommendation analytics:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        message: error.response.data.message || 'Failed to fetch recommendation analytics'
      };
    }
    
    return {
      success: false,
      message: error.message || 'Failed to fetch recommendation analytics'
    };
  }
};

/**
 * Handle single user investment decision
 */
export const handleUserDecision = async (decision: UserDecision): Promise<DecisionResponse> => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.INVESTMENT.USER_DECISION, decision);
    return response.data;
  } catch (error: any) {
    console.error('Error handling user decision:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        status: 'error',
        message: error.response.data.message || 'Failed to process investment decision',
        error: error.response.data.error
      };
    }
    
    return {
      success: false,
      status: 'error',
      message: error.message || 'Failed to process investment decision',
      error: error.message
    };
  }
};

/**
 * Handle multiple user investment decisions
 */
export const handleBatchDecisions = async (decisions: BatchUserDecisions): Promise<BatchDecisionResponse> => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.INVESTMENT.BATCH_DECISIONS, decisions);
    return response.data;
  } catch (error: any) {
    console.error('Error handling batch decisions:', error);
    
    if (error.response && error.response.data) {
      return {
        success: false,
        user_id: decisions.user_id,
        total_decisions: decisions.decisions.length,
        successful_decisions: 0,
        failed_decisions: decisions.decisions.length,
        results: decisions.decisions.map(decision => ({
          decision,
          result: {
            success: false,
            status: 'error',
            message: error.response.data.message || 'Failed to process batch decisions'
          }
        }))
      };
    }
    
    return {
      success: false,
      user_id: decisions.user_id,
      total_decisions: decisions.decisions.length,
      successful_decisions: 0,
      failed_decisions: decisions.decisions.length,
      results: decisions.decisions.map(decision => ({
        decision,
        result: {
          success: false,
          status: 'error',
          message: error.message || 'Failed to process batch decisions'
        }
      }))
    };
  }
};

/**
 * Buy stock based on recommendation
 */
export const buyStockFromRecommendation = async (
  userId: string, 
  stockCode: string, 
  quantity: number, 
  price: number, 
  recommendationId?: string
): Promise<DecisionResponse> => {
  return handleUserDecision({
    user_id: userId,
    decision_type: 'buy',
    stock_code: stockCode,
    quantity,
    price,
    recommendation_id: recommendationId
  });
};

/**
 * Sell stock
 */
export const sellStock = async (
  userId: string, 
  stockCode: string, 
  quantity: number, 
  price: number
): Promise<DecisionResponse> => {
  return handleUserDecision({
    user_id: userId,
    decision_type: 'sell',
    stock_code: stockCode,
    quantity,
    price
  });
};

/**
 * Hold stock (mark as hold)
 */
export const holdStock = async (
  userId: string, 
  stockCode: string
): Promise<DecisionResponse> => {
  return handleUserDecision({
    user_id: userId,
    decision_type: 'hold',
    stock_code: stockCode
  });
};

/**
 * Mark stock as pending for future consideration
 */
export const markStockAsPending = async (
  userId: string, 
  stockCode: string, 
  recommendationId?: string
): Promise<DecisionResponse> => {
  return handleUserDecision({
    user_id: userId,
    decision_type: 'pending',
    stock_code: stockCode,
    recommendation_id: recommendationId
  });
};

/**
 * Submit feedback for recommendations
 */
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