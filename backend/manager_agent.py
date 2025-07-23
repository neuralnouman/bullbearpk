import base64
from io import BytesIO
import matplotlib
# Set non-interactive backend to avoid Tkinter threading issues
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from agents.fin_scraper import scrape_stocks_tool
from agents.stock_agent import StockAnalysisAgent, StockData
from agents.agent_c_news_scraper import AgentCNewsScraper
from agents.agent_d_sentiment import AgentDSentimentAnalyzer
from agents.agent_e_portfolio_updater import AgentEPortfolioUpdater
from agents.agent_g_risk_profiler import AgentGRiskProfiler
from agents.agent_h_history import AgentHUserHistory
import json
from agents.input_parser import parse_hybrid_input
from typing import Dict, List, Optional, Union
from datetime import datetime

# Configuration for dynamic behavior
CONFIG = {
    "stock_analysis": {
        "max_stocks_to_analyze": 10,
        "analysis_metrics": ["momentum", "volatility", "trend"],
        "sort_strategy": "momentum",  # Can be momentum, volatility, or trend
    },
    "recommendation": {
        "max_recommendations": 5,
        "allocation_strategy": {
            "low": {"top_percent": 0.25, "diversification": 0.7},
            "moderate": {"top_percent": 0.33, "diversification": 0.5},
            "high": {"top_percent": 0.5, "diversification": 0.3},
        },
        "factors": ["sentiment", "risk_profile", "user_history"],
    },
    "visualization": {
        "chart_type": "pie",  # Can be pie, bar, etc.
        "display_percent": True,
    }
}

# Instantiate agents dynamically
agents = {
    "stock_analyzer": StockAnalysisAgent(),
    "news_scraper": AgentCNewsScraper(),
    "sentiment_analyzer": AgentDSentimentAnalyzer(),
    "portfolio_updater": AgentEPortfolioUpdater(),
    "risk_profiler": AgentGRiskProfiler(),
    "user_history": AgentHUserHistory(),
}

def generate_chart(data: Dict, chart_type: str = "pie", **kwargs) -> str:
    """Generate visualization dynamically based on config"""
    # Create a new figure with explicit non-interactive backend
    with plt.ioff():
        fig, ax = plt.subplots()
        
        if chart_type == "pie":
            ax.pie(list(data.values()), labels=list(data.keys()), autopct='%1.1f%%' if kwargs.get('display_percent', True) else None)
        elif chart_type == "bar":
            ax.bar(list(data.keys()), list(data.values()))
            ax.set_xticklabels(list(data.keys()), rotation=45)
        
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)  # Explicitly close the figure
        buf.seek(0)
        
    # Return base64 encoded image
    return base64.b64encode(buf.read()).decode('utf-8')

def analyze_stocks(stock_data: List[Dict], config: Dict) -> List[Dict]:
    """Dynamic stock analysis based on config"""
    analyses = []
    max_stocks = config["stock_analysis"]["max_stocks_to_analyze"]
    
    for stock in stock_data[:max_stocks]:
        analysis = agents["stock_analyzer"].analyzer.comprehensive_analysis(stock['code'])
        if analysis:
            # Add sector information to analysis
            analysis['sector'] = stock.get('sector', '')
            
            # Filter analysis to only include requested metrics if needed
            metrics = config["stock_analysis"]["analysis_metrics"]
            analyses.append({
                "code": stock['code'],
                "name": stock.get('name', ''),
                "analysis": analysis
            })
    
    # Sort based on configured strategy
    sort_key = config["stock_analysis"]["sort_strategy"]
    return sorted(
        analyses,
        key=lambda x: abs(x["analysis"].get(sort_key, 0)),
        reverse=True
    )

def filter_stocks_by_preferences(
    analyses: list[dict],
    user_input: dict
) -> list[dict]:
    """filter stocks based on user preferences"""
    filtered_analyses = analyses.copy()
    
    # filter by sector preferences if specified
    sector_preference = user_input.get('sector_preference')
    if sector_preference and sector_preference.lower() != 'any':
        filtered_analyses = [
            stock for stock in filtered_analyses 
            if stock['analysis'].get('sector', '').lower() == sector_preference.lower()
        ]
        
        # if no stocks match the sector, keep a few top stocks
        if not filtered_analyses and analyses:
            filtered_analyses = analyses[:3]  # keep top 3 stocks regardless of sector
    
    # filter by target profit if specified
    target_profit = user_input.get('target_profit')
    if target_profit and isinstance(target_profit, (int, float)) and target_profit > 0:
        # keep stocks with momentum >= target profit or close to it (within 30%)
        profit_threshold = float(target_profit) * 0.7
        profit_filtered = [
            stock for stock in filtered_analyses
            if abs(stock['analysis'].get('momentum', 0)) >= profit_threshold
        ]
        
        # if we have stocks meeting the profit criteria, use them
        if profit_filtered:
            filtered_analyses = profit_filtered
    
    # ensure we have at least some stocks to recommend
    if not filtered_analyses and analyses:
        filtered_analyses = analyses[:5]  # keep top 5 stocks if all filters removed everything
        
    return filtered_analyses

def generate_recommendations(
    analyses: List[Dict],
    sentiment: Dict,
    risk_profile: Dict,
    user_history: Dict,
    user_input: Dict,
    config: Dict
) -> Dict:
    """Dynamically generate recommendations based on multiple factors"""
    # Get user preferences
    budget = float(user_input.get("budget", user_input.get("investment_amount", 100000)))
    risk_level = risk_profile.get("risk_profile", "moderate").lower()
    time_horizon = user_input.get("time_horizon", "medium").lower()
    
    # Filter stocks based on user preferences
    filtered_analyses = filter_stocks_by_preferences(analyses, user_input)
    
    # Adjust analysis strategy based on risk profile and time horizon
    allocation_config = config["recommendation"]["allocation_strategy"].get(risk_level, {})
    
    # Calculate how many stocks to recommend
    max_rec = config["recommendation"]["max_recommendations"]
    top_percent = allocation_config.get("top_percent", 0.33)
    num_recommendations = min(max_rec, max(1, int(len(filtered_analyses) * top_percent)))
    
    recommendations = []
    allocation_suggestions = {}
    
    # Adjust stock selection based on risk profile and time horizon
    if risk_level == "low":
        # For low risk, prioritize stocks with lower volatility
        filtered_analyses.sort(key=lambda x: x["analysis"].get("volatility", 1))
    elif risk_level == "high":
        # For high risk, prioritize stocks with higher momentum
        filtered_analyses.sort(key=lambda x: abs(x["analysis"].get("momentum", 0)), reverse=True)
    
    # Adjust for time horizon
    if time_horizon == "short":
        # For short-term, prioritize stocks with strong recent momentum
        filtered_analyses.sort(key=lambda x: abs(x["analysis"].get("momentum", 0)), reverse=True)
    elif time_horizon == "long":
        # For long-term, prioritize stocks with good trend and lower volatility
        filtered_analyses.sort(
            key=lambda x: (
                2 if x["analysis"].get("price_trend") in ["strong_uptrend", "uptrend"] else 
                1 if x["analysis"].get("price_trend") == "sideways" else 0,
                -x["analysis"].get("volatility", 1)
            ), 
            reverse=True
        )
    
    for i, stock_info in enumerate(filtered_analyses[:num_recommendations]):
        code = stock_info["code"]
        name = stock_info["name"]
        analysis = stock_info["analysis"]
        sector = analysis.get('sector', '')
        
        # Dynamic expected return calculation based on risk profile and time horizon
        momentum = analysis.get('momentum', 0)
        volatility = analysis.get('volatility', 1)
        
        if time_horizon == "short":
            # Short-term focuses more on momentum
            expected_return = momentum * (1.2 - volatility/10)
        else:
            # Long-term is more balanced
            expected_return = momentum * (1 - volatility/10)
            
        # Format expected return
        expected_return_str = f"{expected_return:.1f}%"
        
        # Dynamic allocation considering budget, diversification, and risk profile
        diversification = allocation_config.get("diversification", 0.5)
        
        # For low budget, recommend fewer stocks
        if budget < 10000:
            num_stocks = min(3, num_recommendations)
        else:
            num_stocks = num_recommendations
            
        alloc = round(budget * (1 - diversification) / num_stocks)
        allocation_suggestions[f"{code} ({name})"] = alloc
        
        # Dynamic recommendation reason based on configured factors
        reason_parts = []
        
        # Add sector-specific reason if it matches user preference
        if sector and sector.lower() == user_input.get('sector_preference', '').lower():
            reason_parts.append(f"Matches your preferred {sector} sector")
            
        # Add risk-specific reason
        if risk_level == "low":
            if volatility < 0.05:
                reason_parts.append("Low volatility stock suitable for conservative investors")
        elif risk_level == "high":
            if momentum > 5:
                reason_parts.append("High momentum stock with growth potential")
                
        # Add time horizon specific reason
        if time_horizon == "short":
            if analysis.get('price_trend') in ["strong_uptrend", "uptrend"]:
                reason_parts.append("Strong short-term momentum")
        elif time_horizon == "long":
            if analysis.get('price_trend') in ["strong_uptrend", "uptrend"] and volatility < 0.1:
                reason_parts.append("Stable long-term growth potential")
        
        # Add standard reasons
        if "sentiment" in config["recommendation"]["factors"]:
            reason_parts.append(sentiment.get('summary', ''))
        if "risk_profile" in config["recommendation"]["factors"]:
            reason_parts.append(risk_profile.get('recommendation', ''))
        if "user_history" in config["recommendation"]["factors"]:
            if user_history.get('preferred_sectors') and sector in user_history.get('preferred_sectors', []):
                reason_parts.append(f"Matches your history with {sector}")
        
        recommendations.append({
            "company": f"{code} - {name}",
            "sector": sector,
            "recommendation_reason": " | ".join(reason_parts),
            "risk": risk_level.capitalize(),
            "expected_return": expected_return_str,
            "allocation_suggestion": f"{alloc} {user_input.get('currency', 'PKR')}",
            "analysis_highlights": {k: analysis[k] for k in config["stock_analysis"]["analysis_metrics"] if k in analysis}
        })
    
    return {
        "recommendations": recommendations,
        "allocation_suggestions": allocation_suggestions
    }

def generate_follow_up(stock_analyses: List[Dict], user_history: Dict, risk_profile: Dict) -> str:
    """Generate dynamic follow-up suggestions"""
    follow_ups = []
    
    # Based on user history
    if user_history.get('preferred_sectors'):
        follow_ups.append(
            f"Consider diversifying beyond your usual sectors: {', '.join(user_history['preferred_sectors'])}"
        )
    
    # Based on risk profile
    risk_level = risk_profile.get('risk_profile', '').lower()
    if risk_level == 'low':
        follow_ups.append("You might consider slightly higher risk options for better returns")
    elif risk_level == 'high':
        follow_ups.append("Consider balancing your portfolio with some stable investments")
    
    # Based on stock analysis
    if len(stock_analyses) > 0:
        top_sectors = {}
        for s in stock_analyses:
            sector = s['analysis'].get('sector', '')
            momentum = s['analysis'].get('momentum', 0)
            if sector:
                if sector not in top_sectors or momentum > top_sectors[sector]:
                    top_sectors[sector] = momentum
        
        if top_sectors:
            top_sector = max(top_sectors.items(), key=lambda x: x[1])[0]
            follow_ups.append(f"The {top_sector} sector is showing strong momentum currently")
    
    return " ".join(follow_ups) if follow_ups else "No specific follow-up recommendations"

def manager_agent(user_input: Dict, config: Dict = CONFIG, refresh_data: bool = False) -> Dict:
    try:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        db_manager = agents["stock_analyzer"].db_manager
        
        # 1. Get stock data (either fresh or from database)
        if refresh_data:
            # Scrape fresh data if requested
            logger.info("Scraping fresh stock data...")
            stock_data_path = scrape_stocks_tool()
            with open(stock_data_path, 'r', encoding='utf-8') as f:
                stock_data_json = json.load(f)
                stock_data = stock_data_json.get('stocks', [])
            
            if not stock_data:
                return {"error": "No stock data available from scraping."}
                
            # Save stock data to database
            for stock in stock_data:
                try:
                    stock_obj = StockData(
                        sector=stock.get('sector', ''),
                        code=stock.get('code', ''),
                        name=stock.get('name', ''),
                        open_price=stock.get('open_price', 0.0),
                        high_price=stock.get('high_price', 0.0),
                        low_price=stock.get('low_price', 0.0),
                        close_price=stock.get('close_price', 0.0),
                        volume=stock.get('volume', 0),
                        change=stock.get('change', 0.0),
                        change_percent=stock.get('change_percent', 0.0),
                        timestamp=datetime.fromisoformat(stock.get('timestamp')) if isinstance(stock.get('timestamp'), str) else datetime.now()
                    )
                    db_manager.save_stock_data(stock_obj)
                    logger.info(f"Saved stock {stock.get('code', '')} to database")
                except Exception as e:
                    logger.error(f"Error saving stock {stock.get('code', '')}: {str(e)}")
        else:
            # Use existing data from database
            logger.info("Using existing stock data from database...")
            stock_data = db_manager.get_latest_stock_data()
            if not stock_data:
                return {"error": "No stock data available in database. Try refreshing the data."}
            
            # Convert database format to expected format
            for stock in stock_data:
                if 'change_price' in stock and 'change' not in stock:
                    stock['change'] = stock['change_price']
        
        # 2. Analyze stocks
        stock_analyses = analyze_stocks(stock_data, config)
        
        # 3. Get news and sentiment
        news_data = agents["news_scraper"].run()
        sentiment_data = agents["sentiment_analyzer"].run(news_data=news_data)
        
        # 4. Get user risk profile and history
        user_id = user_input.get("user_id", "default_user")
        risk_profile = agents["risk_profiler"].run(user_profile=user_input)
        user_history = agents["user_history"].run(user_id=user_id)
        
        # 5. Generate recommendations
        recommendations_data = generate_recommendations(
            stock_analyses,
            sentiment_data,
            risk_profile,
            user_history,
            user_input,
            config
        )
        
        # 6. Generate chart
        chart_data = recommendations_data["allocation_suggestions"]
        chart_image = generate_chart(
            chart_data,
            config["visualization"]["chart_type"],
            display_percent=config["visualization"]["display_percent"]
        )
        
        # 7. Generate follow-up suggestions
        follow_up = generate_follow_up(stock_analyses, user_history, risk_profile)
        
        # 8. Update portfolio if requested
        if user_input.get("update_portfolio", False):
            agents["portfolio_updater"].run(
                user_id=user_id,
                recommendations=recommendations_data["recommendations"],
                allocation=recommendations_data["allocation_suggestions"]
            )
        
        # 9. Return comprehensive response
        return {
            "status": "success",
            "market_summary": {
                "total_stocks": len(stock_data),
                "analyzed_stocks": len(stock_analyses),
                "market_sentiment": sentiment_data.get("sentiment", "Neutral"),
                "timestamp": datetime.now().isoformat(),
                "data_source": "fresh scrape" if refresh_data else "database"
            },
            "recommendations": recommendations_data["recommendations"],
            "allocation_chart": chart_image,
            "follow_up_suggestions": follow_up,
            "risk_profile": risk_profile,
            "user_preferences": {
                "budget": user_input.get("budget", 10000.0),
                "sector_preference": user_input.get("sector_preference", "Any"),
                "risk_tolerance": user_input.get("risk_tolerance", "Moderate"),
                "time_horizon": user_input.get("time_horizon", "Medium-term"),
                "target_profit": user_input.get("target_profit", 15.0)
            }
        }
    except Exception as e:
        logger.error(f"Error in manager agent: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "An error occurred while processing your request."
        }

def hybrid_input_workflow(
    user_input: Dict, 
    chat_message: str = '', 
    user_id: Optional[str] = None,
    config: Dict = CONFIG,
    refresh_data: bool = False
) -> Dict:
    """Process hybrid input with dynamic configuration"""
    # Store user preferences in database
    if user_id and user_input:
        from agents.stock_agent import EnhancedDatabaseManager
        db_manager = EnhancedDatabaseManager()
        with db_manager.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO user_preferences (
                    user_id, budget, sector, risk_appetite, time_horizon, target_profit, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                user_input.get('budget', 10000.0),
                user_input.get('sector_preference', ''),
                user_input.get('risk_tolerance', 'medium'),
                user_input.get('time_horizon', 'medium'),
                user_input.get('target_profit', 15.0),
                datetime.now().isoformat()
            ))
            conn.commit()
    
    # Check if refresh is explicitly requested in the input
    if 'refresh_data' in user_input:
        refresh_data = user_input.pop('refresh_data')
    
    # For backward compatibility with chat interface
    if chat_message:
        parsed, missing = parse_hybrid_input(user_input, chat_message)
        if missing:
            return {"status": "input_required", "missing_fields": missing}
    else:
        parsed = user_input
    
    if user_id:
        # Dynamic context loading
        parsed["user_id"] = user_id
        user_context = agents["user_history"].get_extended_context(user_id)
        parsed.update(user_context)
    
    # Merge with config if needed
    if "config" in parsed:
        config.update(parsed.pop("config"))
    
    return manager_agent(parsed, config, refresh_data)


def store_feedback(user_id: Optional[str], feedback: str, recommendations: List[Dict]) -> None:
    """Store user feedback for recommendations"""
    try:
        # Create a feedback entry
        feedback_entry = {
            "user_id": user_id or "anonymous",
            "feedback": feedback,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store feedback in the database
        db_manager = agents["stock_analyzer"].db_manager
        with db_manager.get_connection() as conn:
            # Create feedback table if it doesn't exist
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    feedback TEXT NOT NULL,
                    recommendations TEXT,
                    timestamp TEXT
                )
            ''')
            
            # Insert feedback
            conn.execute('''
                INSERT INTO user_feedback (user_id, feedback, recommendations, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id or "anonymous",
                feedback,
                json.dumps(recommendations),
                datetime.now().isoformat()
            ))
            conn.commit()
        
        # Update user history if user_id is provided
        if user_id and agents.get("user_history"):
            agents["user_history"].update_from_feedback(user_id, feedback, recommendations)
            
        return True
    except Exception as e:
        print(f"Error storing feedback: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    import matplotlib
    # Ensure we're using the Agg backend
    matplotlib.use('Agg')
    # Check if refresh flag is provided as command line argument
    refresh = '--refresh' in sys.argv
    result = manager_agent({}, refresh_data=refresh)
    print(json.dumps({
        k: (v[:40] + '...' if k == 'allocation_chart' else v) 
        for k, v in result.items() 
        if k != 'agent_insights'
    }, indent=2))