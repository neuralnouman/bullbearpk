import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '../store/authStore';
import { Portfolio, Investment, StockData, PortfolioMetrics } from '../types';
import MainLayout from '../components/MainLayout';
import PortfolioDisplay from '../components/PortfolioDisplay';
import { 
  PortfolioPerformanceChart, 
  SectorAllocationChart, 
  InvestmentPerformanceChart, 
  PortfolioMetricsChart 
} from '../components/charts';

import { 
  Plus, 
  RefreshCw, 
  Search,
  SortAsc,
  SortDesc,
  X,
  Target,
  PlusCircle,
  MinusCircle
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { 
  getUserPortfolio, 
  addInvestment,
  addCashToPortfolio
} from '../services/portfolioService';
import { marketService } from '../services/marketService';

import { formatCurrency, formatPercentage, getValueColor } from '../utils';
import { generateUniqueKey } from '../utils/portfolioUtils';

// PortfolioMetrics interface is now imported from types

interface InvestmentTableData extends Investment {
  currentValue: number;
  gainLoss: number;
  gainLossPercent: number;
  isPositive: boolean;
}

interface TransactionModal {
  isOpen: boolean;
  type: 'buy' | 'sell' | 'add_cash' | null;
  stock: StockData | null;
  investment: InvestmentTableData | null;
}

interface TransactionForm {
  quantity: number;
  price: number;
  total: number;
  cashAmount?: number;
}

interface AddCashModal {
  isOpen: boolean;
  amount: number;
}

// These interfaces are now imported from types

const EnhancedPortfolioPage: React.FC = () => {
  const { user } = useAuthStore();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [metrics, setMetrics] = useState<PortfolioMetrics | null>({
    totalInvested: 0,
    totalReturns: 0,
    returnPercentage: 0,
    cashBalance: 0,
    totalHoldings: 0,
    activeInvestments: 0,
    totalValue: 0
  });
  const [investments, setInvestments] = useState<InvestmentTableData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortConfig, setSortConfig] = useState<{
    key: keyof InvestmentTableData;
    direction: 'asc' | 'desc';
  }>({ key: 'stockSymbol', direction: 'asc' });
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal and transaction states
  const [transactionModal, setTransactionModal] = useState<TransactionModal>({
    isOpen: false,
    type: null,
    stock: null,
    investment: null
  });
  const [transactionForm, setTransactionForm] = useState<TransactionForm>({
    quantity: 0,
    price: 0,
    total: 0
  });
  const [addCashModal, setAddCashModal] = useState<AddCashModal>({
    isOpen: false,
    amount: 0
  });
  const [availableStocks, setAvailableStocks] = useState<StockData[]>([]);
  const [selectedStock, setSelectedStock] = useState<StockData | null>(null);

  // Fetch portfolio data on component mount
  useEffect(() => {
    if (user?.id) {
      fetchPortfolioData();
      fetchAvailableStocks();
    }
  }, [user?.id]);



  const fetchPortfolioData = async () => {
    if (!user?.id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Fetch the actual portfolio data - backend handles user creation automatically
      const portfolioResponse = await getUserPortfolio(user.id);
      
      if (!portfolioResponse.success) {
        throw new Error(portfolioResponse.message || 'Failed to fetch portfolio data');
      }

      // Extract data from the backend response
      const portfolioSummary = portfolioResponse.portfolio_summary || {};
      const investmentsData = portfolioResponse.investments || [];
      const allocationData = portfolioResponse.allocation || [];

      // Map backend response to frontend Portfolio structure
      // Backend totalValue already includes cash balance
      const portfolioData: Portfolio = {
        totalValue: portfolioSummary.totalValue || 0,
        totalInvested: portfolioSummary.totalInvested || 0,
        totalReturns: portfolioSummary.totalReturns || 0,
        returnPercentage: portfolioSummary.returnPercentage || 0,
        cashBalance: portfolioSummary.cashBalance || 0,
        investments: investmentsData,
        allocation: allocationData
      };

      setPortfolio(portfolioData);

      // Calculate metrics from portfolio data
      const calculatedMetrics = calculatePortfolioMetrics(portfolioData);
      setMetrics(calculatedMetrics);

      // Process investments for table display
      const processedInvestments = processInvestmentsForTable(investmentsData);
      setInvestments(processedInvestments);

      console.log('Portfolio data loaded:', {
        portfolio: portfolioData,
        metrics: calculatedMetrics,
        investments: processedInvestments
      });


    } catch (err: any) {
      console.error('Error fetching portfolio:', err);
      setError(err.response?.data?.message || err.message || 'Failed to load portfolio data.');
      toast.error('Failed to load portfolio data');
    } finally {
      setLoading(false);
    }
  };

  // Function to fetch available stocks for trading
  const fetchAvailableStocks = async () => {
    try {
      const stocks = await marketService.getAllStocks();
      setAvailableStocks(stocks);
    } catch (err: any) {
      console.error('Error fetching stocks:', err);
      toast.error('Failed to load available stocks');
    }
  };

  // Calculate portfolio metrics from raw portfolio data
  const calculatePortfolioMetrics = (portfolioData: Portfolio): PortfolioMetrics => {
    // Filter out invalid investments and ensure safe calculations
    const validInvestments = (portfolioData.investments || []).filter(inv => 
      inv && typeof inv === 'object' && 
      typeof inv.purchasePrice === 'number' && 
      typeof inv.currentPrice === 'number' && 
      typeof inv.quantity === 'number'
    );

    const totalInvested = validInvestments.reduce(
      (sum, inv) => sum + ((inv.purchasePrice || 0) * (inv.quantity || 0)), 
      0
    );

    // Use the totalValue from portfolioData which already includes cash balance
    const totalValue = portfolioData.totalValue || 0;

    const totalReturns = totalValue - totalInvested;
    const returnPercentage = totalInvested > 0 ? (totalReturns / totalInvested) * 100 : 0;

    return {
      totalInvested,
      totalReturns,
      returnPercentage,
      cashBalance: portfolioData.cashBalance || 0,
      totalHoldings: validInvestments.length,
      activeInvestments: validInvestments.filter(inv => (inv.quantity || 0) > 0).length,
      totalValue
    };
  };

  // Process investments for table display with current market data
  const processInvestmentsForTable = (investments: Investment[]): InvestmentTableData[] => {
    return investments
      .filter(investment => investment && typeof investment === 'object')
      .map(investment => {
        // Map backend investment structure to frontend structure
        const safeInvestment = {
          id: investment.id || '',
          userId: investment.userId || investment.user_id || '',
          stockSymbol: investment.stockSymbol || investment.stock_code || '',
          companyName: investment.companyName || investment.stock_name || '',
          quantity: investment.currentQuantity || investment.current_quantity || investment.quantity || 0,
          purchasePrice: investment.buyPrice || investment.buy_price || investment.purchasePrice || 0,
          currentPrice: investment.currentPrice || investment.current_price || 0,
          purchaseDate: investment.purchaseDate || investment.buy_date || new Date().toISOString(),
          sector: investment.sector || '',
          status: investment.status || 'active'
        };

        const currentValue = safeInvestment.currentPrice * safeInvestment.quantity;
        const investedValue = safeInvestment.purchasePrice * safeInvestment.quantity;
        const gainLoss = currentValue - investedValue;
        const gainLossPercent = investedValue > 0 ? (gainLoss / investedValue) * 100 : 0;

        return {
          ...safeInvestment,
          currentValue,
          gainLoss,
          gainLossPercent,
          isPositive: gainLoss >= 0
        };
      })
      .filter(investment => investment.quantity > 0); // Only show investments with remaining shares
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchPortfolioData();
      await fetchAvailableStocks();
      toast.success('Portfolio refreshed successfully');
    } catch (err) {
      console.error('Error refreshing portfolio:', err);
      toast.error('Failed to refresh portfolio');
    } finally {
      setRefreshing(false);
    }
  };

  const handleSort = (key: keyof InvestmentTableData) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const getSortedInvestments = () => {
    // Filter out undefined/null investments and safely handle missing properties
    const filtered = investments.filter(investment => {
      if (!investment || typeof investment !== 'object') return false;
      
      const stockSymbol = investment.stockSymbol || '';
      const companyName = investment.companyName || '';
      
      return stockSymbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
             companyName.toLowerCase().includes(searchTerm.toLowerCase());
    });

    return filtered.sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortConfig.direction === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      return 0;
    });
  };

  const handleQuickAction = (action: string, investment?: InvestmentTableData) => {
    switch (action) {
      case 'buy':
        openBuyModal();
        break;
      case 'sell':
        if (investment) {
          openSellModal(investment);
        }
        break;
      case 'add_cash':
        openAddCashModal();
        break;
      default:
        break;
    }
  };

  const openBuyModal = () => {
    setTransactionModal({
      isOpen: true,
      type: 'buy',
      stock: null,
      investment: null
    });
    setTransactionForm({
      quantity: 0,
      price: 0,
      total: 0
    });
    setSelectedStock(null);
  };

  const openSellModal = (investment: InvestmentTableData) => {
    // Create a stock object from investment data for the transaction modal
    const stockData: StockData = {
      code: investment.stockSymbol || '',
      name: investment.companyName || '',
      sector: investment.sector || '',
      open_price: investment.currentPrice || 0,
      high_price: investment.currentPrice || 0,
      low_price: investment.currentPrice || 0,
      close_price: investment.currentPrice || 0,
      volume: 0,
      change: 0,
      change_percent: 0,
      timestamp: new Date().toISOString()
    };

    setTransactionModal({
      isOpen: true,
      type: 'sell',
      stock: stockData,
      investment
    });
    setTransactionForm({
      quantity: 0,
      price: investment.currentPrice || 0,
      total: 0
    });
  };

  const openAddCashModal = () => {
    setAddCashModal({
      isOpen: true,
      amount: 0
    });
  };

  const closeModal = () => {
    setTransactionModal({
      isOpen: false,
      type: null,
      stock: null,
      investment: null
    });
    setAddCashModal({
      isOpen: false,
      amount: 0
    });
    setTransactionForm({
      quantity: 0,
      price: 0,
      total: 0
    });
    setSelectedStock(null);
  };

  const handleStockSelect = (stock: StockData) => {
    setSelectedStock(stock);
    setTransactionModal(prev => ({
      ...prev,
      stock: stock
    }));
    setTransactionForm(prev => ({
      ...prev,
      price: stock.close_price || 0,
      total: prev.quantity * (stock.close_price || 0)
    }));
  };

  const handleQuantityChange = (quantity: number) => {
    const price = transactionForm.price;
    const total = quantity * price;
    
    setTransactionForm(prev => ({
      ...prev,
      quantity,
      total
    }));
  };

  const handlePriceChange = (price: number) => {
    const quantity = transactionForm.quantity;
    const total = quantity * price;
    
    setTransactionForm(prev => ({
      ...prev,
      price,
      total
    }));
  };

  const validateTransaction = (): boolean => {
    if (!selectedStock && transactionModal.type === 'buy') {
      toast.error('Please select a stock to buy');
      return false;
    }

    if (transactionForm.quantity <= 0) {
      toast.error('Quantity must be greater than 0');
      return false;
    }

    if (transactionForm.price <= 0) {
      toast.error('Price must be greater than 0');
      return false;
    }

    if (transactionModal.type === 'buy') {
      const requiredCash = transactionForm.total;
      if (requiredCash > (metrics?.cashBalance || 0)) {
        toast.error('Insufficient cash balance');
        return false;
      }
    }

    if (transactionModal.type === 'sell') {
      const investment = transactionModal.investment;
      if (!investment || transactionForm.quantity > (investment.quantity || 0)) {
        toast.error('Cannot sell more shares than you own');
        return false;
      }
    }

    return true;
  };

  const handleTransaction = async (transactionData: any) => {
    try {
      setRefreshing(true);
      
      const response = await addInvestment(transactionData);
      
      if (response.success) {
        toast.success(response.message || 'Transaction completed successfully');
        
        // Refresh portfolio data to show updated values
        await fetchPortfolioData();
        
        // Close modal
        setTransactionModal({ isOpen: false, type: null, stock: null, investment: null });
        setTransactionForm({ quantity: 0, price: 0, total: 0 });
      } else {
        toast.error(response.message || 'Transaction failed');
      }
    } catch (error: any) {
      console.error('Transaction error:', error);
      toast.error('Transaction failed. Please try again.');
    } finally {
      setRefreshing(false);
    }
  };

  const executeTransaction = async () => {
    // Use the comprehensive validation function instead of inline validation
    if (!validateTransaction()) {
      return;
    }

    const transactionData = {
      user_id: user?.id || '',
      stock_code: transactionModal.stock?.code || selectedStock?.code || '',
      quantity: transactionForm.quantity || 0,
      price: transactionForm.price || 0,
      transaction_type: transactionModal.type || 'buy'
    };

    await handleTransaction(transactionData);
  };

  const executeAddCash = async () => {
    if (!user?.id || addCashModal.amount <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    try {
      // Call backend to add cash to portfolio
      const result = await addCashToPortfolio(user.id, addCashModal.amount);
      
      if (result.success) {
        toast.success(result.message || `Added ${formatCurrency(addCashModal.amount)} to your portfolio`);
        closeModal();
        
        // Refresh portfolio data to get updated values
        await fetchPortfolioData();
      } else {
        toast.error(result.message || 'Failed to add cash to portfolio');
      }
    } catch (err: any) {
      console.error('Error adding cash:', err);
      toast.error('Failed to add cash to portfolio');
    }
  };

  const getSortIcon = (key: keyof InvestmentTableData) => {
    if (sortConfig.key !== key) {
      return <SortAsc className="w-4 h-4 text-gray-400" />;
    }
    return sortConfig.direction === 'asc' 
      ? <SortAsc className="w-4 h-4 text-blue-600" />
      : <SortDesc className="w-4 h-4 text-blue-600" />;
  };

  // Generate performance data for charts
  const generatePerformanceData = () => {
    if (!portfolio || !metrics) return [];
    
    // Generate sample data points for the last 7 days
    const data = [];
    const today = new Date();
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      // Simulate some variation in the data
      const variation = 1 + (Math.random() - 0.5) * 0.1; // ±5% variation
      
      data.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        totalValue: metrics.totalValue * variation,
        totalInvested: metrics.totalInvested,
        cashBalance: metrics.cashBalance
      });
    }
    
    return data;
  };

  // Render loading, error, or portfolio display
  if (loading || error || !portfolio) {
    return (
      <MainLayout>
        <PortfolioDisplay
          portfolio={portfolio}
          loading={loading}
          error={error}
          onRefresh={handleRefresh}
        />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {/* Portfolio Header */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row justify-between md:items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              My Portfolio
            </h1>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Manage your investments and track performance
            </p>
          </div>
          
          <div className="flex space-x-4 mt-4 md:mt-0">
            <button
              onClick={() => handleQuickAction('add_cash')}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md flex items-center"
            >
              <PlusCircle className="w-4 h-4 mr-2" />
              Add Cash
            </button>
            <button
              onClick={() => handleQuickAction('buy')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Buy Stock
            </button>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className={`px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-md flex items-center ${refreshing ? 'opacity-50 cursor-wait' : ''}`}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
      </div>
      
      {/* Portfolio Display */}
      <PortfolioDisplay
        portfolio={portfolio}
        loading={loading}
        error={error}
        onRefresh={handleRefresh}
        metrics={metrics}
      />

      {/* Portfolio Charts Section */}
      {!loading && !error && portfolio && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Portfolio Performance Chart */}
            <PortfolioPerformanceChart
              data={generatePerformanceData()}
              loading={loading}
            />
            
            {/* Portfolio Metrics Chart */}
            {metrics && (
              <PortfolioMetricsChart
                metrics={metrics}
                loading={loading}
              />
            )}
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                              {/* Sector Allocation Chart */}
                  <SectorAllocationChart
                    data={portfolio.allocation}
                    loading={loading}
                  />
            
            {/* Investment Performance Chart */}
            <InvestmentPerformanceChart
              investments={portfolio.investments}
              loading={loading}
            />
          </div>
        </div>
      )}
      

      
      {/* Enhanced Investments Table with Search and Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row justify-between md:items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 md:mb-0">
              Your Holdings
            </h2>
            
            <div className="flex space-x-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search stocks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          </div>
        </div>
        
        {getSortedInvestments().length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('stockSymbol')}>
                    <div className="flex items-center">
                      Stock
                      {getSortIcon('stockSymbol')}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('quantity')}>
                    <div className="flex items-center">
                      Quantity
                      {getSortIcon('quantity')}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('purchasePrice')}>
                    <div className="flex items-center">
                      Avg Price
                      {getSortIcon('purchasePrice')}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('currentPrice')}>
                    <div className="flex items-center">
                      Current Price
                      {getSortIcon('currentPrice')}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('currentValue')}>
                    <div className="flex items-center">
                      Current Value
                      {getSortIcon('currentValue')}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer" onClick={() => handleSort('gainLoss')}>
                    <div className="flex items-center">
                      Gain/Loss
                      {getSortIcon('gainLoss')}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {getSortedInvestments().map((investment, index) => {
                  // Create a unique key using the utility function
                  const uniqueKey = generateUniqueKey(investment, index, 'inv');
                  
                  return (
                    <tr key={uniqueKey} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {investment.stockSymbol}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {investment.companyName}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                             {(investment.quantity || 0).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {formatCurrency(investment.purchasePrice)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {formatCurrency(investment.currentPrice)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {formatCurrency(investment.currentValue)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm font-medium ${getValueColor(investment.gainLoss)}`}>
                        {formatCurrency(investment.gainLoss)}
                      </div>
                      <div className={`text-xs ${getValueColor(investment.gainLossPercent)}`}>
                        {formatPercentage(investment.gainLossPercent)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => openSellModal(investment)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                      >
                        <MinusCircle className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center">
            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <Target className="w-8 h-4 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              No Holdings Yet
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              Start building your portfolio by buying your first stock.
            </p>
            <button
              onClick={() => handleQuickAction('buy')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center mx-auto"
            >
              <Plus className="w-4 h-4 mr-2" />
              Buy Your First Stock
            </button>
          </div>
        )}
      </div>

      {/* Transaction Modal */}
      <AnimatePresence>
        {transactionModal.isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {transactionModal.type === 'buy' ? 'Buy Stock' : 'Sell Stock'}
                  </h3>
                  <button
                    onClick={closeModal}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {transactionModal.type === 'buy' && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Select Stock
                    </label>
                    <select
                      value={selectedStock?.code || ''}
                      onChange={(e) => {
                        const stock = availableStocks.find(s => s.code === e.target.value);
                        if (stock) handleStockSelect(stock);
                      }}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="">Select a stock...</option>
                      {availableStocks.map((stock, index) => (
                        <option key={generateUniqueKey(stock, index, 'stock')} value={stock.code}>
                          {stock.code} - {stock.name} (₹{stock.close_price})
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {transactionModal.type === 'sell' && transactionModal.investment && (
                  <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-md">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                      Selling: {transactionModal.investment.stockSymbol}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      You own {transactionModal.investment.quantity} shares
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Current Market Price: {formatCurrency(transactionModal.investment.currentPrice)}
                    </p>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Quantity
                    </label>
                    <input
                      type="number"
                      value={transactionForm.quantity}
                      onChange={(e) => handleQuantityChange(Number(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      min="1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Price per Share
                    </label>
                    <input
                      type="number"
                      value={transactionForm.price}
                      onChange={(e) => handlePriceChange(Number(e.target.value) || 0)}
                      className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white ${
                        transactionModal.type === 'sell' ? 'bg-gray-100 dark:bg-gray-600 cursor-not-allowed' : ''
                      }`}
                      min="0.01"
                      step="0.01"
                      disabled={transactionModal.type === 'sell'}
                    />
                    {transactionModal.type === 'sell' && (
                      <p className="text-xs text-gray-500 mt-1">
                        Price is set to current market value
                      </p>
                    )}
                  </div>
                </div>

                <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-md">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Total Amount:
                    </span>
                    <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {formatCurrency(transactionForm.total)}
                    </span>
                  </div>
                  {transactionModal.type === 'buy' && metrics && (
                    <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      Available Cash: {formatCurrency(metrics.cashBalance)}
                    </div>
                  )}
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={closeModal}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={executeTransaction}
                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md"
                  >
                    {transactionModal.type === 'buy' ? 'Buy' : 'Sell'}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Add Cash Modal */}
      <AnimatePresence>
        {addCashModal.isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={closeModal}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Add Cash to Portfolio
                  </h3>
                  <button
                    onClick={closeModal}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Amount to Add
                  </label>
                  <input
                    type="number"
                    value={addCashModal.amount}
                    onChange={(e) => setAddCashModal(prev => ({ ...prev, amount: Number(e.target.value) }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    min="1"
                    step="1"
                    placeholder="Enter amount..."
                  />
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={closeModal}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={executeAddCash}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md"
                  >
                    Add Cash
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </MainLayout>
  );
};

export default EnhancedPortfolioPage;
