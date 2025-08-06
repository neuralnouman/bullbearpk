import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AgenticResponse, AgenticRecommendation, TechnicalAnalysis, NewsSentiment } from '../types';
import { submitAgenticForm, getUserHistory, submitAgenticFeedback } from '../services/agenticService';

interface AgenticState {
  // Current analysis state
  currentAnalysis: AgenticResponse | null;
  recommendations: AgenticRecommendation[];
  stockAnalysis: TechnicalAnalysis[];
  newsAnalysis: Record<string, NewsSentiment>;
  riskProfile: any;
  portfolioUpdate: any;
  userHistory: any;
  previousForm?: import('../types').PreviousForm;
  previousRecommendations?: import('../types').AgenticRecommendation[];
  recommendationChanges?: import('../types').RecommendationChangeSummary;
  
  // Loading and error states
  isLoading: boolean;
  isAnalyzing: boolean;
  error: string | null;
  
  // User data persistence
  savedFormData: any;
  pastRecommendations: AgenticRecommendation[];
  analysisHistory: AgenticResponse[];
  
  // Actions
  submitForm: (formData: any, userId: string, refreshData?: boolean) => Promise<void>;
  loadUserHistory: (userId: string) => Promise<void>;
  submitFeedback: (userId: string, feedback: string, recommendations: any[]) => Promise<void>;
  clearAnalysis: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  saveFormData: (formData: any) => void;
  updateRecommendations: (recommendations: AgenticRecommendation[]) => void;
}

export const useAgenticStore = create<AgenticState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentAnalysis: null,
      recommendations: [],
      stockAnalysis: [],
      newsAnalysis: {},
      riskProfile: null,
      portfolioUpdate: null,
      userHistory: null,
      previousForm: undefined,
      previousRecommendations: undefined,
      recommendationChanges: undefined,
      
      isLoading: false,
      isAnalyzing: false,
      error: null,
      
      savedFormData: null,
      pastRecommendations: [],
      analysisHistory: [],
      
      // Submit form and trigger agentic workflow
      submitForm: async (formData: any, userId: string, refreshData: boolean = false) => {
        set({ isAnalyzing: true, error: null });
        
        try {
          // Save form data
          set({ savedFormData: formData });
          
          // Submit to agentic workflow
          const response = await submitAgenticForm(formData, userId, refreshData);
          
          if (response.success) {
            set({
              currentAnalysis: response,
              recommendations: response.data?.recommendations || [],
              stockAnalysis: response.data?.stock_analysis || [],
              newsAnalysis: response.data?.news_analysis || {},
              riskProfile: response.data?.risk_profile || null,
              portfolioUpdate: response.data?.portfolio_update || null,
              userHistory: response.data?.user_history || null,
              previousForm: response.data?.previous_form,
              previousRecommendations: response.data?.previous_recommendations,
              recommendationChanges: response.data?.recommendation_changes,
              isAnalyzing: false,
              error: null
            });
            
            // Add to analysis history
            const { analysisHistory } = get();
            set({
              analysisHistory: [response, ...analysisHistory.slice(0, 9)] // Keep last 10
            });
          } else {
            throw new Error(response.message || 'Analysis failed');
          }
        } catch (error: any) {
          set({
            isAnalyzing: false,
            error: error.message || 'Failed to process investment analysis'
          });
          throw error;
        }
      },
      
      // Load user's past analysis and recommendations
      loadUserHistory: async (userId: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const history = await getUserHistory(userId);
          
          if (history.success) {
            set({
              pastRecommendations: history.data?.recommendations || [],
              analysisHistory: history.data?.analysis_history || [],
              isLoading: false
            });
          } else {
            throw new Error(history.message || 'Failed to load user history');
          }
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Failed to load user history'
          });
        }
      },
      
      // Submit feedback for recommendations
      submitFeedback: async (userId: string, feedback: string, recommendations: any[]) => {
        try {
          const response = await submitAgenticFeedback(userId, feedback, recommendations);
          
          if (!response.success) {
            throw new Error(response.message || 'Failed to submit feedback');
          }
        } catch (error: any) {
          set({ error: error.message || 'Failed to submit feedback' });
          throw error;
        }
      },
      
      // Clear current analysis
      clearAnalysis: () => {
        set({
          currentAnalysis: null,
          recommendations: [],
          stockAnalysis: [],
          newsAnalysis: {},
          riskProfile: null,
          portfolioUpdate: null,
          userHistory: null,
          error: null
        });
      },
      
      // Set loading state
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
      
      // Set error state
      setError: (error: string | null) => {
        set({ error });
      },
      
      // Save form data
      saveFormData: (formData: any) => {
        set({ savedFormData: formData });
      },
      
      // Update recommendations
      updateRecommendations: (recommendations: AgenticRecommendation[]) => {
        set({ recommendations });
      }
    }),
    {
      name: 'agentic-storage',
      partialize: (state) => ({
        savedFormData: state.savedFormData,
        pastRecommendations: state.pastRecommendations,
        analysisHistory: state.analysisHistory,
        currentAnalysis: state.currentAnalysis,
        recommendations: state.recommendations,
        stockAnalysis: state.stockAnalysis,
        newsAnalysis: state.newsAnalysis,
        riskProfile: state.riskProfile,
        portfolioUpdate: state.portfolioUpdate,
        userHistory: state.userHistory,
        previousForm: state.previousForm,
        previousRecommendations: state.previousRecommendations,
        recommendationChanges: state.recommendationChanges
      })
    }
  )
); 