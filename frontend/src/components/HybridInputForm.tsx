import React, { useState } from 'react';

interface Props {
  onSubmit: (form: any) => void;
}

export default function HybridInputForm({ onSubmit }: Props) {
  const [form, setForm] = useState({
    budget: '',
    sector_preference: '',
    risk_tolerance: '',
    time_horizon: '',
    target_profit: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  return (
    <form
      className="space-y-2"
      onSubmit={e => {
        e.preventDefault();
        onSubmit(form);
      }}
    >
      <input name="budget" placeholder="Budget (e.g. 10000 PKR)" value={form.budget} onChange={handleChange} />
      <input name="sector_preference" placeholder="Sector (e.g. Banking)" value={form.sector_preference} onChange={handleChange} />
      <input name="risk_tolerance" placeholder="Risk (Low/Medium/High)" value={form.risk_tolerance} onChange={handleChange} />
      <input name="time_horizon" placeholder="Time Horizon (e.g. 6 months)" value={form.time_horizon} onChange={handleChange} />
      <input name="target_profit" placeholder="Target Profit (e.g. 15%)" value={form.target_profit} onChange={handleChange} />
      <button type="submit" className="btn-primary">Submit Details</button>
    </form>
  );
}
