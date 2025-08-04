#!/usr/bin/env python3
"""
Advanced News Scraper Agent for BullBearPK
===========================================

This agent is responsible for:
1. Taking top 5 companies from stock analysis results
2. Performing batch scraping of news for these companies
3. Storing raw news data in news_records table
4. Using advanced scraping techniques and multiple sources
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any, Set
from dataclasses import dataclass
from urllib.parse import quote_plus, urljoin
import json
import re
from textblob import TextBlob
import hashlib
import logging
import time
from database_config import db_config
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Data class for scraped news articles"""
    title: str
    summary: str
    link: str
    published_date: Optional[datetime]
    source: str
    content_hash: str
    sentiment: str = 'neutral'
    sentiment_score: float = 0.0
    keywords: List[str] = None
    company_mentions: List[str] = None
    financial_impact: str = 'neutral'
    confidence_score: float = 0.5

class AdvancedNewsScraper:
    """
    Advanced news scraper with batch processing capabilities
    """
    
    def __init__(self):
        self.session = None
        self.companies_data = self._load_companies_data()
        self.scraping_semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        # Advanced RSS feeds for Pakistani financial news
        self.rss_feeds = [
            "https://profit.pakistantoday.com.pk/feed/",
            "https://www.brecorder.com/rss/business",
            "https://tribune.com.pk/feed/business",
            "https://propakistani.pk/feed/",
            "https://www.dawn.com/feeds/business",
            "https://www.thenews.com.pk/rss/feed/business",
            "https://www.nation.com.pk/rss/business",
            "https://www.businessrecorder.com/rss/",
            "https://www.financialdaily.com.pk/rss/",
            "https://www.pakistantoday.com.pk/category/business/feed/"
        ]
        
        # Google News search endpoints
        self.google_news_urls = [
            "https://news.google.com/rss/search?q={}&hl=en-PK&gl=PK&ceid=PK:en",
            "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-PK&gl=PK&ceid=PK:en"
        ]
        
        # Financial keywords for relevance filtering
        self.financial_keywords = {
            "profit", "loss", "stock", "shares", "dividend", "revenue", "investment",
            "shutdown", "layoffs", "earning", "merger", "acquisition", "forecast", 
            "ipo", "psx", "market", "valuation", "debt", "expansion", "trading", 
            "capital", "quarterly", "annual", "results", "performance", "growth",
            "financial", "business", "economy", "banking", "insurance", "real estate"
        }
        
        # Risk and opportunity keywords
        self.risk_keywords = {
            "bankruptcy", "default", "debt", "loss", "decline", "downturn", "recession",
            "crisis", "scandal", "investigation", "penalty", "fine", "suspension",
            "delisting", "insolvency", "liquidation", "restructuring"
        }
        
        self.opportunity_keywords = {
            "growth", "expansion", "profit", "success", "award", "recognition",
            "partnership", "contract", "deal", "investment", "funding", "innovation",
            "technology", "digital", "efficiency", "sustainability"
        } 
    
    def _load_companies_data(self) -> Dict:
        """Load companies data with symbols and names"""
        try:
            # Get companies from database
            companies = db_config.get_latest_stocks(100)
            companies_dict = {}
            
            for company in companies:
                symbol = company.get('code', '').upper()
                name = company.get('name', '')
                sector = company.get('sector', '')
                
                if symbol and name:
                    companies_dict[symbol] = {
                        'name': name,
                        'sector': sector,
                        'variants': self._generate_company_variants(symbol, name)
                    }
            
            logger.info(f"Loaded {len(companies_dict)} companies for news scraping")
            return companies_dict
            
        except Exception as e:
            logger.error(f"Error loading companies data: {e}")
            return {}
    
    def _generate_company_variants(self, symbol: str, name: str) -> List[str]:
        """Generate search variants for a company"""
        variants = [symbol, name]
        
        # Add common variations
        if ' ' in name:
            words = name.split()
            variants.extend(words)
            variants.append(' '.join(words[:2]))  # First two words
        
        # Add sector-specific terms
        if 'bank' in name.lower():
            variants.append('bank')
        elif 'oil' in name.lower() or 'gas' in name.lower():
            variants.append('energy')
        elif 'telecom' in name.lower():
            variants.append('telecom')
        
        return list(set(variants))  # Remove duplicates
    
    async def initialize_session(self):
        """Initialize aiohttp session with optimized settings"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _calculate_content_hash(self, title: str, link: str) -> str:
        """Calculate hash for content deduplication"""
        content = f"{title}:{link}".lower().strip()
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _analyze_sentiment_fast(self, text: str) -> Tuple[str, float]:
        """Fast sentiment analysis using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return sentiment, abs(polarity)
        except Exception as e:
            logger.warning(f"Error in sentiment analysis: {e}")
            return 'neutral', 0.0
    
    def _extract_keywords(self, text: str, company_symbol: str) -> List[str]:
        """Extract relevant keywords from text"""
        try:
            # Convert to lowercase for matching
            text_lower = text.lower()
            keywords = []
            
            # Check for financial keywords
            for keyword in self.financial_keywords:
                if keyword in text_lower:
                    keywords.append(keyword)
            
            # Check for risk keywords
            for keyword in self.risk_keywords:
                if keyword in text_lower:
                    keywords.append(f"risk_{keyword}")
            
            # Check for opportunity keywords
            for keyword in self.opportunity_keywords:
                if keyword in text_lower:
                    keywords.append(f"opportunity_{keyword}")
            
            # Add company-specific keywords
            if company_symbol.lower() in text_lower:
                keywords.append(f"company_{company_symbol}")
            
            return list(set(keywords))  # Remove duplicates
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return []
    
    def _assess_financial_impact(self, text: str, sentiment: str) -> str:
        """Assess financial impact of news"""
        try:
            text_lower = text.lower()
            
            # High impact indicators
            high_impact_words = {
                'profit', 'loss', 'revenue', 'earnings', 'dividend', 'ipo', 'merger',
                'acquisition', 'bankruptcy', 'default', 'crisis', 'scandal'
            }
            
            # Medium impact indicators
            medium_impact_words = {
                'expansion', 'growth', 'investment', 'partnership', 'contract',
                'technology', 'innovation', 'restructuring'
            }
            
            # Check for high impact words
            for word in high_impact_words:
                if word in text_lower:
                    return 'high'
            
            # Check for medium impact words
            for word in medium_impact_words:
                if word in text_lower:
                    return 'medium'
            
            return 'low'
            
        except Exception as e:
            logger.warning(f"Error assessing financial impact: {e}")
            return 'low' 
    
    async def _fetch_rss_news(self, company_symbol: str) -> List[NewsArticle]:
        """Fetch news from RSS feeds for a specific company"""
        articles = []
        company_variants = self.companies_data.get(company_symbol, {}).get('variants', [company_symbol])
        company_variants_set = set(company_variants)
        
        async with self.scraping_semaphore:
            try:
                # Fetch from multiple RSS feeds concurrently
                tasks = []
                for feed_url in self.rss_feeds:
                    task = self._fetch_single_rss_feed(feed_url, company_variants_set, company_symbol)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, list):
                        articles.extend(result)
                    else:
                        logger.warning(f"RSS feed error: {result}")
                
                logger.info(f"Fetched {len(articles)} RSS articles for {company_symbol}")
                return articles
                
            except Exception as e:
                logger.error(f"Error fetching RSS news for {company_symbol}: {e}")
                return []
    
    async def _fetch_single_rss_feed(self, feed_url: str, company_variants_set: Set[str], 
                                    company_symbol: str) -> List[NewsArticle]:
        """Fetch news from a single RSS feed"""
        try:
            async with self.session.get(feed_url, timeout=10) as response:
                if response.status != 200:
                    return []
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:20]:  # Limit to 20 entries per feed
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    link = entry.get('link', '')
                    
                    # Check if article mentions the company
                    text_to_check = f"{title} {summary}".lower()
                    if not any(variant.lower() in text_to_check for variant in company_variants_set):
                        continue
                    
                    # Parse published date
                    published_date = None
                    if 'published_parsed' in entry:
                        try:
                            published_date = datetime(*entry.published_parsed[:6])
                        except:
                            pass
                    
                    # Analyze sentiment
                    sentiment, sentiment_score = self._analyze_sentiment_fast(f"{title} {summary}")
                    
                    # Extract keywords
                    keywords = self._extract_keywords(f"{title} {summary}", company_symbol)
                    
                    # Assess financial impact
                    financial_impact = self._assess_financial_impact(f"{title} {summary}", sentiment)
                    
                    # Calculate content hash
                    content_hash = self._calculate_content_hash(title, link)
                    
                    article = NewsArticle(
                        title=title,
                        summary=summary,
                        link=link,
                        published_date=published_date,
                        source=feed_url,
                        content_hash=content_hash,
                        sentiment=sentiment,
                        sentiment_score=sentiment_score,
                        keywords=keywords,
                        company_mentions=[company_symbol],
                        financial_impact=financial_impact,
                        confidence_score=min(sentiment_score + 0.3, 1.0)
                    )
                    
                    articles.append(article)
                
                return articles
                
        except Exception as e:
            logger.warning(f"Failed to fetch RSS feed {feed_url}: {e}")
            return []
    
    async def _fetch_google_news(self, company_symbol: str) -> List[NewsArticle]:
        """Fetch news from Google News for a specific company"""
        articles = []
        company_name = self.companies_data.get(company_symbol, {}).get('name', company_symbol)
        
        async with self.scraping_semaphore:
            try:
                # Search for company-specific news
                search_query = f"{company_symbol} {company_name} Pakistan stock market"
                encoded_query = quote_plus(search_query)
                
                for google_url in self.google_news_urls:
                    try:
                        url = google_url.format(encoded_query)
                        async with self.session.get(url, timeout=15) as response:
                            if response.status != 200:
                                continue
                            
                            content = await response.text()
                            feed = feedparser.parse(content)
                            
                            for entry in feed.entries[:10]:  # Limit to 10 entries
                                title = entry.get('title', '')
                                summary = entry.get('summary', '')
                                link = entry.get('link', '')
                                
                                # Parse published date
                                published_date = None
                                if 'published_parsed' in entry:
                                    try:
                                        published_date = datetime(*entry.published_parsed[:6])
                                    except:
                                        pass
                                
                                # Analyze sentiment
                                sentiment, sentiment_score = self._analyze_sentiment_fast(f"{title} {summary}")
                                
                                # Extract keywords
                                keywords = self._extract_keywords(f"{title} {summary}", company_symbol)
                                
                                # Assess financial impact
                                financial_impact = self._assess_financial_impact(f"{title} {summary}", sentiment)
                                
                                # Calculate content hash
                                content_hash = self._calculate_content_hash(title, link)
                                
                                article = NewsArticle(
                                    title=title,
                                    summary=summary,
                                    link=link,
                                    published_date=published_date,
                                    source="Google News",
                                    content_hash=content_hash,
                                    sentiment=sentiment,
                                    sentiment_score=sentiment_score,
                                    keywords=keywords,
                                    company_mentions=[company_symbol],
                                    financial_impact=financial_impact,
                                    confidence_score=min(sentiment_score + 0.3, 1.0)
                                )
                                
                                articles.append(article)
                            
                    except Exception as e:
                        logger.warning(f"Failed to fetch Google News: {e}")
                        continue
                
                logger.info(f"Fetched {len(articles)} Google News articles for {company_symbol}")
                return articles
                
            except Exception as e:
                logger.error(f"Error fetching Google News for {company_symbol}: {e}")
                return []
    
    def _remove_duplicates(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on content hash"""
        seen_hashes = set()
        unique_articles = []
        
        for article in articles:
            if article.content_hash not in seen_hashes:
                seen_hashes.add(article.content_hash)
                unique_articles.append(article)
        
        return unique_articles
    
    async def scrape_company_news(self, company_symbol: str) -> List[NewsArticle]:
        """Scrape all news for a specific company"""
        try:
            await self.initialize_session()
            
            # Fetch from multiple sources concurrently
            rss_task = self._fetch_rss_news(company_symbol)
            google_task = self._fetch_google_news(company_symbol)
            
            rss_articles, google_articles = await asyncio.gather(
                rss_task, google_task, return_exceptions=True
            )
            
            # Combine and remove duplicates
            all_articles = []
            if isinstance(rss_articles, list):
                all_articles.extend(rss_articles)
            if isinstance(google_articles, list):
                all_articles.extend(google_articles)
            
            unique_articles = self._remove_duplicates(all_articles)
            
            logger.info(f"Scraped {len(unique_articles)} unique articles for {company_symbol}")
            return unique_articles
            
        except Exception as e:
            logger.error(f"Error scraping news for {company_symbol}: {e}")
            return []
    
    def save_news_to_database(self, articles: List[NewsArticle], company_symbol: str) -> bool:
        """Save scraped news articles to database"""
        try:
            if not articles:
                logger.warning(f"No articles to save for {company_symbol}")
                return True
            
            # Prepare data for batch insert
            news_data = []
            for article in articles:
                news_data.append({
                    'stock_code': company_symbol,
                    'title': article.title,
                    'summary': article.summary,
                    'link': article.link,
                    'published_date': article.published_date,
                    'source': article.source,
                    'content_hash': article.content_hash,
                    'sentiment': article.sentiment,
                    'sentiment_score': article.sentiment_score,
                    'keywords': json.dumps(article.keywords) if article.keywords else None,
                    'company_mentions': json.dumps(article.company_mentions) if article.company_mentions else None,
                    'financial_impact': article.financial_impact,
                    'confidence_score': article.confidence_score
                })
            
            # Save to database
            success_count = 0
            for data in news_data:
                try:
                    query = """
                    INSERT INTO news_records (
                        stock_code, title, summary, link, published_date, source,
                        content_hash, sentiment, sentiment_score, keywords, company_mentions,
                        financial_impact, confidence_score
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON DUPLICATE KEY UPDATE
                        sentiment = VALUES(sentiment),
                        sentiment_score = VALUES(sentiment_score),
                        keywords = VALUES(keywords),
                        financial_impact = VALUES(financial_impact),
                        confidence_score = VALUES(confidence_score)
                    """
                    
                    params = (
                        data['stock_code'], data['title'], data['summary'], data['link'],
                        data['published_date'], data['source'], data['content_hash'],
                        data['sentiment'], data['sentiment_score'], data['keywords'],
                        data['company_mentions'], data['financial_impact'], data['confidence_score']
                    )
                    
                    db_config.execute_query(query, params)
                    success_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error saving article for {company_symbol}: {e}")
                    continue
            
            logger.info(f"Successfully saved {success_count}/{len(news_data)} articles for {company_symbol}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error saving news to database for {company_symbol}: {e}")
            return False 
    
    async def scrape_top_companies_news(self, top_companies: List[Dict]) -> Dict[str, List[NewsArticle]]:
        """
        Scrape news for top 5 companies from the stock analysis results
        
        Args:
            top_companies: List of top companies from stock analysis (we'll take top 5)
        
        Returns:
            Dict mapping company symbols to their scraped news articles
        """
        try:
            # Take top 5 companies
            top_5_companies = top_companies[:5]
            company_symbols = [company.get('stock_code', company.get('code', '')) for company in top_5_companies]
            company_symbols = [symbol for symbol in company_symbols if symbol]
            
            logger.info(f"Starting batch news scraping for top 5 companies: {company_symbols}")
            
            # Clear previous news data from database
            try:
                db_config.clear_news_records()
            except Exception as e:
                logger.warning(f"Error clearing previous news data: {e}")
            
            # Initialize session
            await self.initialize_session()
            
            # Scrape news for all companies concurrently
            scraping_tasks = []
            for symbol in company_symbols:
                task = self.scrape_company_news(symbol)
                scraping_tasks.append((symbol, task))
            
            # Execute all scraping tasks
            results = {}
            for symbol, task in scraping_tasks:
                try:
                    articles = await task
                    results[symbol] = articles
                    
                    # Save to database
                    if articles:
                        self.save_news_to_database(articles, symbol)
                    
                except Exception as e:
                    logger.error(f"Error scraping news for {symbol}: {e}")
                    results[symbol] = []
            
            # Close session
            await self.close_session()
            
            # Summary
            total_articles = sum(len(articles) for articles in results.values())
            logger.info(f"Batch scraping completed. Total articles scraped: {total_articles}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch news scraping: {e}")
            await self.close_session()
            return {}

class NewsScraperNode:
    """LangGraph node for news scraping"""
    
    def __init__(self):
        self.scraper = AdvancedNewsScraper()
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run news scraping for top companies"""
        try:
            logger.info("Starting news scraping node...")
            
            # Get top performers from stock analysis
            top_performers = state.get('top_performers', [])
            
            if not top_performers:
                logger.warning("No top performers found for news scraping")
                return {
                    **state,
                    'news_records': {},
                    'news_scraping_summary': {
                        'companies_scraped': 0,
                        'total_articles': 0,
                        'status': 'no_companies_found'
                    }
                }
            
            logger.info(f"Found {len(top_performers)} companies for news scraping: {[c.get('stock_code', 'Unknown') for c in top_performers]}")
            
            # Scrape news for top 5 companies
            news_results = await self.scraper.scrape_top_companies_news(top_performers)
            
            # Create summary
            total_articles = sum(len(articles) for articles in news_results.values())
            companies_scraped = len(news_results)
            
            scraping_summary = {
                'companies_scraped': companies_scraped,
                'total_articles': total_articles,
                'companies': list(news_results.keys()),
                'articles_per_company': {symbol: len(articles) for symbol, articles in news_results.items()},
                'status': 'completed'
            }
            
            logger.info(f"News scraping completed: {companies_scraped} companies, {total_articles} articles")
            
            return {
                **state,
                'news_records': news_results,
                'news_scraping_summary': scraping_summary
            }
            
        except Exception as e:
            logger.error(f"Error in news scraping node: {e}")
            return {
                **state,
                'news_records': {},
                'news_scraping_summary': {
                    'companies_scraped': 0,
                    'total_articles': 0,
                    'status': 'error',
                    'error': str(e)
                }
            }

# Global instance for LangGraph
news_scraper_node = NewsScraperNode() 