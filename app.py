"""
Children's Story Generator Flask Application
Main application entry point with health check endpoint
"""

import os

try:
    from flask import Flask, render_template, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Warning: Flask not installed. Please install dependencies with: pip install -r requirements.txt")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables may not load from .env file")

def create_app():
    """Create and configure Flask application"""
    if not FLASK_AVAILABLE:
        print("Flask is not available. Please install dependencies first.")
        return None
        
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Health check endpoint for deployment platforms
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'service': 'children-story-generator',
            'version': '1.0.0'
        }), 200
    
    # Basic route for testing
    @app.route('/')
    def index():
        """Main story creation page"""
        return render_template('index.html')
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    if app is not None:
        # Development server
        app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    else:
        print("Cannot start application. Please install dependencies with: pip install -r requirements.txt")