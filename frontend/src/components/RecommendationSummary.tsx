import React from 'react';
import { TrendingUp, AlertTriangle, Info, CheckCircle, Clock } from 'lucide-react';

interface AgenticRecommendation {
  stock_code: string;
  stock_name: string;
  sector: string;
  recommendation_type: 'buy' | 'hold' | 'sell';
  confidence_score: number;
  technical_analysis: Record<string, unknown>;
  news_sentiment: Record<string, unknown>;
  reasoning: string;
  risk_level: string;
  expected_return: number;
  allocation_percent: number;
}

interface RecommendationSummaryProps {
  recommendations: AgenticRecommendation[];
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

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'buy':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'hold':
        return <Clock size={16} className="text-yellow-500" />;
      case 'sell':
        return <AlertTriangle size={16} className="text-red-500" />;
      default:
        return <Info size={16} className="text-blue-500" />;
    }
  };

  const getRecommendationColor = (type: string) => {
    switch (type) {
      case 'buy':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'hold':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'sell':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">AI Investment Recommendations</h3>
          <TrendingUp size={18} className="text-blue-500" />
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Based on technical analysis, news sentiment, and risk assessment
        </p>
      </div>
      
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {recommendations.map((rec, index) => (
          <div key={index} className="p-4">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  {getRecommendationIcon(rec.recommendation_type)}
                  <h4 className="font-medium text-lg">{rec.stock_code}</h4>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRecommendationColor(rec.recommendation_type)}`}>
                    {rec.recommendation_type.toUpperCase()}
                  </span>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                  {rec.stock_name} • {rec.sector}
                </p>
                
                <p className="text-gray-700 dark:text-gray-300 text-sm mb-3">
                  {rec.reasoning}
                </p>
                
                <div className="flex flex-wrap gap-2 mb-3">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(rec.risk_level)}`}>
                    <AlertTriangle size={12} className="mr-1" />
                    {rec.risk_level} Risk
                  </span>
                  
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                    <TrendingUp size={12} className="mr-1" />
                    {(rec.expected_return || 0).toFixed(1)}% Expected Return
                  </span>
                  
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300">
                    Confidence: {((rec.confidence_score || 0) * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  <p>Suggested allocation: <span className="font-medium">{(rec.allocation_percent || 0).toFixed(1)}%</span></p>
                  {rec.technical_analysis && (
                    <p className="mt-1">
                      Technical: <span className="font-medium">{rec.technical_analysis.price_trend}</span>
                    </p>
                  )}
                </div>
              </div>
              
              {onBuyClick && rec.recommendation_type === 'buy' && (
                <button 
                  onClick={() => onBuyClick(rec.stock_code)}
                  className="btn-primary text-sm ml-4"
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