import json
import os
import logging
from flask import Flask, request, render_template, jsonify
import optimizer
import ai_insights
import quantum_optimizer
import openai_insights
import file_parser

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "aqwse-development-key")

# Initialize quantum optimizer and OpenAI insights generator
ibm_token = os.environ.get("IBM_QUANTUM_TOKEN")
openai_key = os.environ.get("OPENAI_API_KEY")

# Track if we're using quantum computing and/or OpenAI
use_quantum = ibm_token is not None
use_openai = openai_key is not None

if use_quantum:
    logger.info("IBM Quantum token found - will attempt to use quantum computing")
else:
    logger.info("No IBM Quantum token found - using classical optimization")

if use_openai:
    logger.info("OpenAI API key found - will use GPT for insights")
else:
    logger.info("No OpenAI API key found - using deterministic insights")

# Initialize our optimizers and insight generators
quantum_opt = quantum_optimizer.QuantumWorkflowOptimizer(use_quantum=use_quantum, ibm_token=ibm_token)
openai_gen = openai_insights.OpenAIInsightsGenerator(api_key=openai_key)

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/data-format')
def data_format():
    """Render the data format guide page"""
    return render_template('data_format.html')

@app.route('/import-file', methods=['POST'])
def import_file():
    """Process file upload and extract project and developer data"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
            
        if file:
            # Read the file content
            file_content = file.read()
            
            # Parse the file based on its type
            result = file_parser.parse_uploaded_file(file_content, file.filename)
            
            if not result.get('success', False):
                logger.error(f"File parsing error: {result.get('error', 'Unknown error')}")
                return jsonify(result), 400
                
            logger.info(f"Successfully imported data from file: {file.filename}")
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        return jsonify({'success': False, 'error': f'File upload failed: {str(e)}'}), 500

@app.route('/optimize', methods=['POST'])
def optimize():
    """Process optimization request and return results"""
    try:
        # Get input data from request
        data = request.json
        logger.info(f"Received optimization request with {len(data.get('developers', []))} developers and {len(data.get('projects', []))} projects")
        
        # Validate input data
        if not _validate_input(data):
            logger.error("Input validation failed")
            return jsonify({'success': False, 'error': 'Invalid input data'}), 400
        
        # Check if we should try quantum optimization
        use_quantum_param = request.args.get('quantum', 'true').lower() == 'true'
        
        try:
            if use_quantum and use_quantum_param:
                # Run quantum-powered optimization algorithm
                logger.info("Using quantum-powered optimization")
                optimization_result = quantum_opt.optimize(
                    data['budget'],
                    data['deadline'],
                    data['developers'],
                    data['projects']
                )
            else:
                # Run classical optimization algorithm
                logger.info("Using classical optimization")
                optimization_result = optimizer.run_optimization(
                    data['budget'],
                    data['deadline'],
                    data['developers'],
                    data['projects']
                )
                
            logger.info(f"Optimization completed successfully with {len(optimization_result.get('assignments', []))} assignments")
        except Exception as opt_error:
            logger.error(f"Optimization algorithm failed: {str(opt_error)}")
            return jsonify({'success': False, 'error': f'Optimization algorithm failed: {str(opt_error)}'}), 500
        
        try:
            # Generate AI insights - try OpenAI first, fall back to deterministic
            if use_openai:
                logger.info("Generating OpenAI-powered insights")
                insights = openai_gen.generate_insights(
                    data, 
                    optimization_result
                )
            else:
                logger.info("Using deterministic insights")
                insights = ai_insights.generate_insights(
                    data, 
                    optimization_result
                )
            
            logger.info("Insights generation completed successfully")
        except Exception as insights_error:
            logger.error(f"Insights generation failed: {str(insights_error)}")
            # Fall back to deterministic insights on failure
            insights = ai_insights.generate_insights(
                data, 
                optimization_result
            )
        
        # Combine results
        result = {**optimization_result, **{'success': True}, **insights}
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in optimization process: {str(e)}")
        return jsonify({'success': False, 'error': f'Optimization failed: {str(e)}'}), 500

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
