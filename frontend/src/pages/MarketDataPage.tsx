import React from 'react';
import { motion } from 'framer-motion';
import MainLayout from '../components/MainLayout';
import MarketData from '../components/MarketData';

const MarketDataPage: React.FC = () => {
  return (
    <MainLayout>
      <div className="p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="max-w-7xl mx-auto"
        >
          <MarketData />
        </motion.div>
      </div>
    </MainLayout>
  );
};

export default MarketDataPage;