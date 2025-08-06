/**
 * Portfolio Utility Functions
 * ==========================
 * 
 * Utility functions for portfolio management and data processing.
 */

/**
 * Generate a unique key for portfolio items
 * @param item - The portfolio item (investment, sector, etc.)
 * @param index - The index in the array
 * @param prefix - Optional prefix for the key
 * @returns A unique key string
 */
export const generateUniqueKey = (
  item: any, 
  index: number, 
  prefix: string = 'item'
): string => {
  const id = item.id || item.stockSymbol || item.sector || 'unknown';
  const timestamp = item.purchaseDate || item.createdAt || Date.now();
  return `${prefix}_${id}_${timestamp}_${index}`;
};

/**
 * Ensure portfolio investments have unique keys
 * @param investments - Array of investment objects
 * @returns Array with unique keys added
 */
export const addUniqueKeysToInvestments = (investments: any[]): any[] => {
  return investments.map((investment, index) => ({
    ...investment,
    uniqueKey: generateUniqueKey(investment, index, 'inv')
  }));
};

/**
 * Ensure sector allocation items have unique keys
 * @param allocation - Array of sector allocation objects
 * @returns Array with unique keys added
 */
export const addUniqueKeysToAllocation = (allocation: any[]): any[] => {
  return allocation.map((sector, index) => ({
    ...sector,
    uniqueKey: generateUniqueKey(sector, index, 'sector')
  }));
};

/**
 * Validate portfolio data structure
 * @param portfolio - Portfolio object
 * @returns Validation result
 */
export const validatePortfolioData = (portfolio: any): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  if (!portfolio) {
    errors.push('Portfolio data is null or undefined');
    return { isValid: false, errors };
  }
  
  if (!Array.isArray(portfolio.investments)) {
    errors.push('Investments should be an array');
  }
  
  if (portfolio.investments) {
    portfolio.investments.forEach((inv: any, index: number) => {
      if (!inv.stockSymbol) {
        errors.push(`Investment ${index} missing stockSymbol`);
      }
      if (!inv.quantity || inv.quantity <= 0) {
        errors.push(`Investment ${index} has invalid quantity`);
      }
    });
  }
  
  return { isValid: errors.length === 0, errors };
}; 