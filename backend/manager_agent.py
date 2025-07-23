import base64
from io import BytesIO
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
    fig, ax = plt.subplots()
    
    if chart_type == "pie":
        ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%' if kwargs.get('display_percent', True) else None)
    elif chart_type == "bar":
        ax.bar(data.keys(), data.values())
        plt.xticks(rotation=45)
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def analyze_stocks(stock_data: List[Dict], config: Dict) -> List[Dict]:
    """Dynamic stock analysis based on config"""
    analyses = []
    max_stocks = config["stock_analysis"]["max_stocks_to_analyze"]
    
    for stock in stock_data[:max_stocks]:
        analysis = agents["stock_analyzer"].analyzer.comprehensive_analysis(
            stock['code'],
            metrics=config["stock_analysis"]["analysis_metrics"]
        )
        if analysis:
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

def generate_recommendations(
    analyses: List[Dict],
    sentiment: Dict,
    risk_profile: Dict,
    user_history: Dict,
    user_input: Dict,
    config: Dict
) -> Dict:
    """Dynamically generate recommendations based on multiple factors"""
    budget = float(user_input.get("investment_amount", 100000))
    risk_level = risk_profile.get("risk_profile", "moderate").lower()
    allocation_config = config["recommendation"]["allocation_strategy"].get(risk_level, {})
    
    # Calculate how many stocks to recommend
    max_rec = config["recommendation"]["max_recommendations"]
    top_percent = allocation_config.get("top_percent", 0.33)
    num_recommendations = min(max_rec, max(1, int(len(analyses) * top_percent)))
    
    recommendations = []
    allocation_suggestions = {}
    
    for i, stock_info in enumerate(analyses[:num_recommendations]):
        code = stock_info["code"]
        name = stock_info["name"]
        analysis = stock_info["analysis"]
        
        # Dynamic expected return calculation
        momentum = analysis.get('momentum', 0)
        volatility = analysis.get('volatility', 1)
        expected_return = f"{(momentum * (1 - volatility/10)):.1f}%"
        
        # Dynamic allocation considering diversification factor
        diversification = allocation_config.get("diversification", 0.5)
        alloc = round(budget * (1 - diversification) / num_recommendations)
        allocation_suggestions[f"{code} ({name})"] = alloc
        
        # Dynamic recommendation reason based on configured factors
        reason_parts = []
        if "sentiment" in config["recommendation"]["factors"]:
            reason_parts.append(sentiment.get('summary', ''))
        if "risk_profile" in config["recommendation"]["factors"]:
            reason_parts.append(risk_profile.get('recommendation', ''))
        if "user_history" in config["recommendation"]["factors"]:
            if user_history.get('preferred_sectors'):
                reason_parts.append(f"Matches your history with {user_history['preferred_sectors'][0]}")
        
        recommendations.append({
            "company": f"{code} - {name}",
            "recommendation_reason": " | ".join(reason_parts),
            "risk": risk_level.capitalize(),
            "expected_return": expected_return,
            "allocation_suggestion": f"{alloc} {user_input.get('currency', 'PKR')}",
            "analysis_highlights": {k: analysis[k] for k in config["stock_analysis"]["analysis_metrics"] if k in analysis}
        })
    
    return {
        "recommendations": recommendations,
        "allocation_suggestions": allocation_suggestions
    }

def manager_agent(user_input: Dict, config: Dict = CONFIG) -> Dict:
    try:
        # 1. Get stock data
        stock_data_path = scrape_stocks_tool()
        with open(stock_data_path, 'r', encoding='utf-8') as f:
            stock_data_json = json.load(f)
            stock_data = stock_data_json.get('stocks', [])
        
        if not stock_data:
            return {"error": "No stock data available."}
            
        # Save stock data to database
        db_manager = agents["stock_analyzer"].db_manager
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
                print(f"Saved stock {stock.get('code', '')} to database")
            except Exception as e:
                print(f"Error saving stock {stock.get('code', 'unknown')}: {str(e)}")
                continue

        # 2. Run all agents dynamically
        agent_results = {
            "stock_analysis": analyze_stocks(stock_data, config),
            "news": agents["news_scraper"].run(),
        }
        agent_results["sentiment"] = agents["sentiment_analyzer"].run(
            news_data=agent_results["news"]
        )
        agent_results["risk_profile"] = agents["risk_profiler"].run(
            user_profile=user_input
        )
        agent_results["user_history"] = agents["user_history"].run(
            user_id=user_input.get('user_id', 'demo')
        )
        agent_results["portfolio"] = agents["portfolio_updater"].run(
            user_id=user_input.get('user_id', 'demo')
        )

        # 3. Generate recommendations dynamically
        recommendation_result = generate_recommendations(
            analyses=agent_results["stock_analysis"],
            sentiment=agent_results["sentiment"],
            risk_profile=agent_results["risk_profile"],
            user_history=agent_results["user_history"],
            user_input=user_input,
            config=config
        )

        # 4. Generate visualization
        viz_config = config["visualization"]
        viz_base64 = generate_chart(
            recommendation_result["allocation_suggestions"],
            chart_type=viz_config["chart_type"],
            display_percent=viz_config["display_percent"]
        )

        # 5. Dynamic follow-up based on analysis
        follow_up = generate_follow_up(
            agent_results["stock_analysis"],
            agent_results["user_history"],
            agent_results["risk_profile"]
        )

        return {
            **recommendation_result,
            "visualization": viz_base64,
            "follow_up": follow_up,
            "agent_insights": {k: v for k, v in agent_results.items() if k != "stock_analysis"}
        }
    except Exception as e:
        return {"error": f"Manager agent failed: {str(e)}"}

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
        top_sector = max(
            [(s['analysis'].get('sector', ''), s['analysis'].get('momentum', 0)) 
             for s in stock_analyses],
            key=lambda x: x[1]
        )[0]
        if top_sector:
            follow_ups.append(f"The {top_sector} sector is showing strong momentum currently")
    
    return " ".join(follow_ups) if follow_ups else "No specific follow-up recommendations"

def hybrid_input_workflow(
    user_input: Dict, 
    chat_message: str, 
    user_id: Optional[str] = None,
    config: Dict = CONFIG
) -> Dict:
    """Process hybrid input with dynamic configuration"""
    parsed, missing = parse_hybrid_input(user_input, chat_message)
    if missing:
        return {"status": "input_required", "missing_fields": missing}
    
    if user_id:
        # Dynamic context loading
        parsed["user_id"] = user_id
        user_context = agents["user_history"].get_extended_context(user_id)
        parsed.update(user_context)
    
    # Merge with config if needed
    if "config" in parsed:
        config.update(parsed.pop("config"))
    
    return manager_agent(parsed, config)

def store_feedback(user_id: Optional[str], feedback: str, recommendations: List[Dict]) -> None:
    """Store user feedback for recommendations"""
    try:
        # Create a feedback entry
        feedback_entry = {
            "user_id": user_id or "anonymous",
            "feedback": feedback,
            "recommendations": recommendations,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
        
        # In a real implementation, this would store to a database
        # For now, we'll just print the feedback
        print(f"Feedback stored: {json.dumps(feedback_entry)}")
        
        # Update user history if user_id is provided
        if user_id and agents.get("user_history"):
            agents["user_history"].update_from_feedback(user_id, feedback, recommendations)
            
        return True
    except Exception as e:
        print(f"Error storing feedback: {str(e)}")
        return False

if __name__ == "__main__":
    result = manager_agent({})
    print(json.dumps({
        k: (v[:40] + '...' if k == 'visualization' else v) 
        for k, v in result.items() 
        if k != 'agent_insights'
    }, indent=2))