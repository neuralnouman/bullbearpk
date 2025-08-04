import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Portfolio } from '../types';
import MainLayout from '../components/MainLayout';
import PortfolioSummary from '../components/PortfolioSummary';
import PortfolioCharts from '../components/PortfolioCharts';
import { 
  getUserPortfolio, 
  initializeUser, 
  getPortfolioPerformance,
  getInvestmentHistory,
  getPortfolioHoldings,
  getSectorAllocation,
  getTopHoldings
} from '../services/portfolioService';
import { 
  buyStockFromRecommendation,
  sellStock,
  holdStock,
  markStockAsPending,
  DecisionResponse
} from '../services/investmentService';
import { Plus, Minus, RefreshCw, TrendingUp, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

const PortfolioPage: React.FC = () => {
  const { user } = useAuthStore();
  const location = useLocation();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [performance, setPerformance] = useState<any>(null);
  const [holdings, setHoldings] = useState<any[]>([]);
  const [sectorAllocation, setSectorAllocation] = useState<any[]>([]);
  const [topHoldings, setTopHoldings] = useState<any[]>([]);

  // Check if we were redirected with a stock to buy
  const buyStockFromRedirect = location.state?.buyStock;

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Initialize user if needed
      if (user?.id) {
        await initializeUser({
          user_id: user.id,
          name: user.name,
          email: user.email,
          risk_tolerance: 'moderate',
          investment_goal: 'growth',
          initial_cash: 10000
        });
      }

      const data = await getUserPortfolio(user?.id || 'anonymous');
      setPortfolio(data);

      // Fetch additional portfolio data
      try {
        const [performanceData, holdingsData, sectorData, topHoldingsData] = await Promise.all([
          getPortfolioPerformance(user?.id || 'anonymous'),
          getPortfolioHoldings(user?.id || 'anonymous'),
          getSectorAllocation(user?.id || 'anonymous'),
          getTopHoldings(user?.id || 'anonymous')
        ]);

        setPerformance(performanceData);
        setHoldings(holdingsData);
        setSectorAllocation(sectorData);
        setTopHoldings(topHoldingsData);
      } catch (err) {
        console.warn('Some portfolio data could not be loaded:', err);
      }
    } catch (err: any) {
      console.error('Error fetching portfolio:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load portfolio data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBuyStock = async (stockCode: string, quantity: number, price: number) => {
    if (!user?.id) {
      toast.error('Please log in to make investment decisions');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await buyStockFromRecommendation(user.id, stockCode, quantity, price);
      
      if (result.success) {
        toast.success(result.message || 'Stock purchased successfully!');
        fetchPortfolio(); // Refresh portfolio data
      } else {
        toast.error(result.message || 'Failed to complete purchase. Please try again.');
      }
    } catch (err: any) {
      console.error('Error buying stock:', err);
      toast.error(err.message || 'Failed to complete purchase. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSellStock = async (stockCode: string, quantity: number, price: number) => {
    if (!user?.id) {
      toast.error('Please log in to make investment decisions');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await sellStock(user.id, stockCode, quantity, price);
      
      if (result.success) {
        toast.success(result.message || 'Stock sold successfully!');
        fetchPortfolio(); // Refresh portfolio data
      } else {
        toast.error(result.message || 'Failed to complete sale. Please try again.');
      }
    } catch (err: any) {
      console.error('Error selling stock:', err);
      toast.error(err.message || 'Failed to complete sale. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleHoldStock = async (stockCode: string) => {
    if (!user?.id) {
      toast.error('Please log in to make investment decisions');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await holdStock(user.id, stockCode);
      
      if (result.success) {
        toast.success(result.message || 'Stock marked as hold!');
        fetchPortfolio(); // Refresh portfolio data
      } else {
        toast.error(result.message || 'Failed to update stock status. Please try again.');
      }
    } catch (err: any) {
      console.error('Error holding stock:', err);
      toast.error(err.message || 'Failed to update stock status. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePendingStock = async (stockCode: string) => {
    if (!user?.id) {
      toast.error('Please log in to make investment decisions');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await markStockAsPending(user.id, stockCode);
      
      if (result.success) {
        toast.success(result.message || 'Stock marked as pending!');
        fetchPortfolio(); // Refresh portfolio data
      } else {
        toast.error(result.message || 'Failed to update stock status. Please try again.');
      }
    } catch (err: any) {
      console.error('Error marking stock as pending:', err);
      toast.error(err.message || 'Failed to update stock status. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-semibold mb-2">Loading Portfolio</h3>
            <p className="text-gray-600">Fetching your investment data...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center space-x-2 mb-4">
              <AlertCircle className="w-6 h-6 text-red-600" />
              <h3 className="text-lg font-semibold text-red-600">Error</h3>
            </div>
            <p className="text-gray-700 mb-4">{error}</p>
            <button
              onClick={fetchPortfolio}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
            >
              Try Again
            </button>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Portfolio</h1>
              <p className="text-gray-600 dark:text-gray-400">
                Track your investments and performance
              </p>
            </div>
            <button
              onClick={fetchPortfolio}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {portfolio ? (
          <div className="space-y-8">
            {/* Portfolio Summary */}
            <PortfolioSummary portfolio={portfolio} />

            {/* Portfolio Charts */}
            <PortfolioCharts 
              portfolio={portfolio}
            />

            {/* Investment Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <button
                  onClick={() => {/* Navigate to investment form */}}
                  className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg flex items-center justify-center space-x-2"
                >
                  <Plus className="w-5 h-5" />
                  <span>Buy Stock</span>
                </button>
                <button
                  onClick={() => {/* Navigate to sell form */}}
                  className="bg-red-600 hover:bg-red-700 text-white p-4 rounded-lg flex items-center justify-center space-x-2"
                >
                  <Minus className="w-5 h-5" />
                  <span>Sell Stock</span>
                </button>
                <button
                  onClick={() => {/* Navigate to analysis */}}
                  className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg flex items-center justify-center space-x-2"
                >
                  <TrendingUp className="w-5 h-5" />
                  <span>Get Analysis</span>
                </button>
                <button
                  onClick={() => {/* Navigate to recommendations */}}
                  className="bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-lg flex items-center justify-center space-x-2"
                >
                  <AlertCircle className="w-5 h-5" />
                  <span>Recommendations</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Portfolio Found</h3>
            <p className="text-gray-600 mb-4">
              Start by creating your investment profile and getting recommendations
            </p>
            <button
              onClick={() => {/* Navigate to investment form */}}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md"
            >
              Get Started
            </button>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default PortfolioPage;