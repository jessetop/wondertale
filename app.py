"""
Children's Story Generator Flask Application
Main application entry point with health check endpoint
"""

import os
import time

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
        # Check if OpenAI API key is configured
        openai_configured = bool(os.getenv('OPENAI_API_KEY') and 
                                os.getenv('OPENAI_API_KEY') != 'your_actual_openai_api_key_here')
        
        return jsonify({
            'status': 'healthy',
            'service': 'children-story-generator',
            'version': '1.0.0',
            'openai_configured': openai_configured,
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 200
    
    @app.route('/debug')
    def debug_info():
        """Debug endpoint for troubleshooting (remove in production)"""
        def check_openai_available():
            """Check if OpenAI package is available"""
            try:
                import openai
                return True
            except ImportError:
                return False
        
        # Only show debug info in development or if specifically enabled
        if os.getenv('FLASK_ENV') != 'production' or os.getenv('DEBUG_ENABLED') == 'true':
            openai_key = os.getenv('OPENAI_API_KEY', 'NOT_SET')
            return jsonify({
                'environment_variables': {
                    'FLASK_ENV': os.getenv('FLASK_ENV', 'NOT_SET'),
                    'OPENAI_API_KEY_SET': 'YES' if openai_key and openai_key != 'NOT_SET' and openai_key != 'your_actual_openai_api_key_here' else 'NO',
                    'OPENAI_API_KEY_LENGTH': len(openai_key) if openai_key != 'NOT_SET' else 0,
                    'FLASK_SECRET_KEY_SET': 'YES' if os.getenv('FLASK_SECRET_KEY') else 'NO',
                    'MAX_STORY_LENGTH': os.getenv('MAX_STORY_LENGTH', 'NOT_SET'),
                    'PORT': os.getenv('PORT', 'NOT_SET')
                },
                'python_packages': {
                    'flask_available': FLASK_AVAILABLE,
                    'openai_available': check_openai_available(),
                    'dotenv_loaded': True  # If we get here, dotenv worked
                }
            }), 200
        else:
            return jsonify({'error': 'Debug endpoint disabled in production'}), 403
    
    # Routes
    @app.route('/')
    def landing():
        """Landing page with WonderTale branding"""
        return render_template('landing.html')
    
    @app.route('/create')
    def index():
        """Story creation form"""
        return render_template('index.html')
    
    # New wizard routes
    @app.route('/wizard')
    def wizard_start():
        """Start the story creation wizard"""
        return redirect(url_for('wizard_characters'))
    
    @app.route('/wizard/characters')
    def wizard_characters():
        """Step 1: Character setup"""
        return render_template('wizard/characters.html')
    
    @app.route('/wizard/age')
    def wizard_age():
        """Step 2: Age selection"""
        return render_template('wizard/age.html')
    
    @app.route('/wizard/world')
    def wizard_world():
        """Step 3: Story world/topic"""
        return render_template('wizard/world.html')
    
    @app.route('/wizard/length')
    def wizard_length():
        """Step 4: Story length"""
        return render_template('wizard/length.html')
    
    @app.route('/wizard/magic-tool')
    def wizard_magic_tool():
        """Step 5: Magic tool selection"""
        return render_template('wizard/magic_tool.html')
    
    @app.route('/wizard/adventure-pack')
    def wizard_adventure_pack():
        """Step 6: Adventure pack selection"""
        return render_template('wizard/adventure_pack.html')
    
    @app.route('/wizard/animal-friend')
    def wizard_animal_friend():
        """Step 7: Animal friend selection"""
        return render_template('wizard/animal_friend.html')
    
    @app.route('/wizard/review')
    def wizard_review():
        """Final: Review and generate"""
        return render_template('wizard/review.html')
    
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
            
            # Debug: Check OpenAI configuration
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key or openai_key == 'your_actual_openai_api_key_here':
                print("ERROR: OpenAI API key not configured properly")
                error_message = "Story generation is not configured. Please contact support."
                return render_template('index.html', error=error_message)
            
            print(f"DEBUG: Generating story for {len(characters)} characters, topic: {story_request.topic}")
            start_time = time.time()
            
            # Generate story
            story_generator = StoryGenerator()
            generated_story = story_generator.generate_story(story_request)
            
            generation_time = time.time() - start_time
            print(f"DEBUG: Story generated successfully in {generation_time:.2f}s, title: {generated_story.title}")
            
            # Generate image if requested
            if story_request.include_image:
                try:
                    image_generator = ImageGenerator()
                    image_url = image_generator.generate_illustration(generated_story, story_request.topic)
                    generated_story.image_url = image_url
                    print(f"DEBUG: Image generated successfully")
                except Exception as img_error:
                    print(f"WARNING: Image generation failed: {img_error}")
                    # Continue without image - don't fail the whole request
            
            # Store story (for now, just pass to template)
            # In a full implementation, we'd store in database
            
            return render_template('story.html', story=generated_story)
            
        except ImportError as e:
            print(f"ERROR: Import failed: {e}")
            error_message = "Service temporarily unavailable. Please try again later."
            return render_template('index.html', error=error_message)
        except ValueError as e:
            print(f"ERROR: Validation error: {e}")
            error_message = f"Invalid input: {str(e)}"
            return render_template('index.html', error=error_message)
        except Exception as e:
            print(f"ERROR: Unexpected error generating story: {e}")
            print(f"ERROR TYPE: {type(e).__name__}")
            import traceback
            print(f"ERROR TRACEBACK: {traceback.format_exc()}")
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
    
    @app.route('/tts/generate', methods=['POST'])
    def generate_tts():
        """Generate TTS audio for story text - Requirements: 9.1, 9.2, 9.4"""
        try:
            from services.tts_service import TTSService
            
            # Get request data
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'error': 'Text is required'}), 400
            
            text = data.get('text', '').strip()
            voice = data.get('voice', 'friendly')
            
            if not text:
                return jsonify({'error': 'Text cannot be empty'}), 400
            
            # Initialize TTS service
            tts_service = TTSService()
            
            if not tts_service.is_available():
                return jsonify({
                    'error': 'TTS service unavailable',
                    'fallback': True,
                    'message': 'AI voices are not available right now. Please use your browser\'s built-in voices instead.'
                }), 503
            
            # Generate audio
            audio_path = tts_service.generate_audio(text, voice)
            
            if not audio_path:
                return jsonify({
                    'error': 'Failed to generate audio',
                    'fallback': True,
                    'message': 'Could not create audio. Please try the browser voices instead.'
                }), 500
            
            # Return audio file
            from flask import send_file
            return send_file(
                audio_path,
                mimetype='audio/mpeg',
                as_attachment=False,
                download_name=f'story_audio_{voice}.mp3'
            )
            
        except Exception as e:
            print(f"Error in TTS generation: {e}")
            return jsonify({
                'error': 'TTS generation failed',
                'fallback': True,
                'message': 'Something went wrong. Please try the browser voices instead.'
            }), 500
    
    @app.route('/tts/voices')
    def get_tts_voices():
        """Get available TTS voices - Requirements: 9.3"""
        try:
            from services.tts_service import TTSService
            
            tts_service = TTSService()
            
            if not tts_service.is_available():
                return jsonify({
                    'available': False,
                    'voices': [],
                    'message': 'AI voices are not available. Browser voices will be used instead.'
                })
            
            voices = tts_service.get_voices()
            return jsonify({
                'available': True,
                'voices': voices,
                'message': 'AI voices are ready!'
            })
            
        except Exception as e:
            print(f"Error getting TTS voices: {e}")
            return jsonify({
                'available': False,
                'voices': [],
                'message': 'Could not load AI voices. Browser voices will be used instead.'
            })
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    if app is not None:
        # Development server
        app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    else:
        print("Cannot start application. Please install dependencies with: pip install -r requirements.txt")