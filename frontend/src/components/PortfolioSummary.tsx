import React, { useState } from 'react';
import { Portfolio, Investment } from '../types';
import { TrendingUp, TrendingDown, DollarSign, PieChart, Edit2, Check } from 'lucide-react';

interface PortfolioSummaryProps {
  portfolio: Portfolio;
  onUpdateTotalValue?: (newValue: number) => void;
}

const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({ portfolio, onUpdateTotalValue }) => {
  // Add null check for portfolio and its properties
  if (!portfolio) {
    return <div className="p-4">No portfolio data available</div>;
  }
  
  const [isEditingValue, setIsEditingValue] = useState(false);
  // Use useEffect to update customValue when portfolio changes
  const [customValue, setCustomValue] = useState(portfolio.totalValue || 0);
  
  // Update customValue when portfolio.totalValue changes
  React.useEffect(() => {
    if (portfolio.totalValue && portfolio.totalValue > 0) {
      setCustomValue(portfolio.totalValue);
    }
  }, [portfolio.totalValue]);
  
  // Handle form submission for updating total value
  const handleSubmitValue = (e: React.FormEvent) => {
    e.preventDefault();
    if (onUpdateTotalValue && !isNaN(customValue) && customValue > 0) {
      onUpdateTotalValue(customValue);
    }
    setIsEditingValue(false);
  };
  
  const isPositiveReturn = portfolio.totalReturns >= 0;
  
  const handleValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    setCustomValue(isNaN(value) ? 0 : value);
  };
  
  const saveCustomValue = () => {
    if (onUpdateTotalValue && !isNaN(customValue) && customValue > 0) {
      onUpdateTotalValue(customValue);
    }
    setIsEditingValue(false);
  };
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Value</h3>
            {isEditingValue ? (
              <button onClick={saveCustomValue} className="text-blue-500 hover:text-blue-700">
                <Check size={18} />
              </button>
            ) : (
              <button onClick={() => setIsEditingValue(true)} className="text-blue-500 hover:text-blue-700">
                <Edit2 size={18} />
              </button>
            )}
          </div>
          {isEditingValue ? (
            <form onSubmit={handleSubmitValue} className="mt-1">
              <div className="flex items-center">
                <span className="text-lg font-bold mr-2">PKR</span>
                <input 
                  type="number" 
                  value={customValue} 
                  onChange={handleValueChange} 
                  className="input w-full text-xl font-bold" 
                  min="0"
                  step="1000"
                  autoFocus
                />
              </div>
              <div className="mt-2 flex justify-end">
                <button 
                  type="button" 
                  onClick={() => setIsEditingValue(false)} 
                  className="text-gray-500 mr-2"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn-primary btn-sm"
                >
                  Save
                </button>
              </div>
            </form>
          ) : (
            <p className="text-2xl font-bold mt-1">PKR {(portfolio?.totalValue || 0).toLocaleString()}</p>
          )}
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Invested</h3>
            <DollarSign size={18} className="text-gray-500" />
          </div>
          <p className="text-2xl font-bold mt-1">PKR {portfolio?.totalInvested?.toLocaleString() || '0'}</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Returns</h3>
            {isPositiveReturn ? (
              <TrendingUp size={18} className="text-green-500" />
            ) : (
              <TrendingDown size={18} className="text-red-500" />
            )}
          </div>
          <p className={`text-2xl font-bold mt-1 ${isPositiveReturn ? 'text-green-500' : 'text-red-500'}`}>
            {isPositiveReturn ? '+' : ''}PKR {portfolio?.totalReturns?.toLocaleString() || '0'}
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Return %</h3>
            {isPositiveReturn ? (
              <TrendingUp size={18} className="text-green-500" />
            ) : (
              <TrendingDown size={18} className="text-red-500" />
            )}
          </div>
          <p className={`text-2xl font-bold mt-1 ${isPositiveReturn ? 'text-green-500' : 'text-red-500'}`}>
            {isPositiveReturn ? '+' : ''}{portfolio?.returnPercentage?.toFixed(2) || '0.00'}%
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Cash Balance</h3>
            <DollarSign size={18} className="text-green-500" />
          </div>
          <p className="text-2xl font-bold mt-1">PKR {(portfolio?.cashBalance || 0).toLocaleString()}</p>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">Your Investments</h3>
            <PieChart size={18} className="text-blue-500" />
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Purchase Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Current Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Gain/Loss
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {!portfolio.investments || portfolio.investments.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    No investments found. Start by buying some stocks!
                  </td>
                </tr>
              ) : portfolio.investments.map((investment) => {
                if (!investment) return null;
                
                const currentPrice = investment.currentPrice || 0;
                const purchasePrice = investment.purchasePrice || 0;
                const quantity = investment.quantity || 0;
                
                const currentValue = currentPrice * quantity;
                const purchaseValue = purchasePrice * quantity;
                const gainLoss = currentValue - purchaseValue;
                const gainLossPercent = purchaseValue > 0 ? (gainLoss / purchaseValue) * 100 : 0;
                const isPositive = gainLoss >= 0;
                
                return (
                  <tr key={investment.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium">{investment.stockSymbol}</div>
                          <div className="text-xs text-gray-500">{investment.companyName}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      PKR {purchasePrice.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      PKR {currentPrice.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      PKR {currentValue.toLocaleString()}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                      {isPositive ? '+' : ''}PKR {gainLoss.toLocaleString()} ({isPositive ? '+' : ''}{gainLossPercent.toFixed(2)}%)
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PortfolioSummary;