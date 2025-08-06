import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MainLayout from '../components/MainLayout';
import MarketData from '../components/MarketData';
import { 
  RefreshCw, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getMarketStatus } from '../services/agenticService';
import { getMarketData } from '../services/marketService';

interface MarketStatus {
  isOpen: boolean;
  lastUpdated: string;
  nextUpdate: string;
  marketHours: string;
}

// Mock market indices data since it's not available in the API
const mockMarketIndices = [
  { name: 'KSE-100', value: 45000, change: 150, changePercent: 0.33, trend: 'up' },
  { name: 'KSE-30', value: 18000, change: 75, changePercent: 0.42, trend: 'up' },
  { name: 'KMI-30', value: 22000, change: -50, changePercent: -0.23, trend: 'down' },
  { name: 'All Share', value: 32000, change: 100, changePercent: 0.31, trend: 'up' }
];

const MarketDataPage: React.FC = () => {
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMarketData();
    fetchMarketStatus();
  }, []);

  const fetchMarketData = async (silent: boolean = false) => {
    if (!silent) setLoading(true);
    setError(null);

    try {
      await getMarketData();
      
      if (!silent) {
        toast.success('Market data updated successfully!');
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch market data';
      console.error('Error fetching market data:', err);
      setError(errorMessage);
      if (!silent) {
        toast.error('Failed to fetch market data');
      }
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const fetchMarketStatus = async () => {
    try {
      const response = await getMarketStatus();
      if (response.success) {
        setMarketStatus({
          isOpen: response.isOpen,
          lastUpdated: response.lastUpdated,
          nextUpdate: response.nextUpdate,
          marketHours: response.marketHours
        });
      } else {
        throw new Error(response.message || 'Failed to fetch market status');
      }
    } catch (err) {
      console.error('Error fetching market status:', err);
      // Set default status
      setMarketStatus({
        isOpen: true,
        lastUpdated: new Date().toISOString(),
        nextUpdate: new Date(Date.now() + 5 * 60 * 1000).toISOString(),
        marketHours: '09:15 - 15:30'
      });
    }
  };







  const getTrendIcon = (trend: string) => {
    return trend === 'up' ? <TrendingUp className="w-4 h-4 text-green-600" /> : <TrendingDown className="w-4 h-4 text-red-600" />;
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
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Market Data
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Real-time Pakistan Stock Exchange data and market insights
              </p>
            </div>
            
            
          </div>

          
        </motion.div>

        {/* Market Indices */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {mockMarketIndices.map((index, idx) => (
            <motion.div
              key={index.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              whileHover={{ scale: 1.02 }}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-lg"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{index.name}</h3>
                {getTrendIcon(index.trend)}
              </div>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {index.value.toLocaleString()}
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {index.change >= 0 ? '+' : ''}{index.change}
                  </span>
                  <span className={`text-sm ${index.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ({index.changePercent >= 0 ? '+' : ''}{index.changePercent}%)
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6"
          >
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <span className="text-red-800 dark:text-red-200">{error}</span>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center py-12"
          >
            <div className="text-center">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Loading market data...</p>
            </div>
          </motion.div>
        )}

        {/* Market Data Component */}
        {!loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <MarketData />
          </motion.div>
        )}



        
      </div>
    </MainLayout>
  );
};

export default MarketDataPage;