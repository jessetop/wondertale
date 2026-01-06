"""
Image Generation Service
Handles AI-powered image creation for story illustrations
"""

import os
from typing import Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Image generation will be disabled.")

from services.story_generator import GeneratedStory

class ImageGenerator:
    """Service for generating story illustrations using DALL-E"""
    
    def __init__(self):
        """Initialize the image generator"""
        self.client = None
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        if not OPENAI_AVAILABLE:
            print("OpenAI not available - image generation disabled")
            return
            
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.client = openai
        else:
            print("Warning: OPENAI_API_KEY not found in environment variables")
    
    def generate_illustration(self, story: GeneratedStory, topic: str) -> Optional[str]:
        """Generate a child-friendly illustration for the story"""
        # This will be implemented in later tasks
        # For now, return None (no image)
        return None
    
    def _create_image_prompt(self, story: GeneratedStory, topic: str) -> str:
        """Create a child-safe image prompt based on story content"""
        # This will be implemented in later tasks
        return f"Child-friendly illustration for a {topic} story"