import React from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import { formatCurrency, formatPercentage } from '../../utils';
import { PortfolioMetrics } from '../../types';

interface PortfolioMetricsChartProps {
  metrics: PortfolioMetrics;
  loading?: boolean;
}

const PortfolioMetricsChart: React.FC<PortfolioMetricsChartProps> = ({ metrics, loading = false }) => {
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

  if (!metrics) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Portfolio Metrics
        </h3>
        <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
          No metrics data available
        </div>
      </div>
    );
  }

  // Normalize metrics for radar chart (0-100 scale)
  const maxValues = {
    totalValue: Math.max(metrics.totalValue, 10000),
    totalInvested: Math.max(metrics.totalInvested, 10000),
    cashBalance: Math.max(metrics.cashBalance, 10000),
    totalReturns: Math.max(Math.abs(metrics.totalReturns), 5000),
    returnPercentage: Math.max(Math.abs(metrics.returnPercentage), 50),
    activeInvestments: Math.max(metrics.activeInvestments, 10)
  };

  const chartData = [
    {
      metric: 'Total Value',
      value: (metrics.totalValue / maxValues.totalValue) * 100,
      fullMark: 100
    },
    {
      metric: 'Total Invested',
      value: (metrics.totalInvested / maxValues.totalInvested) * 100,
      fullMark: 100
    },
    {
      metric: 'Cash Balance',
      value: (metrics.cashBalance / maxValues.cashBalance) * 100,
      fullMark: 100
    },
    {
      metric: 'Total Returns',
      value: ((metrics.totalReturns + maxValues.totalReturns) / (2 * maxValues.totalReturns)) * 100,
      fullMark: 100
    },
    {
      metric: 'Return %',
      value: ((metrics.returnPercentage + maxValues.returnPercentage) / (2 * maxValues.returnPercentage)) * 100,
      fullMark: 100
    },
    {
      metric: 'Active Positions',
      value: (metrics.activeInvestments / maxValues.activeInvestments) * 100,
      fullMark: 100
    }
  ];

  const formatTooltip = (value: any, name: string, props: any) => {
    const metricName = props.payload.metric;
    let actualValue;
    
    switch (metricName) {
      case 'Total Value':
        actualValue = formatCurrency(metrics.totalValue);
        break;
      case 'Total Invested':
        actualValue = formatCurrency(metrics.totalInvested);
        break;
      case 'Cash Balance':
        actualValue = formatCurrency(metrics.cashBalance);
        break;
      case 'Total Returns':
        actualValue = formatCurrency(metrics.totalReturns);
        break;
      case 'Return %':
        actualValue = formatPercentage(metrics.returnPercentage);
        break;
      case 'Active Positions':
        actualValue = `${metrics.activeInvestments} positions`;
        break;
      default:
        actualValue = value;
    }
    
    return [actualValue, metricName];
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Portfolio Metrics Overview
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          <PolarGrid stroke="#374151" opacity={0.3} />
          <PolarAngleAxis 
            dataKey="metric" 
            stroke="#6B7280"
            fontSize={12}
            tickLine={false}
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 100]} 
            stroke="#6B7280"
            fontSize={10}
            tickLine={false}
            axisLine={false}
          />
          <Radar
            name="Portfolio Metrics"
            dataKey="value"
            stroke="#3B82F6"
            fill="#3B82F6"
            fillOpacity={0.3}
            strokeWidth={2}
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
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PortfolioMetricsChart; 