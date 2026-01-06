#!/usr/bin/env python3
"""
Test script to verify OpenAI setup after adding API key
"""

import os
from dotenv import load_dotenv
from services.story_generator import StoryGenerator
from models import Character, StoryRequest

# Load environment variables from .env file
load_dotenv()

def test_api_key_setup():
    """Test if API key is properly configured"""
    print("=== OpenAI API Key Check ===")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        print("Make sure you:")
        print("1. Got your API key from https://platform.openai.com/api-keys")
        print("2. Updated the .env file with your real key")
        print("3. Restarted your application/terminal")
        return False
    elif api_key == 'your_actual_openai_api_key_here':
        print("❌ API key is still the placeholder")
        print("Replace 'your_actual_openai_api_key_here' with your real OpenAI API key")
        return False
    elif len(api_key) < 20:
        print("❌ API key looks too short")
        print("OpenAI API keys are usually 51+ characters long")
        return False
    else:
        print(f"✅ API key found (starts with: {api_key[:10]}...)")
        print(f"✅ Key length: {len(api_key)} characters")
        return True

def test_story_generation_ready():
    """Test if story generation is ready to work"""
    print("\n=== Story Generation Readiness ===")
    
    try:
        # Test imports
        from openai import OpenAI
        print("✅ OpenAI package imported successfully")
        
        # Test story generator initialization
        generator = StoryGenerator()
        print("✅ StoryGenerator initialized")
        
        if generator.client:
            print("✅ OpenAI client created successfully")
            print("🎉 Ready to generate real AI stories!")
            return True
        else:
            print("❌ OpenAI client not created (check API key)")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def show_next_steps():
    """Show what to do next"""
    print("\n=== Next Steps ===")
    print("1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
    print("2. Edit the .env file and replace 'your_actual_openai_api_key_here' with your real key")
    print("3. Run this test again: python test_openai_setup.py")
    print("4. Test story generation: python test_story_generation.py")
    print("\n💡 Tip: Your .env file is now protected by .gitignore!")

if __name__ == "__main__":
    print("WonderTale OpenAI Setup Test")
    print("=" * 40)
    
    api_ready = test_api_key_setup()
    
    if api_ready:
        generation_ready = test_story_generation_ready()
        if generation_ready:
            print("\n🎉 Everything is set up correctly!")
            print("Your story generator is ready to create amazing AI stories!")
        else:
            show_next_steps()
    else:
        show_next_steps()