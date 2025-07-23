import React from 'react';
import { TrendingUp, AlertTriangle, Info } from 'lucide-react';

interface Recommendation {
  company: string;
  recommendation_reason: string;
  risk: string;
  expected_return: string;
  allocation_suggestion: string;
}

interface RecommendationSummaryProps {
  recommendations: Recommendation[];
  onBuyClick?: (company: string) => void;
}

const RecommendationSummary: React.FC<RecommendationSummaryProps> = ({ 
  recommendations, 
  onBuyClick 
}) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
        <Info size={24} className="mx-auto mb-2 text-blue-500" />
        <h3 className="text-lg font-medium mb-2">No Recommendations Available</h3>
        <p className="text-gray-500 dark:text-gray-400">
          Complete your investment profile to get personalized recommendations.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">Investment Recommendations</h3>
          <TrendingUp size={18} className="text-blue-500" />
        </div>
      </div>
      
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {recommendations.map((rec, index) => (
          <div key={index} className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-medium text-lg">{rec.company}</h4>
                <p className="text-gray-600 dark:text-gray-400 mt-1">{rec.recommendation_reason}</p>
                
                <div className="mt-2 flex flex-wrap gap-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    rec.risk === 'High' 
                      ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                      : rec.risk === 'Medium'
                      ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                      : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                  }`}>
                    <AlertTriangle size={12} className="mr-1" />
                    {rec.risk} Risk
                  </span>
                  
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                    <TrendingUp size={12} className="mr-1" />
                    {rec.expected_return}
                  </span>
                </div>
                
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  Suggested allocation: <span className="font-medium">{rec.allocation_suggestion}</span>
                </p>
              </div>
              
              {onBuyClick && (
                <button 
                  onClick={() => onBuyClick(rec.company.split(' - ')[0])}
                  className="btn-primary text-sm"
                >
                  Buy
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationSummary;