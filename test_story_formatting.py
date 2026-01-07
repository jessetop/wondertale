#!/usr/bin/env python3
"""
Test story formatting in the template
"""

from models import Character, StoryRequest, GeneratedStory
from services.story_generator import StoryGenerator

def test_story_formatting():
    """Test story content formatting"""
    print("Testing Story Formatting")
    print("=" * 40)
    
    # Create a test story with different content formats
    test_cases = [
        {
            "name": "Proper paragraph breaks",
            "content": "Once upon a time, Emma went to space.\n\nShe found a magical planet with colorful rings.\n\nEmma used her wand to help the space creatures.\n\nEveryone was happy and Emma learned about friendship."
        },
        {
            "name": "No paragraph breaks",
            "content": "Once upon a time, Emma went to space. She found a magical planet with colorful rings. Emma used her wand to help the space creatures. Everyone was happy and Emma learned about friendship."
        },
        {
            "name": "Mixed formatting",
            "content": "Once upon a time, Emma went to space. She found a magical planet.\n\nEmma used her wand to help the space creatures. Everyone was happy and Emma learned about friendship."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {case['name']} ---")
        print(f"Original content: {repr(case['content'])}")
        
        # Test paragraph splitting logic
        paragraphs = case['content'].split('\n\n')
        print(f"Paragraphs after split('\\n\\n'): {len(paragraphs)}")
        
        if len(paragraphs) > 1:
            print("✅ Has proper paragraph breaks")
            for j, p in enumerate(paragraphs):
                if p.strip():
                    print(f"  Paragraph {j+1}: {repr(p.strip())}")
        else:
            print("⚠️  No paragraph breaks, will use sentence splitting")
            sentences = case['content'].split('. ')
            print(f"Sentences after split('. '): {len(sentences)}")
            
            # Group into paragraphs (3 sentences for ages 5-6)
            paragraph_size = 3
            for j in range(0, len(sentences), paragraph_size):
                paragraph_sentences = sentences[j:j+paragraph_size]
                if paragraph_sentences:
                    paragraph_text = '. '.join(s.strip() for s in paragraph_sentences if s.strip())
                    if not paragraph_text.endswith('.'):
                        paragraph_text += '.'
                    print(f"  Generated paragraph {j//paragraph_size + 1}: {repr(paragraph_text)}")

if __name__ == "__main__":
    test_story_formatting()