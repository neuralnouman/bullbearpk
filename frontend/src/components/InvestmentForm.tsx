import React, { useState } from 'react';
import { RISK_LEVELS, TIME_HORIZONS, PSX_SECTORS } from '../constants';

interface InvestmentFormProps {
  onSubmit: (formData: InvestmentFormData) => void;
  initialData?: Partial<InvestmentFormData>;
}

export interface InvestmentFormData {
  budget: number;
  sector: string;
  risk_appetite: string;
  time_horizon: string;
  target_profit: number;
}

const InvestmentForm: React.FC<InvestmentFormProps> = ({ onSubmit, initialData }) => {
  const [formData, setFormData] = useState<InvestmentFormData>({
    budget: initialData?.budget || 10000,
    sector: initialData?.sector || '',
    risk_appetite: initialData?.risk_appetite || RISK_LEVELS.MEDIUM,
    time_horizon: initialData?.time_horizon || TIME_HORIZONS.MEDIUM,
    target_profit: initialData?.target_profit || 15,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'budget' || name === 'target_profit' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="form-group">
        <label htmlFor="budget" className="block text-sm font-medium mb-1">
          Investment Budget (PKR)
        </label>
        <input
          type="number"
          id="budget"
          name="budget"
          value={formData.budget}
          onChange={handleChange}
          className="input w-full"
          min="1000"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="sector" className="block text-sm font-medium mb-1">
          Preferred Sector
        </label>
        <select
          id="sector"
          name="sector"
          value={formData.sector}
          onChange={handleChange}
          className="input w-full"
          required
        >
          <option value="">Select a sector</option>
          {PSX_SECTORS.map(sector => (
            <option key={sector} value={sector}>
              {sector}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="risk_appetite" className="block text-sm font-medium mb-1">
          Risk Appetite
        </label>
        <select
          id="risk_appetite"
          name="risk_appetite"
          value={formData.risk_appetite}
          onChange={handleChange}
          className="input w-full"
          required
        >
          <option value={RISK_LEVELS.LOW}>Low</option>
          <option value={RISK_LEVELS.MEDIUM}>Medium</option>
          <option value={RISK_LEVELS.HIGH}>High</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="time_horizon" className="block text-sm font-medium mb-1">
          Time Horizon
        </label>
        <select
          id="time_horizon"
          name="time_horizon"
          value={formData.time_horizon}
          onChange={handleChange}
          className="input w-full"
          required
        >
          <option value={TIME_HORIZONS.SHORT}>Short-term (1-6 months)</option>
          <option value={TIME_HORIZONS.MEDIUM}>Medium-term (6 months - 2 years)</option>
          <option value={TIME_HORIZONS.LONG}>Long-term (2+ years)</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="target_profit" className="block text-sm font-medium mb-1">
          Target Profit (%)
        </label>
        <input
          type="number"
          id="target_profit"
          name="target_profit"
          value={formData.target_profit}
          onChange={handleChange}
          className="input w-full"
          min="1"
          max="100"
          required
        />
      </div>

      <button type="submit" className="btn-primary w-full">
        Submit
      </button>
    </form>
  );
};

export default InvestmentForm;