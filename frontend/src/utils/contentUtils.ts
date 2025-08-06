/**
 * Content utility functions for cleaning and formatting text
 */

/**
 * Clean HTML content and extract readable text
 */
export const cleanHtmlContent = (htmlContent: string): string => {
  if (!htmlContent) return '';
  
  // Remove HTML tags but preserve line breaks
  let cleaned = htmlContent
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<p[^>]*>/gi, '')
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
  
  // Clean up extra whitespace
  cleaned = cleaned
    .replace(/\n\s*\n/g, '\n')
    .replace(/\s+/g, ' ')
    .trim();
  
  return cleaned;
};

/**
 * Extract title from HTML content
 */
export const extractTitleFromContent = (content: string): string => {
  if (!content) return '';
  
  const cleaned = cleanHtmlContent(content);
  
  // Try to extract title from link text
  const linkMatch = cleaned.match(/<a[^>]*>([^<]+)<\/a>/);
  if (linkMatch) {
    return linkMatch[1].trim();
  }
  
  // Fallback to first line
  const lines = cleaned.split('\n');
  return lines[0] || '';
};

/**
 * Extract summary from HTML content
 */
export const extractSummaryFromContent = (content: string): string => {
  if (!content) return '';
  
  const cleaned = cleanHtmlContent(content);
  
  // Remove the title part if it's a link
  let summary = cleaned.replace(/<a[^>]*>([^<]+)<\/a>/, '');
  
  // Clean up and get first few sentences
  summary = summary
    .replace(/\n/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  
  // Limit to 150 characters
  if (summary.length > 150) {
    summary = summary.substring(0, 150) + '...';
  }
  
  return summary;
};

/**
 * Format company name for display
 */
export const formatCompanyName = (companyCode: string): string => {
  if (!companyCode) return '';
  
  // Convert code to readable name
  const companyNames: Record<string, string> = {
    'HICL': 'Hinopak Motors Ltd.',
    'HIFA': 'Hinopak Motors Ltd.',
    'HINO': 'Hinopak Motors Ltd.',
    'HINOON': 'Hinopak Motors Ltd.',
    'HIRAT': 'Hinopak Motors Ltd.',
    'MDTL': 'Media Times Ltd.',
    'RUBY': 'Ruby Textile Mills Ltd.',
    'TATM': 'Tata Textile Mills Ltd.',
    'JSIL': 'JS Investment Ltd.',
    'JKSM': 'J.K. Spinning Mills Ltd.'
  };
  
  return companyNames[companyCode] || companyCode;
};

/**
 * Format source name for display
 */
export const formatSourceName = (source: string): string => {
  if (!source) return 'Unknown';
  
  const sourceNames: Record<string, string> = {
    'Google News': 'Google News',
    'Profit': 'Profit Magazine',
    'Business Recorder': 'Business Recorder',
    'Dawn': 'Dawn News',
    'Tribune': 'The Tribune',
    'ProPakistani': 'ProPakistani',
    'The News': 'The News',
    'Nation': 'The Nation',
    'Financial Daily': 'Financial Daily',
    'Pakistan Today': 'Pakistan Today'
  };
  
  return sourceNames[source] || source;
}; 