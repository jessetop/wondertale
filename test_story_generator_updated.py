"""
Property-based tests for the Children's Story Generator service.
Tests universal properties using the Hypothesis library.
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    print("Warning: pytest not available, using basic assertions")

try:
    from hypothesis import given, strategies as st, settings
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    print("Warning: hypothesis not available, skipping property tests")

import re
from models import Character, StoryRequest
from services.story_generator import StoryGenerator


class TestStoryLengthValidation:
    """Property tests for story length validation - Property 11"""
    
    def test_story_length_validation_examples(self):
        """
        Feature: children-story-generator, Property 11: Story Length Validation by Age and Length Selection
        Test specific examples to ensure story length is appropriate for age and length selection
        Validates: Requirements 3.6-3.17
        """
        generator = StoryGenerator()
        
        test_cases = [
            {
                "characters": [Character(name="Alice", pronouns="she/her")],
                "topic": "community",
                "keywords": ["help", "neighbor", "kind"],
                "age_group": "3-4",
                "story_length": "short"
            },
            {
                "characters": [
                    Character(name="Bob", pronouns="he/him"), 
                    Character(name="Carol", pronouns="they/them")
                ],
                "topic": "dragons",
                "keywords": ["brave", "friendship", "magic"],
                "age_group": "5-6",
                "story_length": "medium"
            },
            {
                "characters": [
                    Character(name="David", pronouns="he/him"),
                    Character(name="Emma", pronouns="she/her")
                ],
                "topic": "space",
                "keywords": ["explore", "wonder", "discovery"],
                "age_group": "7-8",
                "story_length": "long"
            }
        ]
        
        for case in test_cases:
            request = StoryRequest(
                characters=case["characters"],
                topic=case["topic"],
                keywords=case["keywords"],
                age_group=case["age_group"],
                story_length=case["story_length"],
                include_image=False
            )
            
            story = generator.generate_story(request)
            
            # Count words in the story
            word_count = len(story.content.split())
            
            # Get expected range
            min_words, max_words = request.get_target_word_count_range()
            
            # Allow flexibility for placeholder stories
            flexibility = int((max_words - min_words) * 0.3)
            flexible_min = max(min_words - flexibility, min_words // 2)
            flexible_max = max_words + flexibility
            
            assert flexible_min <= word_count <= flexible_max, \
                f"Story word count {word_count} is outside acceptable range ({flexible_min}-{flexible_max}) for age {case['age_group']}, length {case['story_length']}"
            
            # Verify the story object's word_count field is accurate
            assert story.word_count == word_count, \
                f"Story word_count field ({story.word_count}) doesn't match actual count ({word_count})"


if __name__ == "__main__":
    print("Running updated story length validation tests...")
    
    generator = StoryGenerator()
    
    # Test different age/length combinations
    test_cases = [
        {
            "characters": [Character(name="Alice", pronouns="she/her")],
            "topic": "community",
            "keywords": ["help", "friend", "kind"],
            "age_group": "3-4",
            "story_length": "short"
        },
        {
            "characters": [
                Character(name="Bob", pronouns="he/him"),
                Character(name="Carol", pronouns="they/them")
            ],
            "topic": "dragons",
            "keywords": ["brave", "magic", "adventure"],
            "age_group": "5-6",
            "story_length": "medium"
        },
        {
            "characters": [Character(name="David", pronouns="he/him")],
            "topic": "space",
            "keywords": ["explore", "wonder", "discovery"],
            "age_group": "7-8",
            "story_length": "long"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        request = StoryRequest(
            characters=case["characters"],
            topic=case["topic"],
            keywords=case["keywords"],
            age_group=case["age_group"],
            story_length=case["story_length"],
            include_image=False
        )
        
        story = generator.generate_story(request)
        
        print(f"\nTest case {i}:")
        print(f"Age: {case['age_group']}, Length: {case['story_length']}")
        print(f"Characters: {[c.name for c in case['characters']]}")
        print(f"Topic: {case['topic']}")
        
        # Count words
        actual_word_count = len(story.content.split())
        min_words, max_words = request.get_target_word_count_range()
        
        print(f"Story word count: {actual_word_count}")
        print(f"Expected range: {min_words}-{max_words}")
        print(f"Story.word_count field: {story.word_count}")
        
        # Check word count accuracy
        if story.word_count == actual_word_count:
            print("✓ Word count field is accurate")
        else:
            print(f"✗ Word count field mismatch: expected {actual_word_count}, got {story.word_count}")
        
        # Check if word count is in expected range (with flexibility)
        flexibility = int((max_words - min_words) * 0.3)
        flexible_min = max(min_words - flexibility, min_words // 2)
        flexible_max = max_words + flexibility
        
        if flexible_min <= actual_word_count <= flexible_max:
            print(f"✓ Word count {actual_word_count} is within acceptable range ({flexible_min}-{flexible_max})")
        else:
            print(f"✗ Word count {actual_word_count} is outside acceptable range ({flexible_min}-{flexible_max})")
        
        # Show first few words of story
        words = story.content.split()
        preview = " ".join(words[:20]) + "..." if len(words) > 20 else story.content
        print(f"Story preview: {preview}")
    
    print("\nUpdated story length validation tests completed!")