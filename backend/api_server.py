import logging
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from agentic_framework import AgenticFramework
from api.market_routes import market_routes
from api.portfolio_routes import portfolio_routes
from api.recommendation_routes import recommendation_routes
from api.investment_routes import investment_bp
from api.auth_routes import auth_bp

# Configure logging to show debug output in the terminal
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_server.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(market_routes)
app.register_blueprint(portfolio_routes)
app.register_blueprint(recommendation_routes)
app.register_blueprint(investment_bp, url_prefix='/api/investment')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Log registered routes
logging.info("Registered routes:")
for rule in app.url_map.iter_rules():
    logging.info(f"Route: {rule.endpoint} - {rule.rule} - {rule.methods}")

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.route('/api/hybrid', methods=['POST'])
def hybrid():
    logging.debug("Received /api/hybrid POST request with data: %s", request.json)
    try:
        data = request.json
        logging.debug("Parsed hybrid request data: %s", data)
        
        # Initialize agentic framework
        framework = AgenticFramework()
        
        # Run async workflow
        import asyncio
        result = asyncio.run(framework.run_workflow(
            user_input=data.get('user_input', {}),
            chat_message=data.get('chat_message', ''),
            user_id=data.get('user_id')
        ))
        
        logging.debug("Agentic framework result: %s", result)
        return jsonify(result)
    except Exception as e:
        logging.error("Error in /api/hybrid: %s", str(e), exc_info=True)
        return jsonify({"success": False, "message": f"Error in hybrid: {str(e)}"}), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    logging.debug("Received /api/feedback POST request with data: %s", request.json)
    try:
        data = request.json
        logging.debug("Parsed feedback request data: %s", data)
        
        # Validate required fields
        if not data.get('user_id'):
            return jsonify({"success": False, "message": "user_id is required"}), 400
            
        if not data.get('feedback'):
            return jsonify({"success": False, "message": "feedback is required"}), 400
            
        # Store feedback in database (simplified for now)
        logging.info("Feedback received for user_id: %s", data.get('user_id'))
        return jsonify({"success": True, "message": "Feedback received successfully"})
    except Exception as e:
        logging.error("Error in /api/feedback: %s", str(e), exc_info=True)
        return jsonify({"success": False, "message": f"Error in feedback: {str(e)}"}), 500

@app.route('/api/scrape', methods=['POST'])
def run_scraper():
    try:
        logging.info("Triggering fin_scraper.py for live data...")
        result = subprocess.run(
            ['python', 'agents/fin_scraper.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            # No cwd argument!
        )
        if result.returncode == 0:
            logging.info("fin_scraper.py completed successfully.")
            return jsonify({"success": True, "message": "Scraper ran successfully."}), 200
        else:
            logging.error("fin_scraper.py failed: %s", result.stderr)
            return jsonify({"success": False, "message": result.stderr}), 500
    except Exception as e:
        logging.error("Error running fin_scraper.py: %s", str(e), exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/')
def index():
    logging.info("Health check on / endpoint")
    return "API server is running!"

@app.errorhandler(500)
def handle_500_error(e):
    logging.error(f"Internal server error: {str(e)}", exc_info=True)
    return jsonify({
        "success": False,
        "message": "Internal server error occurred. Check server logs for details."
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        "success": False,
        "message": f"An unexpected error occurred: {str(e)}"
    }), 500

if __name__ == "__main__":
    logging.info("Starting Flask API server on port 5000")
    app.run(debug=True, port=5000)
