#!/usr/bin/env python3
"""
Test script to check OpenAI configuration and generate a sample story
"""

import os
import sys
from dotenv import load_dotenv
from services.story_generator import StoryGenerator
from models import Character, StoryRequest

# Load environment variables from .env file
load_dotenv()

def test_openai_setup():
    """Test if OpenAI is properly configured"""
    print("=== OpenAI Configuration Check ===")
    
    # Check environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"OPENAI_API_KEY found: {'Yes' if api_key and api_key != 'your_openai_api_key_here' else 'No'}")
    
    if api_key == 'your_openai_api_key_here':
        print("❌ API key is still the placeholder value")
        return False
    elif not api_key:
        print("❌ No API key found in environment")
        return False
    else:
        print(f"✅ API key configured (starts with: {api_key[:10]}...)")
        return True

def test_story_generation():
    """Generate a test story to see the current output"""
    print("\n=== Story Generation Test ===")
    
    # Create a test story request
    character = Character(name="Emma", pronouns="she/her")
    request = StoryRequest(
        characters=[character],
        topic="space",
        age_group="5-6",
        story_length="medium",
        keywords=["wand", "backpack", "wolf"]
    )
    
    print(f"Test request: {character.name} ({character.pronouns}), {request.topic}, ages {request.age_group}")
    
    # Generate story
    generator = StoryGenerator()
    story = generator.generate_story(request)
    
    print(f"\n=== Generated Story ===")
    print(f"Title: {story.title}")
    print(f"Word count: {len(story.content.split())} words")
    print(f"Target range: {story.target_word_range}")
    print(f"\nContent:")
    print("-" * 50)
    print(story.content)
    print("-" * 50)
    print(f"\nMoral: {story.moral}")
    
    # Check if this looks like a placeholder story
    is_placeholder = (
        "Once upon a time" in story.content and 
        len(story.content.split()) < 100 and
        story.content.count("They ") > 5
    )
    
    print(f"\nAnalysis:")
    print(f"Appears to be placeholder story: {'Yes' if is_placeholder else 'No'}")
    
    return story

if __name__ == "__main__":
    print("WonderTale Story Generation Test")
    print("=" * 40)
    
    # Test OpenAI setup
    openai_configured = test_openai_setup()
    
    # Generate test story
    story = test_story_generation()
    
    print(f"\n=== Summary ===")
    if not openai_configured:
        print("❌ OpenAI not properly configured - using placeholder stories")
        print("To fix: Set a real OpenAI API key in the .env file")
    else:
        print("✅ OpenAI configured - should generate real stories")