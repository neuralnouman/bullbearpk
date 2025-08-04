import React, { useState, useEffect } from 'react';
import { marketService } from '../services/marketService';

interface BuyStockFormProps {
  onSubmit: (formData: BuyStockFormData) => void;
  availableFunds?: number;
}

export interface BuyStockFormData {
  company: string;
  amount: number;
}

const BuyStockForm: React.FC<BuyStockFormProps> = ({ onSubmit, availableFunds = 0 }) => {
  const [formData, setFormData] = useState<BuyStockFormData>({
    company: '',
    amount: 0,
  });
  const [amountInput, setAmountInput] = useState('0');
  const [stockOptions, setStockOptions] = useState<Array<{symbol: string, name: string}>>([]);
  const [error, setError] = useState<string | null>(null);
  const [filterText, setFilterText] = useState('');

  useEffect(() => {
    // Fetch available stocks from the API
    const fetchStocks = async () => {
      try {
        const marketData = await marketService.getMarketData();
        const stocks = marketData.stocks.map(stock => ({
          symbol: stock.code,
          name: stock.name || stock.code
        }));
        
        // Sort stocks alphabetically by company name
        stocks.sort((a, b) => a.name.localeCompare(b.name));
        setStockOptions(stocks);
      } catch (error) {
        console.error('Error fetching stocks:', error);
        setError('Failed to load available stocks. Please try again.');
      }
    };
    
    fetchStocks();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name === 'amount') {
      setAmountInput(value);
      const parsedValue = parseFloat(value);
      setFormData(prev => ({
        ...prev,
        amount: isNaN(parsedValue) ? 0 : parsedValue
      }));
    } else if (name === 'company') {
      setFormData(prev => ({
        ...prev,
        company: value
      }));
    } else if (name === 'filterText') {
      setFilterText(value.toLowerCase());
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.amount <= 0) {
      setError('Amount must be greater than 0');
      return;
    }
    
    if (formData.amount > availableFunds) {
      setError(`Insufficient funds. Available: PKR ${availableFunds.toLocaleString()}`);
      return;
    }
    
    setError(null);
    onSubmit(formData);
  };

  // Filter stocks based on search text
  const filteredStocks = filterText 
    ? stockOptions.filter(stock => 
        stock.name.toLowerCase().includes(filterText) || 
        stock.symbol.toLowerCase().includes(filterText))
    : stockOptions;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}
      
      <div className="form-group">
        <label htmlFor="filterText" className="block text-sm font-medium mb-1">
          Search Company
        </label>
        <input
          type="text"
          id="filterText"
          name="filterText"
          value={filterText}
          onChange={handleChange}
          placeholder="Type to search companies..."
          className="input w-full mb-2"
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="company" className="block text-sm font-medium mb-1">
          Company / Ticker
        </label>
        <select
          id="company"
          name="company"
          value={formData.company}
          onChange={handleChange}
          className="input w-full"
          required
          size={5}
        >
          <option value="">Select a company</option>
          {filteredStocks.map(stock => (
            <option key={stock.symbol} value={stock.symbol}>
              {stock.name} ({stock.symbol})
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="amount" className="block text-sm font-medium mb-1">
          Amount to Invest (PKR)
        </label>
        <input
          type="number"
          id="amount"
          name="amount"
          value={amountInput}
          onChange={handleChange}
          className="input w-full"
          min="1"
          max={availableFunds}
          required
        />
        <p className="text-sm text-gray-500 mt-1">
          Available funds: PKR {availableFunds.toLocaleString()}
        </p>
      </div>

      <button 
        type="submit" 
        className="btn-primary w-full"
        disabled={formData.amount <= 0 || formData.amount > availableFunds || !formData.company}
      >
        Buy Stock
      </button>
    </form>
  );
};

export default BuyStockForm;