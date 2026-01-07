#!/usr/bin/env python3
"""
Quick test to verify word count ranges for different age groups and story lengths
"""

from models import StoryRequest, Character

def test_word_count_ranges():
    """Test that word count ranges are appropriate for each age group"""
    
    # Create a sample character for testing
    test_character = Character(name="Alex", pronouns="they/them")
    
    # Test all combinations
    age_groups = ["3-4", "5-6", "7-8", "9-10"]
    story_lengths = ["short", "medium", "long"]
    
    print("Word Count Ranges by Age Group and Story Length:")
    print("=" * 60)
    
    for age_group in age_groups:
        print(f"\nAge Group: {age_group}")
        print("-" * 30)
        
        for story_length in story_lengths:
            # Create a test request
            request = StoryRequest(
                characters=[test_character],
                topic="space",
                keywords=["wand", "backpack", "wolf"],
                age_group=age_group,
                story_length=story_length
            )
            
            min_words, max_words = request.get_target_word_count_range()
            print(f"  {story_length.capitalize():6}: {min_words:3d} - {max_words:3d} words")

if __name__ == "__main__":
    test_word_count_ranges()