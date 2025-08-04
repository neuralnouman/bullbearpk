#!/usr/bin/env python3
"""
Advanced News Analyzer Agent for BullBearPK
===========================================

This agent is responsible for:
1. Analyzing scraped news data from news_records table
2. Performing comprehensive sentiment and impact analysis
3. Saving analysis results to news_analysis table
4. Providing robust analysis for investment decisions
"""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json
from textblob import TextBlob
from database_config import db_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsAnalysisResult:
    """Data class for news analysis results"""
    stock_code: str
    overall_sentiment: str
    sentiment_score: float
    news_count: int
    positive_news: int
    negative_news: int
    neutral_news: int
    key_events: List[str]
    risk_factors: List[str]
    opportunities: List[str]
    recommendation: str
    confidence: float
    analysis_summary: str
    analysis_timestamp: datetime
    
    def __str__(self) -> str:
        """String representation for display"""
        return f"NewsAnalysis({self.stock_code}: {self.overall_sentiment}, score={self.sentiment_score:.2f}, articles={self.news_count})"

class AdvancedNewsAnalyzer:
    """
    Advanced news analyzer for comprehensive sentiment and impact analysis
    """
    
    def __init__(self):
        # Risk and opportunity keywords for analysis
        self.risk_keywords = {
            "bankruptcy", "default", "debt", "loss", "decline", "downturn", "recession",
            "crisis", "scandal", "investigation", "penalty", "fine", "suspension",
            "delisting", "insolvency", "liquidation", "restructuring", "layoffs",
            "shutdown", "bankruptcy", "default", "fraud", "corruption", "lawsuit"
        }
        
        self.opportunity_keywords = {
            "growth", "expansion", "profit", "success", "award", "recognition",
            "partnership", "contract", "deal", "investment", "funding", "innovation",
            "technology", "digital", "efficiency", "sustainability", "merger",
            "acquisition", "ipo", "dividend", "revenue", "earnings", "profit"
        }
        
        # High impact keywords
        self.high_impact_keywords = {
            "profit", "loss", "revenue", "earnings", "dividend", "ipo", "merger",
            "acquisition", "bankruptcy", "default", "crisis", "scandal", "ceo",
            "board", "executive", "quarterly", "annual", "results", "forecast"
        }
    
    def get_news_records_for_company(self, stock_code: str) -> List[Dict]:
        """Get news records for a specific company from database"""
        try:
            query = """
            SELECT * FROM news_records 
            WHERE stock_code = %s 
            ORDER BY published_date DESC, scraped_at DESC
            """
            results = db_config.execute_query(query, (stock_code,))
            return results or []
        except Exception as e:
            logger.error(f"Error fetching news records for {stock_code}: {e}")
            return []
    
    def analyze_sentiment_advanced(self, text: str) -> Tuple[str, float]:
        """Advanced sentiment analysis using TextBlob with enhancements"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Enhanced sentiment classification
            if polarity > 0.2 and subjectivity > 0.3:
                sentiment = 'positive'
                score = polarity
            elif polarity < -0.2 and subjectivity > 0.3:
                sentiment = 'negative'
                score = abs(polarity)
            else:
                sentiment = 'neutral'
                score = 0.0
            
            return sentiment, score
        except Exception as e:
            logger.warning(f"Error in sentiment analysis: {e}")
            return 'neutral', 0.0
    
    def extract_keywords_and_impact(self, text: str) -> Tuple[List[str], List[str], List[str]]:
        """Extract keywords, risk factors, and opportunities from text"""
        try:
            text_lower = text.lower()
            keywords = []
            risk_factors = []
            opportunities = []
            
            # Extract risk factors
            for keyword in self.risk_keywords:
                if keyword in text_lower:
                    risk_factors.append(keyword)
            
            # Extract opportunities
            for keyword in self.opportunity_keywords:
                if keyword in text_lower:
                    opportunities.append(keyword)
            
            # Extract high impact keywords
            for keyword in self.high_impact_keywords:
                if keyword in text_lower:
                    keywords.append(keyword)
            
            return keywords, risk_factors, opportunities
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return [], [], []
    
    def analyze_news_for_company(self, news_records: List[Dict], stock_code: str) -> NewsAnalysisResult:
        """Analyze news records for a company"""
        try:
            if not news_records:
                return NewsAnalysisResult(
                    stock_code=stock_code,
                    overall_sentiment="neutral",
                    sentiment_score=0.0,
                    news_count=0,
                    positive_news=0,
                    negative_news=0,
                    neutral_news=0,
                    key_events=[],
                    risk_factors=[],
                    opportunities=[],
                    recommendation="No recent news available for analysis.",
                    confidence=0.0,
                    analysis_summary="No news data available for this company.",
                    analysis_timestamp=datetime.now()
                )
            
            # Analyze each news record
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            total_confidence = 0.0
            key_events = []
            risk_factors = []
            opportunities = []
            all_keywords = []
            
            for record in news_records:
                # Get text for analysis
                title = record.get('title', '')
                summary = record.get('summary', '')
                text = f"{title} {summary}"
                
                # Analyze sentiment
                sentiment, score = self.analyze_sentiment_advanced(text)
                sentiment_counts[sentiment] += 1
                
                # Get confidence from record and convert to float
                confidence = float(record.get('confidence_score', 0.5))
                total_confidence += confidence
                
                # Extract keywords and impact
                keywords, risks, opps = self.extract_keywords_and_impact(text)
                all_keywords.extend(keywords)
                
                # Check for high impact news
                financial_impact = record.get('financial_impact', 'low')
                if financial_impact == 'high':
                    key_events.append(title)
                
                # Add risk factors and opportunities
                risk_factors.extend(risks)
                opportunities.extend(opps)
            
            # Calculate overall sentiment
            total_articles = len(news_records)
            positive_ratio = sentiment_counts["positive"] / total_articles
            negative_ratio = sentiment_counts["negative"] / total_articles
            
            if positive_ratio > negative_ratio and positive_ratio > 0.4:
                overall_sentiment = "bullish"
                sentiment_score = float(positive_ratio)
            elif negative_ratio > positive_ratio and negative_ratio > 0.4:
                overall_sentiment = "bearish"
                sentiment_score = float(-negative_ratio)
            else:
                overall_sentiment = "neutral"
                sentiment_score = 0.0
            
            # Calculate average confidence
            avg_confidence = total_confidence / total_articles if total_articles > 0 else 0.0
            
            # Remove duplicates and limit lists
            key_events = list(set(key_events))[:5]
            risk_factors = list(set(risk_factors))[:5]
            opportunities = list(set(opportunities))[:5]
            
            # Generate recommendation
            recommendation, confidence = self._generate_recommendation(
                overall_sentiment, sentiment_score, sentiment_counts,
                risk_factors, opportunities, avg_confidence
            )
            
            # Generate analysis summary
            analysis_summary = self._generate_analysis_summary(
                stock_code, news_records, overall_sentiment, sentiment_counts,
                key_events, risk_factors, opportunities
            )
            
            return NewsAnalysisResult(
                stock_code=stock_code,
                overall_sentiment=overall_sentiment,
                sentiment_score=sentiment_score,
                news_count=total_articles,
                positive_news=sentiment_counts["positive"],
                negative_news=sentiment_counts["negative"],
                neutral_news=sentiment_counts["neutral"],
                key_events=key_events,
                risk_factors=risk_factors,
                opportunities=opportunities,
                recommendation=recommendation,
                confidence=confidence,
                analysis_summary=analysis_summary,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing news for {stock_code}: {e}")
            return NewsAnalysisResult(
                stock_code=stock_code,
                overall_sentiment="neutral",
                sentiment_score=0.0,
                news_count=0,
                positive_news=0,
                negative_news=0,
                neutral_news=0,
                key_events=[],
                risk_factors=[],
                opportunities=[],
                recommendation=f"Error occurred during analysis: {str(e)}",
                confidence=0.0,
                analysis_summary=f"Error analyzing {stock_code}: {str(e)}",
                analysis_timestamp=datetime.now()
            )
    
    def _generate_recommendation(self, overall_sentiment: str, sentiment_score: float,
                                sentiment_counts: Dict, risk_factors: List[str],
                                opportunities: List[str], avg_confidence: float) -> Tuple[str, float]:
        """Generate investment recommendation based on news analysis"""
        
        if overall_sentiment == "bullish":
            if sentiment_score > 0.7 and len(opportunities) > len(risk_factors):
                recommendation = "Strong buy recommendation based on positive news sentiment and growth opportunities."
                confidence = min(0.9, avg_confidence + 0.2)
            else:
                recommendation = "Buy recommendation based on positive news sentiment."
                confidence = min(0.8, avg_confidence + 0.1)
        
        elif overall_sentiment == "bearish":
            if sentiment_score < -0.7 and len(risk_factors) > len(opportunities):
                recommendation = "Strong sell recommendation due to negative news sentiment and risk factors."
                confidence = min(0.9, avg_confidence + 0.2)
            else:
                recommendation = "Sell recommendation based on negative news sentiment."
                confidence = min(0.8, avg_confidence + 0.1)
        
        else:  # neutral
            if len(opportunities) > len(risk_factors):
                recommendation = "Hold with potential for growth based on mixed news sentiment."
                confidence = min(0.7, avg_confidence)
            else:
                recommendation = "Hold with caution due to mixed news sentiment."
                confidence = min(0.6, avg_confidence)
        
        return recommendation, confidence
    
    def _generate_analysis_summary(self, stock_code: str, news_records: List[Dict],
                                 overall_sentiment: str, sentiment_counts: Dict,
                                 key_events: List[str], risk_factors: List[str],
                                 opportunities: List[str]) -> str:
        """Generate comprehensive analysis summary"""
        
        summary_parts = [
            f"Advanced news analysis for {stock_code}:",
            f"Analyzed {len(news_records)} news articles",
            f"Overall sentiment: {overall_sentiment}",
            f"News distribution: {sentiment_counts['positive']} positive, {sentiment_counts['negative']} negative, {sentiment_counts['neutral']} neutral"
        ]
        
        if key_events:
            summary_parts.append(f"Key high-impact events: {len(key_events)}")
        
        if risk_factors:
            summary_parts.append(f"Risk factors identified: {len(risk_factors)}")
        
        if opportunities:
            summary_parts.append(f"Growth opportunities: {len(opportunities)}")
        
        return " | ".join(summary_parts)
    
    def save_analysis_to_database(self, analysis: NewsAnalysisResult) -> bool:
        """Save news analysis results to database"""
        try:
            # Clear previous analysis for this stock
            clear_query = "DELETE FROM news_analysis WHERE stock_code = %s"
            db_config.execute_query(clear_query, (analysis.stock_code,))
            
            # Insert new analysis
            query = """
            INSERT INTO news_analysis (
                stock_code, overall_sentiment, sentiment_score, news_count,
                positive_news, negative_news, neutral_news, key_events,
                risk_factors, opportunities, recommendation, confidence, analysis_summary
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            params = (
                analysis.stock_code,
                analysis.overall_sentiment,
                analysis.sentiment_score,
                analysis.news_count,
                analysis.positive_news,
                analysis.negative_news,
                analysis.neutral_news,
                json.dumps(analysis.key_events),
                json.dumps(analysis.risk_factors),
                json.dumps(analysis.opportunities),
                analysis.recommendation,
                analysis.confidence,
                analysis.analysis_summary
            )
            
            db_config.execute_query(query, params)
            logger.info(f"Successfully saved news analysis for {analysis.stock_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving news analysis for {analysis.stock_code}: {e}")
            return False
    
    async def analyze_company_news(self, stock_code: str) -> NewsAnalysisResult:
        """Analyze news for a specific company"""
        try:
            logger.info(f"Starting news analysis for {stock_code}")
            
            # Get news records from database
            news_records = self.get_news_records_for_company(stock_code)
            
            if not news_records:
                logger.warning(f"No news records found for {stock_code}")
                return NewsAnalysisResult(
                    stock_code=stock_code,
                    overall_sentiment="neutral",
                    sentiment_score=0.0,
                    news_count=0,
                    positive_news=0,
                    negative_news=0,
                    neutral_news=0,
                    key_events=[],
                    risk_factors=[],
                    opportunities=[],
                    recommendation="No recent news available for analysis.",
                    confidence=0.0,
                    analysis_summary="No news data available for this company.",
                    analysis_timestamp=datetime.now()
                )
            
            # Perform analysis
            analysis = self.analyze_news_for_company(news_records, stock_code)
            
            # Save to database
            self.save_analysis_to_database(analysis)
            
            logger.info(f"Completed news analysis for {stock_code}: {analysis.overall_sentiment} sentiment, {analysis.news_count} articles")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing news for {stock_code}: {e}")
            return NewsAnalysisResult(
                stock_code=stock_code,
                overall_sentiment="neutral",
                sentiment_score=0.0,
                news_count=0,
                positive_news=0,
                negative_news=0,
                neutral_news=0,
                key_events=[],
                risk_factors=[],
                opportunities=[],
                recommendation=f"Error occurred during analysis: {str(e)}",
                confidence=0.0,
                analysis_summary=f"Error analyzing {stock_code}: {str(e)}",
                analysis_timestamp=datetime.now()
            )
    
    async def analyze_multiple_companies(self, stock_codes: List[str]) -> Dict[str, NewsAnalysisResult]:
        """Analyze news for multiple companies concurrently"""
        try:
            logger.info(f"Starting news analysis for {len(stock_codes)} companies: {stock_codes}")
            
            # Analyze all companies concurrently
            tasks = []
            for stock_code in stock_codes:
                task = self.analyze_company_news(stock_code)
                tasks.append((stock_code, task))
            
            # Execute all analysis tasks
            results = {}
            for stock_code, task in tasks:
                try:
                    analysis = await task
                    results[stock_code] = analysis
                except Exception as e:
                    logger.error(f"Error analyzing news for {stock_code}: {e}")
                    # Create error result
                    results[stock_code] = NewsAnalysisResult(
                        stock_code=stock_code,
                        overall_sentiment="neutral",
                        sentiment_score=0.0,
                        news_count=0,
                        positive_news=0,
                        negative_news=0,
                        neutral_news=0,
                        key_events=[],
                        risk_factors=[],
                        opportunities=[],
                        recommendation=f"Error occurred during analysis: {str(e)}",
                        confidence=0.0,
                        analysis_summary=f"Error analyzing {stock_code}: {str(e)}",
                        analysis_timestamp=datetime.now()
                    )
            
            logger.info(f"Completed news analysis for {len(results)} companies")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch news analysis: {e}")
            return {}

class NewsAnalyzerNode:
    """LangGraph node for news analysis"""
    
    def __init__(self):
        self.analyzer = AdvancedNewsAnalyzer()
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run news analysis for companies with scraped news"""
        try:
            logger.info("Starting news analysis node...")
            
            # Get companies that have scraped news
            news_records = state.get('news_records', {})
            companies_with_news = list(news_records.keys())
            
            if not companies_with_news:
                logger.warning("No companies with scraped news found for analysis")
                return {
                    **state,
                    'news_analysis': {},
                    'news_analysis_summary': {
                        'companies_analyzed': 0,
                        'total_articles_analyzed': 0,
                        'status': 'no_news_data'
                    }
                }
            
            logger.info(f"Found {len(companies_with_news)} companies with news data: {companies_with_news}")
            
            # Analyze news for all companies
            analysis_results = await self.analyzer.analyze_multiple_companies(companies_with_news)
            
            # Create summary
            total_articles = sum(result.news_count for result in analysis_results.values())
            companies_analyzed = len(analysis_results)
            
            analysis_summary = {
                'companies_analyzed': companies_analyzed,
                'total_articles_analyzed': total_articles,
                'companies': list(analysis_results.keys()),
                'sentiment_distribution': {
                    'bullish': len([r for r in analysis_results.values() if r.overall_sentiment == 'bullish']),
                    'bearish': len([r for r in analysis_results.values() if r.overall_sentiment == 'bearish']),
                    'neutral': len([r for r in analysis_results.values() if r.overall_sentiment == 'neutral'])
                },
                'status': 'completed'
            }
            
            logger.info(f"News analysis completed: {companies_analyzed} companies, {total_articles} articles analyzed")
            
            return {
                **state,
                'news_analysis': analysis_results,
                'news_analysis_summary': analysis_summary
            }
            
        except Exception as e:
            logger.error(f"Error in news analysis node: {e}")
            return {
                **state,
                'news_analysis': {},
                'news_analysis_summary': {
                    'companies_analyzed': 0,
                    'total_articles_analyzed': 0,
                    'status': 'error',
                    'error': str(e)
                }
            }

# Global instance for LangGraph
news_analyzer_node = NewsAnalyzerNode() 