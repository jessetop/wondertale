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
    
    # Routes
    @app.route('/')
    def landing():
        """Landing page with WonderTale branding"""
        return render_template('landing.html')
    
    @app.route('/create')
    def index():
        """Story creation form"""
        return render_template('index.html')
    
    @app.route('/generate', methods=['POST'])
    def generate_story():
        """Generate story endpoint (placeholder for now)"""
        # This will be implemented in later tasks
        # For now, just show a sample story
        from models import GeneratedStory, Character
        from datetime import datetime
        
        # Create sample story data for testing
        sample_story = GeneratedStory(
            id="sample-123",
            title="Emma's Amazing Dragon Adventure",
            content="""Once upon a time, in a magnificent castle high on a hill, there lived a brave young adventurer named Emma. She loved exploring the castle's many rooms and secret passages, always looking for new discoveries.

One sunny morning, Emma heard a gentle roar coming from the castle courtyard. When she looked out her window, she saw something amazing – a beautiful dragon with shimmering scales that sparkled in the sunlight! The dragon looked friendly but seemed lost.

Emma wasn't scared at all. Instead, she smiled and waved at the dragon. "Hello there! Are you lost?" she called out. The dragon nodded sadly. Emma knew just what to do. She grabbed her map of the kingdom and hurried down to help her new friend.

Together, Emma and the dragon looked at the map. Emma used her clever thinking to figure out where the dragon's home was – a beautiful mountain beyond the forest. The dragon was so happy! Before flying away, the dragon gave Emma a special scale from its tail that glowed with magic.

"You were so brave and kind, Emma," the dragon said. "Whenever you need help, just hold this scale and I'll come to visit!" Emma waved goodbye as her new friend flew home. She knew that being kind and helpful made her the best kind of hero.""",
            moral="Being kind and helpful to others makes you a true hero.",
            characters=[Character(name="Emma", pronouns="she/her")],
            topic="dragons",
            age_group="5-6",
            story_length="medium",
            image_url=None,
            created_at=datetime.now(),
            word_count=234,
            target_word_range=(120, 250)
        )
        
        return render_template('story.html', story=sample_story)
    
    @app.route('/story/<story_id>')
    def view_story(story_id):
        """View a specific story (placeholder for now)"""
        # This will be implemented in later tasks
        # For now, redirect to sample story
        return generate_story()
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    if app is not None:
        # Development server
        app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    else:
        print("Cannot start application. Please install dependencies with: pip install -r requirements.txt")