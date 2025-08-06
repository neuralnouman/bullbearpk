import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Clock, Search, Filter, RefreshCw } from 'lucide-react';
import { formatNumber } from '../utils';
import { marketService } from '../services/marketService';
import { StockData } from '../types';

// Local interfaces for MarketSummary, ScrapeInfo, and MarketDataResponse
interface MarketSummary {
  top_gainer: StockData;
  top_loser: StockData;
  highest_volume: StockData;
}

interface ScrapeInfo {
  timestamp: string;
  total_stocks: number;
  gainers: number;
  losers: number;
  unchanged: number;
}

interface MarketDataResponse {
  scrape_info: ScrapeInfo;
  market_summary: MarketSummary;
  stocks: StockData[];
}

interface RefreshResponse {
  success: boolean;
  message?: string;
  stocks?: StockData[];
  market_summary?: MarketSummary;
  scrape_info?: ScrapeInfo;
}

const MarketData: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketDataResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterSector, setFilterSector] = useState<string>('All');
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' }>({ 
    key: 'symbol', 
    direction: 'asc' 
  });

  const fetchMarketData = async (refresh: boolean = false) => {
    setLoading(true);
    setError(null);
    try {
      let data;
      if (refresh) {
        // Use the refresh endpoint to get fresh data
        const refreshData = await marketService.refreshMarketData() as RefreshResponse;
        // The refresh endpoint now returns the full market data
        if (refreshData.success && refreshData.stocks) {
          setMarketData({
            stocks: refreshData.stocks,
            market_summary: refreshData.market_summary!,
            scrape_info: refreshData.scrape_info!
          });
        } else {
          throw new Error(refreshData.message || 'Failed to refresh market data');
        }
      } else {
        // Just get the latest data from the database
        data = await marketService.getMarketData();
        setMarketData(data);
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error fetching market data. Please try again.';
      setError(errorMessage);
      console.error('Error fetching market data:', err);
      
      // Show a more user-friendly message for common errors
      if (errorMessage.includes('Database connection failed') || errorMessage.includes('MySQL')) {
        setError('Database connection issue. Please check if MySQL is running and the backend is properly configured.');
      } else if (errorMessage.includes('No market data available')) {
        setError('No market data available. The database may be empty or not properly initialized.');
      } else if (errorMessage.includes('Network error')) {
        setError('Network error. Please check if the backend server is running on localhost:5000.');
      } else if (errorMessage.includes('Server error')) {
        setError('Server error occurred. Please try again later or contact support.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketData();
  }, []);

  const handleSort = (key: string) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const [filteredStocks, setFilteredStocks] = useState<StockData[]>([]);
  
  useEffect(() => {
    if (!marketData?.stocks) return;
    
    const handleFiltering = async () => {
      try {
        if (searchTerm) {
          const searchResults = await marketService.searchStocks(searchTerm);
          setFilteredStocks(searchResults.stocks
            .filter(stock => filterSector === 'All' || stock.sector === filterSector)
            .sort((a, b) => {
              const key = sortConfig.key as keyof StockData;
              if (a[key] < b[key]) return sortConfig.direction === 'asc' ? -1 : 1;
              if (a[key] > b[key]) return sortConfig.direction === 'asc' ? 1 : -1;
              return 0;
            }));
        } else {
          setFilteredStocks(marketData.stocks
            .filter(stock => filterSector === 'All' || stock.sector === filterSector)
            .sort((a, b) => {
              const key = sortConfig.key as keyof StockData;
              if (a[key] < b[key]) return sortConfig.direction === 'asc' ? -1 : 1;
              if (a[key] > b[key]) return sortConfig.direction === 'asc' ? 1 : -1;
              return 0;
            }));
        }
      } catch (err) {
        console.error('Error searching stocks:', err);
        setFilteredStocks([]);
      }
    };

    handleFiltering();
  }, [marketData, searchTerm, filterSector, sortConfig]);

  const uniqueSectors = marketData?.stocks
    ? ['All', ...new Set(marketData.stocks.map(stock => stock.sector))]
    : ['All'];

  return (
    <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold mb-2">Market Data</h2>
                      <p className="text-gray-600 dark:text-gray-400 flex items-center">
              <Clock size={16} className="mr-1" />
              Last updated: {marketData?.scrape_info?.timestamp 
                ? new Date(marketData.scrape_info.timestamp).toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                  })
                : 'Loading...'}
              {marketData?.scrape_info?.total_stocks && (
                <span className="ml-2 text-sm text-gray-500">
                  ({marketData.scrape_info.total_stocks} stocks)
                </span>
              )}
            </p>
        </div>
        <div className="mt-4 md:mt-0 flex items-center">
          <button 
            onClick={() => fetchMarketData(true)} 
            className="btn-primary flex items-center"
            disabled={loading}
          >
            <RefreshCw size={16} className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {marketData?.market_summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-900"
          >
            <div className="flex items-center mb-2">
              <TrendingUp size={20} className="text-green-600 mr-2" />
              <h3 className="font-semibold">Top Gainer</h3>
            </div>
            <div className="text-lg font-bold">{marketData.market_summary.top_gainer.code}</div>
            <div className="text-sm">{marketData.market_summary.top_gainer.name}</div>
            <div className="mt-2 text-green-600 font-semibold">
              +{(typeof marketData.market_summary.top_gainer.change_percent === 'string' 
                ? parseFloat(marketData.market_summary.top_gainer.change_percent) 
                : marketData.market_summary.top_gainer.change_percent).toFixed(2)}%
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-900"
          >
            <div className="flex items-center mb-2">
              <TrendingDown size={20} className="text-red-600 mr-2" />
              <h3 className="font-semibold">Top Loser</h3>
            </div>
            <div className="text-lg font-bold">{marketData.market_summary.top_loser.code}</div>
            <div className="text-sm">{marketData.market_summary.top_loser.name}</div>
            <div className="mt-2 text-red-600 font-semibold">
              {(typeof marketData.market_summary.top_loser.change_percent === 'string' 
                ? parseFloat(marketData.market_summary.top_loser.change_percent) 
                : marketData.market_summary.top_loser.change_percent).toFixed(2)}%
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
            className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-900"
          >
            <div className="flex items-center mb-2">
              <TrendingUp size={20} className="text-blue-600 mr-2" />
              <h3 className="font-semibold">Highest Volume</h3>
            </div>
            <div className="text-lg font-bold">{marketData.market_summary.highest_volume.code}</div>
            <div className="text-sm">{marketData.market_summary.highest_volume.name}</div>
            <div className="mt-2 text-blue-600 font-semibold">
              {formatNumber(marketData.market_summary.highest_volume.volume)} shares
            </div>
          </motion.div>
        </div>
      )}

      <div className="mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
          <div className="relative w-full md:w-64 mb-4 md:mb-0">
            <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name or symbol"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10 w-full"
            />
          </div>
          <div className="flex items-center">
            <Filter size={16} className="mr-2 text-gray-500" />
            <select
              value={filterSector}
              onChange={(e) => setFilterSector(e.target.value)}
              className="input"
            >
              {uniqueSectors.map(sector => (
                <option key={sector} value={sector}>{sector}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Stock Data Table */}
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-100 dark:bg-gray-800">
                <tr>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('code')}
                  >
                    Symbol {sortConfig.key === 'code' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('name')}
                  >
                    Name {sortConfig.key === 'name' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('sector')}
                  >
                    Sector {sortConfig.key === 'sector' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('open_price')}
                  >
                    Open {sortConfig.key === 'open_price' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('high_price')}
                  >
                    High {sortConfig.key === 'high_price' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('low_price')}
                  >
                    Low {sortConfig.key === 'low_price' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('close_price')}
                  >
                    Close {sortConfig.key === 'close_price' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('change_percent')}
                  >
                    Change % {sortConfig.key === 'change_percent' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                    onClick={() => handleSort('volume')}
                  >
                    Volume {sortConfig.key === 'volume' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {loading ? (
                  <tr>
                    <td colSpan={9} className="px-6 py-4 text-center">
                      <div className="flex justify-center items-center">
                        <div className="w-6 h-6 border-2 border-t-primary-600 rounded-full animate-spin mr-2"></div>
                        Loading market data...
                      </div>
                    </td>
                  </tr>
                ) : filteredStocks.length > 0 ? (
                  filteredStocks.map((stock, index) => (
                    <motion.tr 
                      key={stock.code}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.2, delay: index * 0.01 }}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700/50"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{stock.code}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{stock.name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{stock.sector}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {typeof stock.open_price === 'string' ? parseFloat(stock.open_price).toFixed(2) : stock.open_price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {typeof stock.high_price === 'string' ? parseFloat(stock.high_price).toFixed(2) : stock.high_price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {typeof stock.low_price === 'string' ? parseFloat(stock.low_price).toFixed(2) : stock.low_price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {typeof stock.close_price === 'string' ? parseFloat(stock.close_price).toFixed(2) : stock.close_price.toFixed(2)}
                      </td>
                      <td
                        className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                          (typeof stock.change_percent === 'string' ? parseFloat(stock.change_percent) : stock.change_percent) > 0
                            ? 'text-green-600'
                            : (typeof stock.change_percent === 'string' ? parseFloat(stock.change_percent) : stock.change_percent) < 0
                            ? 'text-red-600'
                            : 'text-gray-500'
                        }`}
                      >
                        {(typeof stock.change_percent === 'string' ? parseFloat(stock.change_percent) : stock.change_percent) > 0 ? '+' : ''}
                        {(typeof stock.change_percent === 'string' ? parseFloat(stock.change_percent) : stock.change_percent).toFixed(2)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{formatNumber(stock.volume)}</td>
                    </motion.tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={9} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                      No stocks found matching your criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {marketData?.scrape_info && (
          <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex flex-wrap gap-4">
              <span>Total Stocks: {marketData.scrape_info.total_stocks}</span>
              <span className="text-green-600">Gainers: {marketData.scrape_info.gainers}</span>
              <span className="text-red-600">Losers: {marketData.scrape_info.losers}</span>
              <span>Unchanged: {marketData.scrape_info.unchanged}</span>
            </div>
          </div>
        )}
      </div>

      {loading && (
        <div className="mb-4 flex items-center text-blue-600">
          <RefreshCw className="animate-spin mr-2" size={18} />
          Fetching live market data...
        </div>
      )}
    </div>
  );
};

export default MarketData;