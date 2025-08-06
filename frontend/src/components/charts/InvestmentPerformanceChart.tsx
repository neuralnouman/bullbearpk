import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { formatCurrency, formatPercentage, getValueColor } from '../../utils';
import { Investment } from '../../types';

interface InvestmentPerformanceChartProps {
  investments: Investment[];
  loading?: boolean;
}

interface ChartDataPoint {
  stockSymbol: string;
  currentValue: number;
  investedValue: number;
  profitLoss: number;
  profitLossPercent: number;
}

const InvestmentPerformanceChart: React.FC<InvestmentPerformanceChartProps> = ({ 
  investments, 
  loading = false 
}) => {
  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (!investments || investments.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Investment Performance
        </h3>
        <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
          No investment data available
        </div>
      </div>
    );
  }

  // Process data for chart
  const chartData: ChartDataPoint[] = investments.map(investment => {
    const currentValue = investment.quantity * investment.currentPrice;
    const investedValue = investment.quantity * investment.purchasePrice;
    const profitLoss = currentValue - investedValue;
    const profitLossPercent = investedValue > 0 ? (profitLoss / investedValue) * 100 : 0;

    return {
      stockSymbol: investment.stockSymbol,
      currentValue,
      investedValue,
      profitLoss,
      profitLossPercent
    };
  });

  const formatTooltip = (value: any, name: string) => {
    if (name === 'profitLossPercent') {
      return [formatPercentage(value), 'Return %'];
    }
    return [formatCurrency(value), name];
  };

  const CustomBar = (props: any) => {
    const { x, y, width, height, profitLoss } = props;
    const color = profitLoss >= 0 ? '#10B981' : '#EF4444';
    
    return (
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={color}
        radius={[2, 2, 0, 0]}
      />
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Investment Performance
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis 
            dataKey="stockSymbol" 
            stroke="#6B7280"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            stroke="#6B7280"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => formatCurrency(value)}
          />
          <Tooltip 
            formatter={formatTooltip}
            contentStyle={{
              backgroundColor: '#1F2937',
              border: 'none',
              borderRadius: '8px',
              color: '#F9FAFB'
            }}
          />
          <Legend />
          <Bar 
            dataKey="currentValue" 
            fill="#3B82F6" 
            name="Current Value"
            radius={[2, 2, 0, 0]}
          />
          <Bar 
            dataKey="investedValue" 
            fill="#6B7280" 
            name="Invested Value"
            radius={[2, 2, 0, 0]}
          />
          <Bar 
            dataKey="profitLoss" 
            fill="#10B981" 
            name="Profit/Loss"
            radius={[2, 2, 0, 0]}
            shape={<CustomBar />}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default InvestmentPerformanceChart; 