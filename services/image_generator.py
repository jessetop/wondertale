"""
Image Generation Service
Handles AI-powered image creation for story illustrations using Hugging Face Stable Diffusion (Free)
"""

import os
import re
import base64
from typing import Optional
from io import BytesIO

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests package not installed. Image generation will be disabled.")
    # Create a dummy requests module for testing
    requests = None

from models import GeneratedStory


class ImageGenerator:
    """Service for generating story illustrations using Hugging Face Stable Diffusion (Free)"""
    
    def __init__(self):
        """Initialize the image generator with Hugging Face API"""
        self.api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        self.headers = {}
        self._setup_huggingface()
        
        # Simple prompt templates for each topic
        self.prompt_templates = {
            "space": "A colorful, child-friendly cartoon illustration of {characters} exploring space with {keywords}. Disney-style, bright colors, planets and stars, no scary elements, suitable for children ages 3-10",
            "community": "A warm, cheerful cartoon illustration of {characters} in a friendly neighborhood with {keywords}. Child-friendly style, bright colors, houses and gardens, suitable for children ages 3-10",
            "dragons": "A cute, friendly cartoon dragon adventure with {characters} and {keywords}. Colorful, magical, Disney-style, no scary elements, suitable for children ages 3-10",
            "fairies": "A magical fairy garden cartoon scene with {characters} discovering {keywords}. Sparkly, colorful, enchanted forest, child-appropriate style, suitable for children ages 3-10"
        }
    
    def _setup_huggingface(self):
        """Setup Hugging Face API headers"""
        if not REQUESTS_AVAILABLE:
            print("Requests not available - image generation disabled")
            return
            
        # Hugging Face API token (optional for free tier, but recommended)
        hf_token = os.getenv('HUGGINGFACE_API_TOKEN')
        if hf_token:
            self.headers = {"Authorization": f"Bearer {hf_token}"}
        else:
            print("Info: No HUGGINGFACE_API_TOKEN found. Using free tier (may have rate limits).")
    
    def generate_illustration(self, story: GeneratedStory, topic: str) -> Optional[str]:
        """
        Generate a child-friendly illustration for the story using Hugging Face Stable Diffusion (Free)
        Requirements: 5.1 - provide option to create accompanying illustration
        Requirements: 5.4 - handle failed image generation gracefully
        """
        if not REQUESTS_AVAILABLE or requests is None:
            print("Requests library not available - skipping image generation")
            return None
        
        try:
            # Create simple prompt using template
            prompt = self._create_simple_prompt(story, topic)
            
            # Make request to Hugging Face API
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": prompt},
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                # Save image data and return a local path or base64 data URL
                image_data = response.content
                
                # For MVP, we'll return a data URL that can be used directly in HTML
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                data_url = f"data:image/png;base64,{image_base64}"
                
                print(f"Successfully generated image using Hugging Face")
                return data_url
                
            elif response.status_code == 503:
                print("Hugging Face model is loading, please try again in a few minutes")
                return None
            else:
                print(f"Hugging Face API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            if "requests" in str(e).lower():
                print("Requests library not available - skipping image generation")
            else:
                print(f"Error generating image with Hugging Face: {e}")
            # Gracefully handle failed image generation (Requirement 5.4)
            return None
    
    def _create_simple_prompt(self, story: GeneratedStory, topic: str) -> str:
        """
        Create a simple, child-safe image prompt using templates
        Requirements: 5.2 - ensure visual content is child-appropriate and matches story theme
        Requirements: 5.3 - incorporate key story elements and selected topic
        Requirements: 5.5 - generate colorful and appealing images for children ages 3-10
        """
        # Get character names
        character_names = [char.name for char in story.characters]
        characters_text = " and ".join(character_names)
        
        # Get first few keywords from story content for context
        story_words = story.content.lower().split()
        keywords = []
        positive_words = ["adventure", "friendship", "magic", "wonder", "discovery", "help", "kind", "brave", "happy", "joy"]
        
        for word in story_words:
            if word in positive_words and word not in keywords:
                keywords.append(word)
            if len(keywords) >= 3:
                break
        
        if not keywords:
            keywords = ["adventure", "friendship", "magic"]
        
        keywords_text = ", ".join(keywords)
        
        # Use template for the topic
        template = self.prompt_templates.get(topic, self.prompt_templates["space"])
        
        # Fill in the template
        prompt = template.format(
            characters=characters_text,
            keywords=keywords_text
        )
        
        # Ensure prompt is child-safe and not too long
        prompt = self._sanitize_for_image_prompt(prompt)
        
        # Keep prompt under 200 characters for better results with free tier
        if len(prompt) > 200:
            prompt = prompt[:200]
        
        return prompt
    
    def _sanitize_for_image_prompt(self, text: str) -> str:
        """Remove potentially inappropriate content from image prompts"""
        # List of words to avoid in image generation
        inappropriate_words = [
            "scary", "frightening", "frightened", "dark", "violent", "angry", "sad", "crying",
            "monster", "ghost", "demon", "evil", "death", "hurt", "pain", "blood",
            "weapon", "gun", "knife", "sword", "fight", "battle", "war"
        ]
        
        # Replace inappropriate words with positive alternatives
        sanitized_text = text.lower()
        for word in inappropriate_words:
            sanitized_text = sanitized_text.replace(word, "happy")
        
        # Remove any remaining problematic patterns
        sanitized_text = re.sub(r'\b(very|extremely|super)\s+(scary|dark|frightening)\b', 'wonderful', sanitized_text)
        
        return sanitized_text
    
    def _validate_image_content(self, image_data: bytes) -> bool:
        """
        Validate that generated image is appropriate for children
        This is a placeholder for future content validation
        Requirements: 5.2 - ensure visual content is child-appropriate
        """
        # For MVP, we trust the prompt engineering and Stable Diffusion's safety filters
        return image_data is not None and len(image_data) > 0