import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import { useAgenticStore } from '../store/agenticStore';
import MainLayout from '../components/MainLayout';
import InvestmentForm, { InvestmentFormData } from '../components/InvestmentForm';
import RecommendationSummary from '../components/RecommendationSummary';
import InvestmentDecisionCard from '../components/InvestmentDecisionCard';
import { DecisionResponse } from '../services/investmentService';
import { toast } from 'react-hot-toast';
import { 
  RefreshCw, 
  AlertCircle, 
  CheckCircle, 
  Brain,
  FileText,
  Shield,
  Users,
  Briefcase,
  ArrowLeft,
  TrendingUp,
  Target,
  Clock
} from 'lucide-react';

const InvestmentFormPage: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const [showOnboarding, setShowOnboarding] = useState(false);
  const [analysisStep, setAnalysisStep] = useState<'form' | 'analyzing' | 'results'>('form');
  const [decisionsMade, setDecisionsMade] = useState<Set<string>>(new Set());

  // Agentic store
  const {
    currentAnalysis,
    recommendations,
    isLoading,
    error,
    savedFormData,
    pastRecommendations,
    submitForm,
    loadUserHistory,
    clearAnalysis,
    setError,
    previousForm,
    previousRecommendations,
    recommendationChanges
  } = useAgenticStore();

  useEffect(() => {
    // Check if user has previous data
    if (user?.id && savedFormData) {
      setShowOnboarding(false);
      // Load user history if available
      loadUserHistory(user.id);
    } else if (user?.id) {
      // New user or no saved data
      setShowOnboarding(true);
    }
    
    // Check if there are existing recommendations to show
    if (recommendations && recommendations.length > 0) {
      setAnalysisStep('results');
    }
  }, [user, savedFormData, loadUserHistory, recommendations]);

  // Restore analysis state when component mounts with existing data
  useEffect(() => {
    if (currentAnalysis && recommendations && recommendations.length > 0) {
      setAnalysisStep('results');
      setDecisionsMade(new Set()); // Reset decisions made
    }
  }, [currentAnalysis, recommendations]);

  const handleFormSubmit = async (formData: InvestmentFormData) => {
    if (!user?.id) {
      toast.error('Please log in to submit investment analysis');
      return;
    }

    setAnalysisStep('analyzing');
    setDecisionsMade(new Set());

    try {
      await submitForm(formData, user.id);
      setAnalysisStep('results');
      toast.success('Investment analysis completed successfully!');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process investment analysis';
      setAnalysisStep('form');
      toast.error(errorMessage);
    }
  };

  const handleRefreshAnalysis = async () => {
    if (!user?.id || !savedFormData) {
      toast.error('No previous analysis to refresh');
      return;
    }

    setAnalysisStep('analyzing');
    setDecisionsMade(new Set());

    try {
      await submitForm(savedFormData, user.id, true);
      setAnalysisStep('results');
      toast.success('Analysis refreshed with latest data!');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to refresh analysis';
      setAnalysisStep('results');
      toast.error(errorMessage);
    }
  };

  const handleDecisionComplete = (result: DecisionResponse, stockCode: string) => {
    setDecisionsMade(prev => new Set([...prev, stockCode]));
    toast.success(`Decision processed for ${stockCode}`);
  };

  const handleViewPortfolio = () => {
    navigate('/portfolio');
  };

  const handleNewAnalysis = () => {
    navigate('/news');
  };

  const getAnalysisProgress = () => {
    if (analysisStep === 'analyzing') {
      return (
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-4"
          />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Analyzing Your Investment Profile
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Our AI is processing your preferences and market data...
          </p>
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <Brain className="w-4 h-4 text-blue-600" />
              <span>Analyzing market trends and patterns</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <Target className="w-4 h-4 text-green-600" />
              <span>Evaluating risk and return profiles</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <Shield className="w-4 h-4 text-purple-600" />
              <span>Generating personalized recommendations</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-4 mb-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Dashboard</span>
            </button>
          </div>
          
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Investment Analysis
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Get AI-powered investment recommendations based on your preferences
              </p>
            </div>
            
            {analysisStep === 'results' && (
              <div className="flex items-center space-x-4 mt-4 sm:mt-0">
                <motion.button
                  onClick={handleRefreshAnalysis}
                  disabled={isLoading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                  <span>Refresh Analysis</span>
                </motion.button>
                
                <motion.button
                  onClick={handleNewAnalysis}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Target className="w-4 h-4" />
                  <span>New Analysis</span>
                </motion.button>
              </div>
            )}
          </div>
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6"
          >
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-red-800 dark:text-red-200">{error}</span>
            </div>
          </motion.div>
        )}

        {/* Analysis Steps */}
        <AnimatePresence mode="wait">
          {analysisStep === 'form' && (
            <motion.div
              key="form"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="max-w-2xl mx-auto"
            >
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg p-8">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Brain className="w-8 h-8 text-blue-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    Investment Profile
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Tell us about your investment goals and preferences
                  </p>
                </div>

                <InvestmentForm onSubmit={handleFormSubmit} />

                {previousForm && (
                  <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Previous Analysis
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Budget: ₨{previousForm.budget?.toLocaleString()}, 
                      Risk: {previousForm.risk_tolerance}, 
                      Goal: {previousForm.investment_goal}
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {analysisStep === 'analyzing' && (
            <motion.div
              key="analyzing"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="max-w-2xl mx-auto"
            >
              <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg p-8">
                {getAnalysisProgress()}
              </div>
            </motion.div>
          )}

          {analysisStep === 'results' && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Analysis Summary */}
              {currentAnalysis && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg p-6"
                >
                  <div className="flex items-center space-x-2 mb-4">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      Analysis Complete
                    </h3>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <TrendingUp className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                      <div className="text-sm text-gray-600 dark:text-gray-400">Risk Profile</div>
                      <div className="font-semibold text-gray-900 dark:text-white">
                        {currentAnalysis.risk_profile?.risk_level || 'Moderate'}
                      </div>
                    </div>
                    
                    <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <Target className="w-8 h-8 text-green-600 mx-auto mb-2" />
                      <div className="text-sm text-gray-600 dark:text-gray-400">Recommendations</div>
                      <div className="font-semibold text-gray-900 dark:text-white">
                        {recommendations?.length || 0}
                      </div>
                    </div>
                    

                  </div>
                </motion.div>
              )}

              {/* Recommendations */}
              {recommendations && recommendations.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <RecommendationSummary 
                    recommendations={recommendations}
                    onBuyClick={(company) => {
                      // Handle buy click
                      console.log('Buy clicked for:', company);
                    }}
                  />
                </motion.div>
              )}

              {/* Individual Recommendation Cards */}
              {recommendations && recommendations.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="space-y-4"
                >
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    Detailed Recommendations
                  </h3>
                  
                  {recommendations.map((recommendation, index) => (
                    <motion.div
                      key={recommendation.stock_code}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                    >
                      <InvestmentDecisionCard
                        recommendation={recommendation}
                        onDecisionComplete={handleDecisionComplete}
                        onRefresh={() => {
                          // Handle refresh
                          console.log('Refresh recommendations');
                        }}
                      />
                    </motion.div>
                  ))}
                </motion.div>
              )}

              {/* Action Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4"
              >
                <motion.button
                  onClick={handleViewPortfolio}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Briefcase className="w-5 h-5" />
                  <span>View Portfolio</span>
                </motion.button>
                
                <motion.button
                  onClick={handleNewAnalysis}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <FileText className="w-5 h-5" />
                  <span>News Analysis</span>
                </motion.button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading State */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center py-12"
          >
            <div className="text-center">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Processing your request...</p>
            </div>
          </motion.div>
        )}
      </div>
    </MainLayout>
  );
};

export default InvestmentFormPage;