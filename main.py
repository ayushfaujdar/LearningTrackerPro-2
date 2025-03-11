import json
import os
import logging
from flask import Flask, request, render_template, jsonify
import optimizer
import ai_insights

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "aqwse-development-key")

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    """Process optimization request and return results"""
    try:
        # Get input data from request
        data = request.json
        
        # Validate input data
        if not _validate_input(data):
            return jsonify({'error': 'Invalid input data'}), 400
        
        # Run optimization algorithm
        optimization_result = optimizer.run_optimization(
            data['budget'],
            data['deadline'],
            data['developers'],
            data['projects']
        )
        
        # Generate AI insights
        insights = ai_insights.generate_insights(
            data, 
            optimization_result
        )
        
        # Combine results
        result = {**optimization_result, **insights}
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error in optimization process: {str(e)}")
        return jsonify({'error': f'Optimization failed: {str(e)}'}), 500

def _validate_input(data):
    """Validate the input data"""
    try:
        # Check required fields
        required_fields = ['budget', 'deadline', 'developers', 'projects']
        for field in required_fields:
            if field not in data:
                logging.error(f"Missing required field: {field}")
                return False
        
        # Validate numeric values
        if not isinstance(data['budget'], (int, float)) or data['budget'] <= 0:
            logging.error("Budget must be a positive number")
            return False
        
        if not isinstance(data['deadline'], (int, float)) or data['deadline'] <= 0:
            logging.error("Deadline must be a positive number")
            return False
        
        # Validate developers
        if not isinstance(data['developers'], list) or len(data['developers']) == 0:
            logging.error("At least one developer is required")
            return False
        
        for dev in data['developers']:
            if not all(key in dev for key in ['name', 'rate', 'hours_per_day', 'skills']):
                logging.error("Developer missing required fields")
                return False
            if not isinstance(dev['rate'], (int, float)) or dev['rate'] <= 0:
                logging.error("Developer rate must be a positive number")
                return False
            if not isinstance(dev['hours_per_day'], (int, float)) or dev['hours_per_day'] <= 0:
                logging.error("Developer hours_per_day must be a positive number")
                return False
        
        # Validate projects
        if not isinstance(data['projects'], list) or len(data['projects']) == 0:
            logging.error("At least one project is required")
            return False
        
        for proj in data['projects']:
            if not all(key in proj for key in ['name', 'hours', 'priority']):
                logging.error("Project missing required fields")
                return False
            if not isinstance(proj['hours'], (int, float)) or proj['hours'] <= 0:
                logging.error("Project hours must be a positive number")
                return False
            if not isinstance(proj['priority'], (int, float)) or proj['priority'] < 1 or proj['priority'] > 5:
                logging.error("Project priority must be between 1 and 5")
                return False
        
        return True
    
    except Exception as e:
        logging.error(f"Validation error: {str(e)}")
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
