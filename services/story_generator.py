"""
Story Generation Service
Handles AI-powered story creation with OpenAI GPT
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Story generation will use placeholder content.")

@dataclass
class Character:
    """Represents a story character"""
    name: str
    pronouns: str
    
    def validate(self) -> bool:
        """Validate character data"""
        import re
        return bool(re.match(r'^[A-Za-z\s]+$', self.name.strip()))

@dataclass
class StoryRequest:
    """Represents a story generation request"""
    characters: List[Character]
    topic: str
    keywords: List[str]
    include_image: bool = False
    
    def validate(self) -> List[str]:
        """Return list of validation errors"""
        errors = []
        
        # Validate characters
        if not self.characters:
            errors.append("At least one character is required")
        
        for i, char in enumerate(self.characters, 1):
            if not char.validate():
                errors.append(f"Character {i} name is invalid")
            if char.pronouns not in ["he/him", "she/her", "they/them"]:
                errors.append(f"Character {i} pronouns are invalid")
        
        # Validate topic
        valid_topics = ["space", "community", "dragons", "fairies"]
        if self.topic not in valid_topics:
            errors.append("Invalid topic selected")
        
        # Validate keywords
        if len(self.keywords) not in [3, 5]:
            errors.append("Must provide exactly 3 or 5 keywords")
        
        return errors

@dataclass
class GeneratedStory:
    """Represents a generated story"""
    id: str
    title: str
    content: str
    moral: str
    characters: List[Character]
    topic: str
    image_url: Optional[str]
    created_at: datetime
    word_count: int

class StoryGenerator:
    """Service for generating children's stories using OpenAI"""
    
    def __init__(self):
        """Initialize the story generator"""
        self.client = None
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        if not OPENAI_AVAILABLE:
            print("OpenAI not available - using placeholder mode")
            return
            
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.client = openai
        else:
            print("Warning: OPENAI_API_KEY not found in environment variables")
    
    def generate_story(self, request: StoryRequest) -> GeneratedStory:
        """Generate a story based on the request"""
        # Validate request
        errors = request.validate()
        if errors:
            raise ValueError(f"Invalid request: {', '.join(errors)}")
        
        # This will be implemented in later tasks
        # For now, return a placeholder story
        return GeneratedStory(
            id="placeholder-001",
            title="Your Amazing Adventure",
            content="This is a placeholder story. Story generation will be implemented in task 4.",
            moral="Always be kind to others.",
            characters=request.characters,
            topic=request.topic,
            image_url=None,
            created_at=datetime.now(),
            word_count=50
        )