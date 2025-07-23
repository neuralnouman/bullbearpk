import logging
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from manager_agent import hybrid_input_workflow, store_feedback
from api.market_routes import market_routes

# Configure logging to show debug output in the terminal
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(market_routes)

@app.route('/api/hybrid', methods=['POST'])
def hybrid():
    logging.debug("Received /api/hybrid POST request with data: %s", request.json)
    try:
        data = request.json
        logging.debug("Parsed hybrid request data: %s", data)
        result = hybrid_input_workflow(
            user_input=data.get('user_input', {}),
            chat_message=data.get('chat_message', ''),
            user_id=data.get('user_id')
        )
        logging.debug("Hybrid workflow result: %s", result)
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
        store_feedback(
            user_id=data.get('user_id'),
            feedback=data.get('feedback'),
            recommendations=data.get('recommendations')
        )
        logging.info("Feedback stored for user_id: %s", data.get('user_id'))
        return jsonify({"status": "ok"})
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

if __name__ == "__main__":
    logging.info("Starting Flask API server on port 5000")
    app.run(debug=True, port=5000)
