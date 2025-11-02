from flask import Flask, jsonify, request
from flask_cors import CORS
from routes.claims_routes import claims_bp
from routes.eligibility_routes import eligibility_bp
from routes.recommendations_routes import recommendations_bp
import logging
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

# Configure file uploads
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register blueprints
app.register_blueprint(claims_bp, url_prefix='/api/claims')
app.register_blueprint(eligibility_bp, url_prefix='/api/eligibility')
app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Claims AI Backend API is running',
        'version': '1.0.0'
    }), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        'api_status': 'active',
        'available_endpoints': [
            '/api/claims/validate',
            '/api/eligibility/check',
            '/api/recommendations/generate'
        ]
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)