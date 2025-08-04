import React, { useState } from 'react';
import { AgenticRecommendation } from '../types';
import { 
  buyStockFromRecommendation, 
  sellStock, 
  holdStock, 
  markStockAsPending,
  DecisionResponse 
} from '../services/investmentService';
import { useAuthStore } from '../store/authStore';
import { toast } from 'react-hot-toast';
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  DollarSign, 
  BarChart3,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface InvestmentDecisionCardProps {
  recommendation: AgenticRecommendation;
  onDecisionComplete?: (result: DecisionResponse) => void;
  onRefresh?: () => void;
}

const InvestmentDecisionCard: React.FC<InvestmentDecisionCardProps> = ({
  recommendation,
  onDecisionComplete,
  onRefresh
}) => {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [decisionMade, setDecisionMade] = useState(false);

  const handleDecision = async (decisionType: 'buy' | 'sell' | 'hold' | 'pending') => {
    if (!user?.id) {
      toast.error('Please log in to make investment decisions');
      return;
    }

    setLoading(true);
    try {
      let result: DecisionResponse;

      switch (decisionType) {
        case 'buy':
          result = await buyStockFromRecommendation(
            user.id,
            recommendation.stock_code,
            Math.floor(recommendation.allocation_percent * 100), // Convert to quantity
            recommendation.technical_analysis.current_price,
            recommendation.recommendation_type === 'buy' ? 'rec_' + Date.now() : undefined
          );
          break;
        case 'sell':
          result = await sellStock(
            user.id,
            recommendation.stock_code,
            Math.floor(recommendation.allocation_percent * 100),
            recommendation.technical_analysis.current_price
          );
          break;
        case 'hold':
          result = await holdStock(user.id, recommendation.stock_code);
          break;
        case 'pending':
          result = await markStockAsPending(
            user.id,
            recommendation.stock_code,
            'rec_' + Date.now()
          );
          break;
        default:
          throw new Error('Invalid decision type');
      }

      if (result.success) {
        toast.success(result.message || 'Decision processed successfully!');
        setDecisionMade(true);
        onDecisionComplete?.(result);
        onRefresh?.();
      } else {
        toast.error(result.message || 'Failed to process decision');
      }
    } catch (error: any) {
      console.error('Error processing decision:', error);
      toast.error(error.message || 'Failed to process decision');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'buy':
        return <TrendingUp className="w-5 h-5 text-green-600" />;
      case 'sell':
        return <TrendingDown className="w-5 h-5 text-red-600" />;
      case 'hold':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      default:
        return <BarChart3 className="w-5 h-5 text-blue-600" />;
    }
  };

  const getRecommendationColor = (type: string) => {
    switch (type) {
      case 'buy':
        return 'bg-green-50 border-green-200';
      case 'sell':
        return 'bg-red-50 border-red-200';
      case 'hold':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  if (decisionMade) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span className="text-green-800 font-medium">
            Decision processed for {recommendation.stock_code}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={`border rounded-lg p-4 ${getRecommendationColor(recommendation.recommendation_type)}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getRecommendationIcon(recommendation.recommendation_type)}
          <div>
            <h3 className="font-semibold text-lg">{recommendation.stock_code}</h3>
            <p className="text-sm text-gray-600">{recommendation.stock_name}</p>
          </div>
        </div>
        <div className="text-right">
          <div className={`font-bold ${getConfidenceColor(recommendation.confidence_score)}`}>
            {recommendation.confidence_score}%
          </div>
          <div className="text-xs text-gray-500">Confidence</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-sm text-gray-600">Current Price</div>
          <div className="font-semibold">₨{recommendation.technical_analysis.current_price}</div>
        </div>
        <div>
          <div className="text-sm text-gray-600">Expected Return</div>
          <div className="font-semibold text-green-600">
            +{recommendation.expected_return}%
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-600">Risk Level</div>
          <div className="font-semibold">{recommendation.risk_level}</div>
        </div>
        <div>
          <div className="text-sm text-gray-600">Allocation</div>
          <div className="font-semibold">{recommendation.allocation_percent}%</div>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-2">Reasoning</div>
        <p className="text-sm text-gray-700">{recommendation.reasoning}</p>
      </div>

      <div className="flex space-x-2">
        {recommendation.recommendation_type === 'buy' && (
          <button
            onClick={() => handleDecision('buy')}
            disabled={loading}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            {loading ? 'Processing...' : 'Buy'}
          </button>
        )}
        
        {recommendation.recommendation_type === 'sell' && (
          <button
            onClick={() => handleDecision('sell')}
            disabled={loading}
            className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            {loading ? 'Processing...' : 'Sell'}
          </button>
        )}

        <button
          onClick={() => handleDecision('hold')}
          disabled={loading}
          className="flex-1 bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
        >
          {loading ? 'Processing...' : 'Hold'}
        </button>

        <button
          onClick={() => handleDecision('pending')}
          disabled={loading}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
        >
          {loading ? 'Processing...' : 'Pending'}
        </button>
      </div>

      {recommendation.technical_analysis && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600 mb-2">Technical Analysis</div>
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div>
              <span className="text-gray-500">RSI:</span>
              <span className="ml-1 font-medium">{recommendation.technical_analysis.rsi.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-gray-500">Trend:</span>
              <span className="ml-1 font-medium">{recommendation.technical_analysis.price_trend}</span>
            </div>
            <div>
              <span className="text-gray-500">Momentum:</span>
              <span className="ml-1 font-medium">{recommendation.technical_analysis.momentum.toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvestmentDecisionCard; 