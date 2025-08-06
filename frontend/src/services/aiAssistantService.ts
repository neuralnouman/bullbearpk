import axios from 'axios';
import { API_BASE_URL } from '../constants';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  success: boolean;
  message: string;
  timestamp: string;
  user_id: string;
}

export interface ChatHistoryResponse {
  success: boolean;
  chat_history: ChatMessage[];
  user_id: string;
}

export interface ClearHistoryResponse {
  success: boolean;
  message: string;
  user_id: string;
}

/**
 * Send a message to the AI assistant
 */
export const sendChatMessage = async (
  message: string,
  userId: string,
  chatHistory: ChatMessage[] = []
): Promise<ChatResponse> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/ai/chat`, {
      message,
      user_id: userId,
      chat_history: chatHistory
    });
    return response.data;
  } catch (error: any) {
    console.error('Error sending chat message:', error);
    throw new Error(error.response?.data?.message || 'Failed to send message');
  }
};

/**
 * Get chat history for a user
 */
export const getChatHistory = async (
  userId: string,
  limit: number = 50
): Promise<ChatHistoryResponse> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/ai/chat/history`, {
      params: {
        user_id: userId,
        limit
      }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error getting chat history:', error);
    throw new Error(error.response?.data?.message || 'Failed to get chat history');
  }
};

/**
 * Clear chat history for a user
 */
export const clearChatHistory = async (userId: string): Promise<ClearHistoryResponse> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/ai/chat/clear`, {
      user_id: userId
    });
    return response.data;
  } catch (error: any) {
    console.error('Error clearing chat history:', error);
    throw new Error(error.response?.data?.message || 'Failed to clear chat history');
  }
}; 