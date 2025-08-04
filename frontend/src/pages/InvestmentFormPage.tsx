import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import MainLayout from '../components/MainLayout';
import InvestmentForm, { InvestmentFormData } from '../components/InvestmentForm';
import RecommendationSummary from '../components/RecommendationSummary';
import InvestmentDecisionCard from '../components/InvestmentDecisionCard';
import { submitInvestmentForm, submitFeedback, DecisionResponse } from '../services/investmentService';
import { AgenticRecommendation } from '../types';
import { toast } from 'react-hot-toast';
import { RefreshCw, TrendingUp, AlertCircle } from 'lucide-react';

interface AgenticResponse {
  success: boolean;
  message: string;
  data: {
    recommendations: AgenticRecommendation[];
    stock_analysis: any[];
    news_analysis: any;
    risk_profile: any;
    portfolio_update: any;
    user_history: any;
  };
  errors: string[];
  timestamp: string;
  user_id: string;
}

const InvestmentFormPage: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agenticResponse, setAgenticResponse] = useState<AgenticResponse | null>(null);
  const [savedFormData, setSavedFormData] = useState<InvestmentFormData | null>(null);
  const [decisionsMade, setDecisionsMade] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Check if user has previously submitted form data
    const storedData = localStorage.getItem('investmentFormData');
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData);
        setSavedFormData(parsedData);
        
        // If we have saved form data, fetch recommendations automatically
        fetchRecommendations(parsedData);
      } catch (err) {
        console.error('Error parsing stored form data:', err);
      }
    }
  }, []);

  const fetchRecommendations = async (formData: InvestmentFormData, refresh: boolean = false) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await submitInvestmentForm(formData, user?.id || 'user001', refresh);
      
      if (!result.success) {
        setError(result.error || result.message || 'Failed to get recommendations');
        return;
      }
      
      setAgenticResponse(result);
      setDecisionsMade(new Set()); // Reset decisions when new recommendations are fetched
    } catch (err: any) {
      console.error('Error fetching recommendations:', err);
      setError(err.response?.data?.message || err.message || 'Failed to get recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = async (formData: InvestmentFormData) => {
    // Save form data to localStorage
    localStorage.setItem('investmentFormData', JSON.stringify(formData));
    setSavedFormData(formData);
    
    await fetchRecommendations(formData);
  };

  const handleDecisionComplete = (result: DecisionResponse, stockCode: string) => {
    setDecisionsMade(prev => new Set([...prev, stockCode]));
    
    if (result.portfolio_updated) {
      toast.success('Portfolio updated successfully!');
    }
  };

  const handleRefreshRecommendations = () => {
    if (savedFormData) {
      fetchRecommendations(savedFormData, true);
    }
  };

  const handleViewPortfolio = () => {
    navigate('/portfolio');
  };

  // Extract recommendations from agentic response
  const recommendations = agenticResponse?.data?.recommendations || [];
  const hasRecommendations = recommendations.length > 0;
  const allDecisionsMade = recommendations.length > 0 && decisionsMade.size === recommendations.length;

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Investment Preferences</h2>
              <InvestmentForm 
                onSubmit={handleFormSubmit} 
                initialData={savedFormData || undefined}
              />
            </div>
          </div>
          
          <div className="lg:col-span-2">
            {loading ? (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
                <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
                <h3 className="text-lg font-semibold mb-2">Analyzing Market Data</h3>
                <p className="text-gray-600">Our AI is analyzing stocks and generating personalized recommendations...</p>
              </div>
            ) : error ? (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                  <h3 className="text-lg font-semibold text-red-600">Error</h3>
                </div>
                <p className="text-gray-700 mb-4">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
                >
                  Try Again
                </button>
              </div>
            ) : hasRecommendations ? (
              <div className="space-y-6">
                {/* Header with actions */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                        AI Recommendations
                      </h2>
                      <p className="text-gray-600 dark:text-gray-400">
                        Based on your investment preferences, here are our top recommendations
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={handleRefreshRecommendations}
                        className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
                      >
                        <RefreshCw className="w-4 h-4 inline mr-1" />
                        Refresh
                      </button>
                      <button
                        onClick={handleViewPortfolio}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                      >
                        View Portfolio
                      </button>
                    </div>
                  </div>

                  {/* Summary Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        <div>
                          <div className="text-sm text-green-600">Buy Recommendations</div>
                          <div className="text-2xl font-bold text-green-700">
                            {recommendations.filter(r => r.recommendation_type === 'buy').length}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2">
                        <AlertCircle className="w-5 h-5 text-yellow-600" />
                        <div>
                          <div className="text-sm text-yellow-600">Hold Recommendations</div>
                          <div className="text-2xl font-bold text-yellow-700">
                            {recommendations.filter(r => r.recommendation_type === 'hold').length}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="w-5 h-5 text-red-600" />
                        <div>
                          <div className="text-sm text-red-600">Sell Recommendations</div>
                          <div className="text-2xl font-bold text-red-700">
                            {recommendations.filter(r => r.recommendation_type === 'sell').length}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Progress indicator */}
                  {allDecisionsMade && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 bg-green-600 rounded-full"></div>
                        <span className="text-green-800 font-medium">
                          All recommendations processed! Check your portfolio for updates.
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Recommendations Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {recommendations.map((recommendation, index) => (
                    <InvestmentDecisionCard
                      key={`${recommendation.stock_code}-${index}`}
                      recommendation={recommendation}
                      onDecisionComplete={(result) => handleDecisionComplete(result, recommendation.stock_code)}
                      onRefresh={() => {
                        // Optionally refresh portfolio data
                        toast.success('Portfolio updated!');
                      }}
                    />
                  ))}
                </div>

                {/* Risk Profile Summary */}
                {agenticResponse?.data?.risk_profile && (
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Risk Profile Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600">Risk Level</div>
                        <div className="font-semibold">{agenticResponse.data.risk_profile.risk_level}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Risk Score</div>
                        <div className="font-semibold">{agenticResponse.data.risk_profile.risk_score}/100</div>
                      </div>
                      <div className="md:col-span-2">
                        <div className="text-sm text-gray-600 mb-2">Recommendations</div>
                        <p className="text-sm text-gray-700">{agenticResponse.data.risk_profile.recommendations}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
                <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Recommendations Yet</h3>
                <p className="text-gray-600 mb-4">
                  Submit your investment preferences to get personalized AI recommendations
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default InvestmentFormPage;