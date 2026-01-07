#!/usr/bin/env python3
"""
Test script to generate a story and see the OpenAI prompt/response
"""

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("DEBUG: Environment variables loaded from .env file")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables may not load from .env file")

import os
from services.story_generator import StoryGenerator
from models import StoryRequest, Character

def test_story_generation():
    """Test story generation with logging"""
    
    # Create test characters
    characters = [
        Character(name="Alex", pronouns="they/them"),
        Character(name="Sam", pronouns="she/her")
    ]
    
    # Create test request
    request = StoryRequest(
        characters=characters,
        topic="underwater",
        keywords=["bow", "map", "dragon"],  # magic_tool, adventure_pack, animal_friend
        age_group="5-6",
        story_length="long"
    )
    
    print("Testing story generation with the following parameters:")
    print(f"Characters: {[f'{c.name} ({c.pronouns})' for c in characters]}")
    print(f"Topic: {request.topic}")
    print(f"Items: {request.keywords}")
    print(f"Age: {request.age_group}")
    print(f"Length: {request.story_length}")
    print("\n" + "="*50 + "\n")
    
    # Generate story
    generator = StoryGenerator()
    story = generator.generate_story(request)
    
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print(f"Title: {story.title}")
    print(f"Word Count: {story.word_count}")
    print(f"Target Range: {story.target_word_range}")
    print("="*50)

if __name__ == "__main__":
    test_story_generation()