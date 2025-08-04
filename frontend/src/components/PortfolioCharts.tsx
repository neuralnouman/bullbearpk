import React from 'react';
import { Portfolio } from '../types';
import { PieChart, BarChart, LineChart } from 'lucide-react';

interface PortfolioChartsProps {
  portfolio: Portfolio;
}

const PortfolioCharts: React.FC<PortfolioChartsProps> = ({ portfolio }) => {
  // Check if portfolio has investments
  const hasInvestments = portfolio.investments && portfolio.investments.length > 0;
  
  // Check if portfolio has allocation data
  const hasAllocation = portfolio.allocation && portfolio.allocation.length > 0;
  
  if (!hasInvestments) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          No investment data available for analysis. Add investments to see charts.
        </p>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Sector Allocation Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium">Sector Allocation</h3>
          <PieChart size={18} className="text-blue-500" />
        </div>
        
        {hasAllocation ? (
          <>
            <div className="h-64 flex items-center justify-center">
              <div className="relative w-48 h-48">
                {/* Simple pie chart visualization */}
                {portfolio.allocation.map((sector, index) => {
                  // Ensure percentage is a valid number
                  const percentage = isNaN(sector.percentage) ? 0 : sector.percentage;
                  
                  const startAngle = portfolio.allocation
                    .slice(0, index)
                    .reduce((sum, s) => {
                      const pct = isNaN(s.percentage) ? 0 : s.percentage;
                      return sum + pct;
                    }, 0) * 3.6;
                  
                  const angle = percentage * 3.6;
                  
                  return (
                    <div 
                      key={sector.sector}
                      className="absolute inset-0"
                      style={{
                        background: `conic-gradient(transparent ${startAngle}deg, ${sector.color} ${startAngle}deg, ${sector.color} ${startAngle + angle}deg, transparent ${startAngle + angle}deg)`,
                        borderRadius: '50%'
                      }}
                    />
                  );
                })}
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-2 mt-4">
              {portfolio.allocation.map(sector => {
                // Ensure percentage is a valid number
                const percentage = isNaN(sector.percentage) ? 0 : sector.percentage;
                
                return (
                  <div key={sector.sector} className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded-full mr-2" 
                      style={{ backgroundColor: sector.color }}
                    />
                    <span className="text-sm">{sector.sector}: {percentage.toFixed(1)}%</span>
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500 dark:text-gray-400">
              No sector allocation data available.
            </p>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Top Holdings Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Top Holdings</h3>
            <BarChart size={18} className="text-blue-500" />
          </div>
          
          {hasInvestments ? (
            <div className="space-y-2">
              {portfolio.investments
                .sort((a, b) => ((b.currentPrice || 0) * (b.quantity || 0)) - ((a.currentPrice || 0) * (a.quantity || 0)))
                .slice(0, 5)
                .map(investment => {
                  const value = (investment.currentPrice || 0) * (investment.quantity || 0);
                  const totalValue = portfolio.totalValue || 1; // Prevent division by zero
                  const percentage = (value / totalValue) * 100;
                  
                  return (
                    <div key={investment.id} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>{investment.stockSymbol}</span>
                        <span>{isNaN(percentage) ? '0.0' : percentage.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `${isNaN(percentage) ? 0 : percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">
                No investment data available.
              </p>
            </div>
          )}
        </div>
        
        {/* Performance Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Performance</h3>
            <LineChart size={18} className="text-blue-500" />
          </div>
          
          {hasInvestments && portfolio.investments.length > 0 ? (
            <div className="h-48 flex items-end justify-between px-2">
              {/* Simple bar chart visualization */}
              {portfolio.investments.slice(0, 7).map(investment => {
                const purchasePrice = investment.purchasePrice || 0;
                const currentPrice = investment.currentPrice || 0;
                
                // Calculate gain/loss percentage, handle division by zero
                let gainLoss = 0;
                if (purchasePrice > 0) {
                  gainLoss = ((currentPrice - purchasePrice) / purchasePrice) * 100;
                }
                
                // Ensure gainLoss is a valid number
                gainLoss = isNaN(gainLoss) ? 0 : gainLoss;
                
                // Calculate bar height (minimum 5% for visibility)
                const height = Math.max(5, Math.min(Math.abs(gainLoss) * 2, 100));
                
                return (
                  <div key={investment.id} className="flex flex-col items-center">
                    <div 
                      className={`w-8 ${gainLoss >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                      style={{ height: `${height}%` }}
                    />
                    <span className="text-xs mt-1">{investment.stockSymbol}</span>
                    <span className={`text-xs ${gainLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {gainLoss >= 0 ? '+' : ''}{gainLoss.toFixed(1)}%
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">
                No performance data available.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PortfolioCharts;