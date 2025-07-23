import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import MainLayout from '../components/MainLayout';
import InvestmentForm, { InvestmentFormData } from '../components/InvestmentForm';
import RecommendationSummary from '../components/RecommendationSummary';
import { submitInvestmentForm, submitFeedback } from '../services/investmentService';

const InvestmentFormPage: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [savedFormData, setSavedFormData] = useState<InvestmentFormData | null>(null);

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
      const result = await submitInvestmentForm(formData, user?.id || 'anonymous', refresh);
      
      if (result.error) {
        setError(result.error);
        return;
      }
      
      setRecommendations(result.recommendations || []);
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

  const handleBuyClick = (company: string) => {
    navigate('/portfolio', { state: { buyStock: company } });
  };

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto px-4 py-8">
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
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 flex justify-center items-center h-64">
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="mt-4 text-gray-500">Generating recommendations...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-4 rounded-lg">
              {error}
            </div>
          ) : (
            <RecommendationSummary 
              recommendations={recommendations} 
              onBuyClick={handleBuyClick}
            />
          )}
          
          {recommendations.length > 0 && (
            <div className="mt-4 bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-medium">What do you think of these recommendations?</h3>
                <button 
                  className="btn-secondary flex items-center text-sm"
                  onClick={() => savedFormData && fetchRecommendations(savedFormData, true)}
                  disabled={loading}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh Data
                </button>
              </div>
              <div className="flex space-x-2">
                <button 
                  className="btn-primary"
                  onClick={() => {
                    setLoading(true);
                    // Store feedback using the submitFeedback service
                    submitFeedback(user?.id || 'anonymous', 'positive', recommendations)
                      .then(() => {
                        console.log('Positive feedback submitted');
                        // Show a success message
                        alert('Thank you for your feedback!');
                      })
                      .catch(err => {
                        console.error('Error submitting feedback:', err);
                        // Show an error message
                        setError('Failed to submit feedback. Please try again.');
                      })
                      .finally(() => setLoading(false));
                  }}
                >
                  Helpful
                </button>
                <button 
                  className="btn-secondary"
                  onClick={() => {
                    setLoading(true);
                    // Store feedback using the submitFeedback service
                    submitFeedback(user?.id || 'anonymous', 'negative', recommendations)
                      .then(() => {
                        console.log('Negative feedback submitted');
                        // Show a success message
                        alert('Thank you for your feedback!');
                      })
                      .catch(err => {
                        console.error('Error submitting feedback:', err);
                        // Show an error message
                        setError('Failed to submit feedback. Please try again.');
                      })
                      .finally(() => setLoading(false));
                  }}
                >
                  Not Helpful
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
    </MainLayout>
  );
};

export default InvestmentFormPage;