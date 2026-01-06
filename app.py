"""
Children's Story Generator Flask Application
Main application entry point with health check endpoint
"""

import os

try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for
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
        """Generate story endpoint - Requirements: 1.1, 1.2, 1.3, 1.4"""
        try:
            # Import services
            from services.story_generator import StoryGenerator
            from services.image_generator import ImageGenerator
            from models import StoryRequest, Character
            
            # Extract form data
            form_data = request.form
            
            # Parse characters
            characters = []
            num_characters = int(form_data.get('num_characters', 1))
            
            for i in range(1, num_characters + 1):
                name = form_data.get(f'character_{i}_name', '').strip()
                pronouns = form_data.get(f'character_{i}_pronouns', '')
                
                if name and pronouns:
                    try:
                        character = Character(name=name, pronouns=pronouns)
                        characters.append(character)
                    except ValueError as e:
                        return render_template('index.html', error=f"Character {i}: {str(e)}")
            
            # Parse adventure items into keywords
            keywords = []
            magic_tool = form_data.get('magic_tool', '').strip()
            adventure_pack = form_data.get('adventure_pack', '').strip()
            animal_friend = form_data.get('animal_friend', '').strip()
            
            if magic_tool:
                keywords.append(magic_tool)
            if adventure_pack:
                keywords.append(adventure_pack)
            if animal_friend:
                keywords.append(animal_friend)
            
            # Create story request
            story_request = StoryRequest(
                characters=characters,
                topic=form_data.get('topic', ''),
                keywords=keywords,
                age_group=form_data.get('age_group', ''),
                story_length=form_data.get('story_length', ''),
                include_image=form_data.get('include_image') == 'true'
            )
            
            # Validate request
            validation_errors = story_request.validate()
            if validation_errors:
                error_message = "Please fix these issues: " + "; ".join(validation_errors)
                return render_template('index.html', error=error_message)
            
            # Generate story
            story_generator = StoryGenerator()
            generated_story = story_generator.generate_story(story_request)
            
            # Generate image if requested
            if story_request.include_image:
                image_generator = ImageGenerator()
                image_url = image_generator.generate_illustration(generated_story, story_request.topic)
                generated_story.image_url = image_url
            
            # Store story (for now, just pass to template)
            # In a full implementation, we'd store in database
            
            return render_template('story.html', story=generated_story)
            
        except Exception as e:
            print(f"Error generating story: {e}")
            error_message = "Sorry, we couldn't create your story right now. Please try again!"
            return render_template('index.html', error=error_message)
    
    @app.route('/story/<story_id>')
    def view_story(story_id):
        """View a specific story - Requirements: 1.3, 1.4"""
        # In a full implementation, we'd retrieve from database
        # For now, redirect to create new story since we don't have persistence
        # This is a placeholder that would be replaced with proper story retrieval
        
        # For MVP, we'll redirect to the story creation form
        # In production, this would query the database for the story_id
        return redirect(url_for('index'))
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    if app is not None:
        # Development server
        app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    else:
        print("Cannot start application. Please install dependencies with: pip install -r requirements.txt")