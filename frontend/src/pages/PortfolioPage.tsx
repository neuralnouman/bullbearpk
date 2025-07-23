import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Portfolio } from '../types';
import MainLayout from '../components/MainLayout';
import PortfolioSummary from '../components/PortfolioSummary';
import PortfolioCharts from '../components/PortfolioCharts';
import BuyStockForm, { BuyStockFormData } from '../components/BuyStockForm';
import SellStockForm, { SellStockFormData } from '../components/SellStockForm';
import { getUserPortfolio, buyStock, sellStock, updatePortfolioValue } from '../services/portfolioService';
import { Plus, Minus, RefreshCw } from 'lucide-react';

const PortfolioPage: React.FC = () => {
  const { user } = useAuthStore();
  const location = useLocation();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showBuyForm, setShowBuyForm] = useState(false);
  const [showSellForm, setShowSellForm] = useState(false);
  const [transactionSuccess, setTransactionSuccess] = useState<string | null>(null);

  // Check if we were redirected with a stock to buy
  const buyStockFromRedirect = location.state?.buyStock;

  useEffect(() => {
    if (buyStockFromRedirect) {
      setShowBuyForm(true);
    }
    
    fetchPortfolio();
  }, [buyStockFromRedirect]);

  const fetchPortfolio = async (forceRefresh: boolean = false) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getUserPortfolio(user?.id || 'anonymous', forceRefresh);
      setPortfolio(data);
    } catch (err: any) {
      console.error('Error fetching portfolio:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load portfolio data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBuyStock = async (formData: BuyStockFormData) => {
    setLoading(true);
    setError(null);
    setTransactionSuccess(null);
    
    try {
      const result = await buyStock({
        userId: user?.id || 'anonymous',
        stockSymbol: formData.company,
        amount: formData.amount
      });
      
      if (result.success) {
        setTransactionSuccess(`Successfully purchased ${formData.company} stock!`);
        setShowBuyForm(false);
        fetchPortfolio(true); // Force refresh after buying
      } else {
        // Handle error from buyStock function
        setError(result.message || 'Failed to complete purchase. Please try again.');
      }
    } catch (err: any) {
      console.error('Error buying stock:', err);
      setError(err.response?.data?.message || err.message || 'Failed to complete purchase. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSellStock = async (formData: SellStockFormData) => {
    setLoading(true);
    setError(null);
    setTransactionSuccess(null);
    
    try {
      const result = await sellStock({
        userId: user?.id || 'anonymous',
        investmentId: formData.investmentId,
        quantity: formData.quantity
      });
      
      if (result.success) {
        setTransactionSuccess('Successfully sold stock!');
        setShowSellForm(false);
        fetchPortfolio(true); // Force refresh after selling
      } else {
        // Handle error from sellStock function
        setError(result.message || 'Failed to complete sale. Please try again.');
      }
    } catch (err: any) {
      console.error('Error selling stock:', err);
      setError(err.response?.data?.message || err.message || 'Failed to complete sale. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTotalValue = async (newValue: number) => {
    setLoading(true);
    setError(null);
    setTransactionSuccess(null);
    
    try {
      console.log(`Updating total value to ${newValue}`);
      
      // Update the portfolio in the backend
      const result = await updatePortfolioValue(user?.id || 'anonymous', newValue);
      
      if (result.success) {
        setTransactionSuccess('Portfolio value updated successfully!');
        // Refetch the portfolio to get updated values
        await fetchPortfolio(true);
      } else {
        setError(result.message || 'Failed to update portfolio value. Please try again.');
      }
    } catch (error: any) {
      console.error('Error updating total value:', error);
      setError(error.message || 'Failed to update portfolio value. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !portfolio) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 flex justify-center items-center h-64">
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-500">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Your Portfolio</h1>
        
        <div className="flex space-x-2">
          <button 
            onClick={() => setShowBuyForm(true)}
            className="btn-primary flex items-center"
          >
            <Plus size={16} className="mr-1" />
            Buy Stock
          </button>
          
          <button 
            onClick={() => setShowSellForm(true)}
            className="btn-secondary flex items-center"
            disabled={!portfolio?.investments.length}
          >
            <Minus size={16} className="mr-1" />
            Sell Stock
          </button>
          
          <button 
            onClick={() => fetchPortfolio(true)} // Force refresh when clicking refresh button
            className="btn-outline flex items-center"
            disabled={loading}
          >
            <RefreshCw size={16} className={`mr-1 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}
      
      {transactionSuccess && (
        <div className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 p-4 rounded-lg mb-6">
          {transactionSuccess}
        </div>
      )}
      
      {portfolio ? (
        <>
          <PortfolioSummary 
            portfolio={portfolio} 
            onUpdateTotalValue={handleUpdateTotalValue}
          />
          
          <div className="mt-8">
            <h2 className="text-xl font-bold mb-4">Portfolio Analysis</h2>
            <PortfolioCharts portfolio={portfolio} />
          </div>
        </>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
          <h3 className="text-lg font-medium mb-2">No Portfolio Data</h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            You don't have any investments yet. Start by buying some stocks!
          </p>
          <button 
            onClick={() => setShowBuyForm(true)}
            className="btn-primary"
          >
            Buy Your First Stock
          </button>
        </div>
      )}
      
      {/* Buy Stock Modal */}
      {showBuyForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Buy Stock</h2>
            <BuyStockForm 
              onSubmit={handleBuyStock}
              availableFunds={portfolio?.cashBalance || portfolio?.totalValue || 10000}
            />
            <button 
              onClick={() => setShowBuyForm(false)}
              className="mt-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
      
      {/* Sell Stock Modal */}
      {showSellForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Sell Stock</h2>
            {portfolio?.investments.length ? (
              <SellStockForm 
                onSubmit={handleSellStock}
                userInvestments={portfolio.investments}
              />
            ) : (
              <p className="text-gray-500 dark:text-gray-400">
                You don't have any investments to sell.
              </p>
            )}
            <button 
              onClick={() => setShowSellForm(false)}
              className="mt-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
    </MainLayout>
  );
};

export default PortfolioPage;