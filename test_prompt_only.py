#!/usr/bin/env python3
"""
Test script to show what prompt would be sent to OpenAI
"""

import os
from services.story_generator import StoryGenerator
from models import Character, StoryRequest

def show_openai_prompt():
    """Show the exact prompt that would be sent to OpenAI"""
    print("=== OpenAI Prompt Test ===")
    
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
    
    # Create generator and get the prompt
    generator = StoryGenerator()
    prompt = generator._create_story_prompt(request)
    
    print(f"\n=== EXACT PROMPT SENT TO OPENAI GPT-4 ===")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    
    print(f"\nPrompt length: {len(prompt)} characters")
    print(f"Estimated tokens: ~{len(prompt.split()) * 1.3:.0f}")

if __name__ == "__main__":
    show_openai_prompt()