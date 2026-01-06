"""
Data models for the Children's Story Generator application.
Includes Character and StoryRequest models with validation.
"""

import re
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Character:
    """Represents a character in the story with name and pronoun validation."""
    name: str
    pronouns: str
    
    def __post_init__(self):
        """Validate character data after initialization."""
        if not self.validate_name():
            raise ValueError(f"Invalid character name: '{self.name}'. Names must contain only letters and spaces.")
        if not self.validate_pronouns():
            raise ValueError(f"Invalid pronouns: '{self.pronouns}'. Must be one of: he/him, she/her, they/them")
    
    def validate_name(self) -> bool:
        """Validate that character name contains only letters and spaces."""
        if not self.name or not isinstance(self.name, str):
            return False
        # Check if name contains only letters and spaces, and is not empty after stripping
        return bool(re.match(r'^[A-Za-z\s]+$', self.name.strip())) and len(self.name.strip()) > 0
    
    def validate_pronouns(self) -> bool:
        """Validate that pronouns are one of the allowed options."""
        valid_pronouns = {"he/him", "she/her", "they/them"}
        return self.pronouns in valid_pronouns


@dataclass
class StoryRequest:
    """Represents a request to generate a story with comprehensive validation."""
    characters: List[Character]
    topic: str
    keywords: List[str]
    include_image: bool = False
    
    def validate(self) -> List[str]:
        """Return list of validation errors, empty list if valid."""
        errors = []
        
        # Validate characters
        if not self.characters:
            errors.append("At least one character is required")
        elif len(self.characters) > 5:
            errors.append("Maximum 5 characters allowed")
        
        # Validate each character
        for i, character in enumerate(self.characters):
            try:
                # Character validation happens in __post_init__
                pass
            except ValueError as e:
                errors.append(f"Character {i+1}: {str(e)}")
        
        # Validate topic
        valid_topics = {"space", "community", "dragons", "fairies"}
        if self.topic not in valid_topics:
            errors.append(f"Invalid topic: '{self.topic}'. Must be one of: {', '.join(valid_topics)}")
        
        # Validate keywords count (must be exactly 3 or 5)
        if len(self.keywords) not in [3, 5]:
            errors.append(f"Invalid keyword count: {len(self.keywords)}. Must provide exactly 3 or 5 keywords")
        
        # Validate keywords are not empty
        for i, keyword in enumerate(self.keywords):
            if not keyword or not keyword.strip():
                errors.append(f"Keyword {i+1} cannot be empty")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if the story request is valid."""
        return len(self.validate()) == 0


@dataclass
class GeneratedStory:
    """Represents a generated story with metadata."""
    id: str
    title: str
    content: str
    moral: str
    characters: List[Character]
    topic: str
    image_url: Optional[str]
    created_at: datetime
    word_count: int
    
    @classmethod
    def create(cls, title: str, content: str, moral: str, 
               characters: List[Character], topic: str, 
               image_url: Optional[str] = None) -> 'GeneratedStory':
        """Create a new GeneratedStory with auto-generated metadata."""
        import uuid
        
        return cls(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            moral=moral,
            characters=characters,
            topic=topic,
            image_url=image_url,
            created_at=datetime.now(),
            word_count=len(content.split()) if content else 0
        )