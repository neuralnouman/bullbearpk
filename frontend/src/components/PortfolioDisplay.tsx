import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Wallet, 
  Target, 
  Eye,
  ArrowUpRight,
  ArrowDownRight,
  Info,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { Portfolio, PortfolioMetrics } from '../types';
import { formatCurrency, formatPercentage, getValueColor } from '../utils';
import { generateUniqueKey } from '../utils/portfolioUtils';

interface PortfolioDisplayProps {
  portfolio: Portfolio | null;
  loading: boolean;
  error: string | null;
  onRefresh?: () => void;
  metrics?: PortfolioMetrics | null;
}

// PortfolioMetrics interface is now imported from types

const PortfolioDisplay: React.FC<PortfolioDisplayProps> = ({
  portfolio,
  loading,
  error,
  onRefresh,
  metrics
}) => {

  
  // Always calculate metrics from the latest portfolio data to ensure we have the most up-to-date values
  const displayMetrics = (() => {
    if (!portfolio) {
      return {
        totalInvested: 0,
        totalReturns: 0,
        returnPercentage: 0,
        cashBalance: 0,
        totalHoldings: 0,
        activeInvestments: 0,
        totalValue: 0
      };
    }

    const activeInvestments = portfolio.investments.filter(inv => inv.status === 'active');
    const totalInvested = activeInvestments.reduce((sum, inv) => sum + (inv.quantity * inv.purchasePrice), 0);
    const totalValue = portfolio.totalValue || 0; // Use the totalValue from portfolio which includes cash balance
    const totalReturns = totalValue - totalInvested;
    const returnPercentage = totalInvested > 0 ? (totalReturns / totalInvested) * 100 : 0;

    return {
      totalInvested,
      totalReturns,
      returnPercentage,
      cashBalance: portfolio.cashBalance || 0,
      totalHoldings: activeInvestments.length,
      activeInvestments: activeInvestments.length,
      totalValue
    };
  })();

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-20 h-20 border-4 border-t-blue-500 border-r-transparent border-b-blue-500 border-l-transparent rounded-full animate-spin mb-4"></div>
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300">Loading Portfolio</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-2">Retrieving your investments...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-20 h-20 flex items-center justify-center rounded-full bg-red-100 dark:bg-red-900/20 mb-4">
          <AlertCircle className="w-10 h-10 text-red-600 dark:text-red-400" />
        </div>
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300">Error Loading Portfolio</h2>
        <p className="text-red-500 dark:text-red-400 mt-2">{error}</p>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="mt-6 px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center"
          >
            <Eye className="w-4 h-4 mr-2" />
            Try Again
          </button>
        )}
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-20 h-20 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
          <Target className="w-10 h-10 text-gray-400" />
        </div>
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300">No Portfolio Data</h2>
        <p className="text-gray-500 dark:text-gray-400 mt-2">Start investing to see your portfolio here</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Portfolio Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Cash Balance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Cash Balance</p>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {formatCurrency(displayMetrics.cashBalance)}
              </h3>
            </div>
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-md">
              <Wallet className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
          </div>
          
          <div className="mt-4 flex items-center">
            <div className="text-gray-600 dark:text-gray-400 text-sm flex items-center">
              <Info className="w-4 h-4 mr-1" />
              <span>Available for trading</span>
            </div>
          </div>
        </motion.div>
        
        {/* Total Invested */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Total Invested</p>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {formatCurrency(displayMetrics.totalInvested)}
              </h3>
            </div>
            <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-md">
              <Target className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
          
          <div className="mt-4 flex items-center">
            <div className="text-gray-600 dark:text-gray-400 text-sm flex items-center">
              <Eye className="w-4 h-4 mr-1" />
                              <span>{displayMetrics.activeInvestments} active positions</span>
            </div>
          </div>
        </motion.div>
        
        {/* Total Returns */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
        >
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Total Returns</p>
              <h3 className={`text-2xl font-bold ${getValueColor(displayMetrics.totalReturns)}`}>
                {formatCurrency(displayMetrics.totalReturns)}
              </h3>
            </div>
            <div className={`p-2 ${displayMetrics.totalReturns >= 0 ? 'bg-green-100 dark:bg-red-900/20' : 'bg-red-100 dark:bg-red-900/20'} rounded-md`}>
              {displayMetrics.totalReturns >= 0 ? (
                <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-600 dark:text-red-400" />
              )}
            </div>
          </div>
          
          <div className="mt-4 flex items-center">
            <div className={`flex items-center ${getValueColor(displayMetrics.returnPercentage)}`}>
              {displayMetrics.returnPercentage >= 0 ? (
                <ArrowUpRight className="w-4 h-4 mr-1" />
              ) : (
                <ArrowDownRight className="w-4 h-4 mr-1" />
              )}
              <span className="font-medium">{formatPercentage(displayMetrics.returnPercentage)}</span>
            </div>
            <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">Return rate</span>
          </div>
        </motion.div>
      </div>





      {/* Empty State */}
      {portfolio.investments.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center py-12"
        >
          <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
            <Target className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            No Investments Yet
          </h3>
          <p className="text-gray-500 dark:text-gray-400 text-center max-w-md">
            Start building your portfolio by purchasing your first stocks. 
            Your investment journey begins here!
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default PortfolioDisplay; 