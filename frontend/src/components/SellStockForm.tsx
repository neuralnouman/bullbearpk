import React, { useState } from 'react';
import { Investment } from '../types';

interface SellStockFormProps {
  onSubmit: (formData: SellStockFormData) => void;
  userInvestments: Investment[];
}

export interface SellStockFormData {
  investmentId: string;
  quantity: number;
}

const SellStockForm: React.FC<SellStockFormProps> = ({ onSubmit, userInvestments }) => {
  const [formData, setFormData] = useState<SellStockFormData>({
    investmentId: '',
    quantity: 1,
  });
  const [error, setError] = useState<string | null>(null);
  
  const selectedInvestment = userInvestments.find(inv => inv.id === formData.investmentId);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    if (name === 'investmentId') {
      const investment = userInvestments.find(inv => inv.id === value);
      setFormData({
        investmentId: value,
        quantity: investment ? 1 : 0,
      });
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: name === 'quantity' ? parseInt(value, 10) : value
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedInvestment) {
      setError('Please select a stock to sell');
      return;
    }
    
    if (formData.quantity <= 0) {
      setError('Quantity must be greater than 0');
      return;
    }
    
    if (formData.quantity > selectedInvestment.quantity) {
      setError(`You only have ${selectedInvestment.quantity} shares to sell`);
      return;
    }
    
    setError(null);
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          {error}
        </div>
      )}
      
      <div className="form-group">
        <label htmlFor="investmentId" className="block text-sm font-medium mb-1">
          Stock to Sell
        </label>
        <select
          id="investmentId"
          name="investmentId"
          value={formData.investmentId}
          onChange={handleChange}
          className="input w-full"
          required
        >
          <option value="">Select a stock</option>
          {userInvestments.map(investment => (
            <option key={investment.id} value={investment.id}>
              {investment.stockSymbol} - {investment.companyName} ({investment.quantity} shares)
            </option>
          ))}
        </select>
      </div>

      {selectedInvestment && (
        <div className="form-group">
          <label htmlFor="quantity" className="block text-sm font-medium mb-1">
            Quantity to Sell
          </label>
          <input
            type="number"
            id="quantity"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            className="input w-full"
            min="1"
            max={selectedInvestment.quantity}
            required
          />
          <p className="text-sm text-gray-500 mt-1">
            Current value: PKR {(selectedInvestment.currentPrice * formData.quantity).toLocaleString()}
          </p>
        </div>
      )}

      <button 
        type="submit" 
        className="btn-primary w-full"
        disabled={!selectedInvestment || formData.quantity <= 0 || formData.quantity > (selectedInvestment?.quantity || 0)}
      >
        Sell Stock
      </button>
    </form>
  );
};

export default SellStockForm;