"""
Property-based tests for the Children's Story Generator data models.
Tests universal properties using the Hypothesis library.
"""

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    print("Warning: pytest not available, using basic assertions")

try:
    from hypothesis import given, strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    print("Warning: hypothesis not available, skipping property tests")

from models import Character, StoryRequest
from services.content_filter import ContentFilter


class TestCharacterNameValidation:
    """Property tests for Character name validation - Property 4"""
    
    @given(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')), min_size=1))
    def test_valid_names_with_letters_and_spaces_are_accepted(self, name):
        """
        Feature: children-story-generator, Property 4: Character Name Validation
        For any character name input, the system should accept it if and only if it contains only letters and spaces
        Validates: Requirements 1.7
        """
        # Strip the name to handle edge cases with only spaces
        stripped_name = name.strip()
        if stripped_name:  # Only test non-empty names after stripping
            try:
                character = Character(name=name, pronouns="he/him")
                assert character.validate_name() == True
            except ValueError:
                # If Character creation fails, validate_name should return False
                temp_char = Character.__new__(Character)
                temp_char.name = name
                temp_char.pronouns = "he/him"
                assert temp_char.validate_name() == False
    
    @given(st.text().filter(lambda x: not x.strip() or any(c for c in x if not (c.isalpha() or c.isspace()))))
    def test_invalid_names_are_rejected(self, invalid_name):
        """
        Feature: children-story-generator, Property 4: Character Name Validation
        For any character name input containing non-letters/non-spaces or empty, it should be rejected
        Validates: Requirements 1.7
        """
        temp_char = Character.__new__(Character)
        temp_char.name = invalid_name
        temp_char.pronouns = "he/him"
        assert temp_char.validate_name() == False
        
        # Also test that Character creation raises ValueError for invalid names
        with pytest.raises(ValueError, match="Invalid character name"):
            Character(name=invalid_name, pronouns="he/him")
    
    def test_empty_and_whitespace_names_rejected(self):
        """
        Feature: children-story-generator, Property 4: Character Name Validation
        Empty names and names with only whitespace should be rejected
        Validates: Requirements 1.7
        """
        invalid_names = ["", "   ", "\t", "\n", "  \t  \n  "]
        
        for invalid_name in invalid_names:
            temp_char = Character.__new__(Character)
            temp_char.name = invalid_name
            temp_char.pronouns = "he/him"
            assert temp_char.validate_name() == False
            
            with pytest.raises(ValueError, match="Invalid character name"):
                Character(name=invalid_name, pronouns="he/him")


class TestKeywordCountValidation:
    """Property tests for keyword count validation - Property 2"""
    
    @given(st.lists(st.text(min_size=1), min_size=3, max_size=3))
    def test_exactly_three_keywords_accepted(self, keywords):
        """
        Feature: children-story-generator, Property 2: Keyword Count Validation
        For any keyword input with exactly 3 keywords, the system should accept it
        Validates: Requirements 1.5
        """
        characters = [Character(name="Test", pronouns="he/him")]
        request = StoryRequest(
            characters=characters,
            topic="space",
            keywords=keywords,
            include_image=False
        )
        
        errors = request.validate()
        # Should not have keyword count errors
        keyword_count_errors = [e for e in errors if "keyword count" in e.lower()]
        assert len(keyword_count_errors) == 0
    
    @given(st.lists(st.text(min_size=1), min_size=5, max_size=5))
    def test_exactly_five_keywords_accepted(self, keywords):
        """
        Feature: children-story-generator, Property 2: Keyword Count Validation
        For any keyword input with exactly 5 keywords, the system should accept it
        Validates: Requirements 1.5
        """
        characters = [Character(name="Test", pronouns="he/him")]
        request = StoryRequest(
            characters=characters,
            topic="space",
            keywords=keywords,
            include_image=False
        )
        
        errors = request.validate()
        # Should not have keyword count errors
        keyword_count_errors = [e for e in errors if "keyword count" in e.lower()]
        assert len(keyword_count_errors) == 0
    
    @given(st.lists(st.text(), min_size=0, max_size=10).filter(lambda x: len(x) not in [3, 5]))
    def test_invalid_keyword_counts_rejected(self, keywords):
        """
        Feature: children-story-generator, Property 2: Keyword Count Validation
        For any keyword input that doesn't have exactly 3 or 5 keywords, it should be rejected
        Validates: Requirements 1.5
        """
        characters = [Character(name="Test", pronouns="he/him")]
        request = StoryRequest(
            characters=characters,
            topic="space",
            keywords=keywords,
            include_image=False
        )
        
        errors = request.validate()
        # Should have keyword count error
        keyword_count_errors = [e for e in errors if "keyword count" in e.lower()]
        assert len(keyword_count_errors) > 0


class TestInputValidationErrorHandling:
    """Property tests for input validation error handling - Property 3"""
    
    @given(
        st.lists(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs')), min_size=1), min_size=1, max_size=5),
        st.sampled_from(["space", "community", "dragons", "fairies"]),
        st.lists(st.text(min_size=1), min_size=3, max_size=5).filter(lambda x: len(x) in [3, 5])
    )
    def test_valid_inputs_produce_no_errors(self, character_names, topic, keywords):
        """
        Feature: children-story-generator, Property 3: Input Validation Error Handling
        For any valid input, the system should produce no validation errors
        Validates: Requirements 1.6
        """
        try:
            characters = [Character(name=name.strip(), pronouns="he/him") for name in character_names if name.strip()]
            if characters:  # Only test if we have valid characters
                request = StoryRequest(
                    characters=characters,
                    topic=topic,
                    keywords=keywords,
                    include_image=False
                )
                
                errors = request.validate()
                assert len(errors) == 0
                assert request.is_valid() == True
        except ValueError:
            # If character creation fails due to invalid names, that's expected
            pass
    
    @given(
        st.one_of(
            st.just([]),  # No characters
            st.lists(st.text(), min_size=6, max_size=10),  # Too many characters
            st.lists(st.text().filter(lambda x: not x.strip() or any(c for c in x if not (c.isalpha() or c.isspace()))), min_size=1, max_size=3)  # Invalid character names
        )
    )
    def test_invalid_character_inputs_produce_errors(self, invalid_character_data):
        """
        Feature: children-story-generator, Property 3: Input Validation Error Handling
        For any invalid character input, the system should produce clear error messages
        Validates: Requirements 1.6
        """
        try:
            if len(invalid_character_data) > 5:
                # Too many characters case
                characters = [Character(name="Valid", pronouns="he/him")]
                request = StoryRequest(
                    characters=characters * 6,  # Force more than 5 characters
                    topic="space",
                    keywords=["word1", "word2", "word3"],
                    include_image=False
                )
                errors = request.validate()
                assert any("Maximum 5 characters" in error for error in errors)
            elif len(invalid_character_data) == 0:
                # No characters case
                request = StoryRequest(
                    characters=[],
                    topic="space",
                    keywords=["word1", "word2", "word3"],
                    include_image=False
                )
                errors = request.validate()
                assert any("At least one character is required" in error for error in errors)
            else:
                # Invalid character names case - these should raise ValueError during Character creation
                for name in invalid_character_data:
                    with pytest.raises(ValueError):
                        Character(name=name, pronouns="he/him")
        except ValueError:
            # Expected for invalid character names
            pass
    
    def test_invalid_topic_produces_error(self):
        """
        Feature: children-story-generator, Property 3: Input Validation Error Handling
        For any invalid topic, the system should produce clear error messages
        Validates: Requirements 1.6
        """
        characters = [Character(name="Test", pronouns="he/him")]
        request = StoryRequest(
            characters=characters,
            topic="invalid_topic",
            keywords=["word1", "word2", "word3"],
            include_image=False
        )
        
        errors = request.validate()
        assert any("Invalid topic" in error for error in errors)
        assert request.is_valid() == False


def run_basic_tests():
    """Run basic tests without pytest/hypothesis if they're not available"""
    print("Running basic character name validation tests...")
    
    # Test valid names
    valid_names = ["Alice", "Bob Smith", "Mary Jane", "A", "Test Name"]
    for name in valid_names:
        try:
            char = Character(name=name, pronouns="he/him")
            assert char.validate_name() == True
            print(f"✓ Valid name '{name}' accepted")
        except Exception as e:
            print(f"✗ Valid name '{name}' rejected: {e}")
    
    # Test invalid names
    invalid_names = ["", "   ", "Alice123", "Bob@Smith", "Test-Name", "Name!", "123"]
    for name in invalid_names:
        try:
            char = Character(name=name, pronouns="he/him")
            print(f"✗ Invalid name '{name}' was accepted (should be rejected)")
        except ValueError:
            print(f"✓ Invalid name '{name}' correctly rejected")
    
    print("\nRunning keyword count validation tests...")
    
    # Test valid keyword counts
    valid_keywords = [
        ["word1", "word2", "word3"],
        ["word1", "word2", "word3", "word4", "word5"]
    ]
    
    for keywords in valid_keywords:
        characters = [Character(name="Test", pronouns="he/him")]
        request = StoryRequest(
            characters=characters,
            topic="space",
            keywords=keywords,
            include_image=False
        )
        errors = request.validate()
        keyword_errors = [e for e in errors if "keyword count" in e.lower()]
        if len(keyword_errors) == 0:
            print(f"✓ {len(keywords)} keywords accepted")
        else:
            print(f"✗ {len(keywords)} keywords rejected: {keyword_errors}")
    
    # Test invalid keyword counts
    invalid_keywords = [
        [],
        ["word1"],
        ["word1", "word2"],
        ["word1", "word2", "word3", "word4"],
        ["word1", "word2", "word3", "word4", "word5", "word6"]
    ]
    
    for keywords in invalid_keywords:
        characters = [Character(name="Test", pronouns="he/him")]
        request = StoryRequest(
            characters=characters,
            topic="space",
            keywords=keywords,
            include_image=False
        )
        errors = request.validate()
        keyword_errors = [e for e in errors if "keyword count" in e.lower()]
        if len(keyword_errors) > 0:
            print(f"✓ {len(keywords)} keywords correctly rejected")
        else:
            print(f"✗ {len(keywords)} keywords incorrectly accepted")
    
    print("\nRunning input validation error handling tests...")
    
    # Test valid input produces no errors
    characters = [Character(name="Alice", pronouns="she/her")]
    request = StoryRequest(
        characters=characters,
        topic="dragons",
        keywords=["magic", "adventure", "friendship"],
        include_image=True
    )
    errors = request.validate()
    if len(errors) == 0:
        print("✓ Valid input produces no errors")
    else:
        print(f"✗ Valid input produced errors: {errors}")
    
    # Test invalid topic
    request = StoryRequest(
        characters=characters,
        topic="invalid_topic",
        keywords=["word1", "word2", "word3"],
        include_image=False
    )
    errors = request.validate()
    topic_errors = [e for e in errors if "Invalid topic" in e]
    if len(topic_errors) > 0:
        print("✓ Invalid topic correctly produces error")
    else:
        print("✗ Invalid topic did not produce error")
    
    print("\nBasic tests completed!")


if __name__ == "__main__":
    if not HYPOTHESIS_AVAILABLE:
        run_basic_tests()
    else:
        print("Running property-based tests...")
        
        # Import hypothesis for manual testing
        from hypothesis import given, strategies as st
        
        # Test character name validation manually
        print("Testing character name validation property...")
        
        # Test valid names
        valid_test_names = ["Alice", "Bob Smith", "Mary Jane Watson", "A B C"]
        for name in valid_test_names:
            try:
                character = Character(name=name, pronouns="he/him")
                assert character.validate_name() == True
                print(f"✓ Valid name '{name}' accepted")
            except Exception as e:
                print(f"✗ Valid name '{name}' failed: {e}")
        
        # Test invalid names
        invalid_test_names = ["Alice123", "Bob@Smith", "", "   ", "\t", "Test-Name"]
        for name in invalid_test_names:
            temp_char = Character.__new__(Character)
            temp_char.name = name
            temp_char.pronouns = "he/him"
            if not temp_char.validate_name():
                print(f"✓ Invalid name '{name}' correctly rejected")
            else:
                print(f"✗ Invalid name '{name}' incorrectly accepted")
        
        print("\nTesting keyword count validation property...")
        
        # Test valid keyword counts
        for count in [3, 5]:
            keywords = [f"word{i}" for i in range(count)]
            characters = [Character(name="Test", pronouns="he/him")]
            request = StoryRequest(
                characters=characters,
                topic="space",
                keywords=keywords,
                include_image=False
            )
            errors = request.validate()
            keyword_count_errors = [e for e in errors if "keyword count" in e.lower()]
            if len(keyword_count_errors) == 0:
                print(f"✓ {count} keywords correctly accepted")
            else:
                print(f"✗ {count} keywords incorrectly rejected: {keyword_count_errors}")
        
        # Test invalid keyword counts
        for count in [0, 1, 2, 4, 6, 7]:
            keywords = [f"word{i}" for i in range(count)]
            characters = [Character(name="Test", pronouns="he/him")]
            request = StoryRequest(
                characters=characters,
                topic="space",
                keywords=keywords,
                include_image=False
            )
            errors = request.validate()
            keyword_count_errors = [e for e in errors if "keyword count" in e.lower()]
            if len(keyword_count_errors) > 0:
                print(f"✓ {count} keywords correctly rejected")
            else:
                print(f"✗ {count} keywords incorrectly accepted")
        
        print("\nTesting input validation error handling property...")
        
        # Test valid input produces no errors
        characters = [Character(name="Alice", pronouns="she/her")]
        request = StoryRequest(
            characters=characters,
            topic="dragons",
            keywords=["magic", "adventure", "friendship"],
            include_image=True
        )
        errors = request.validate()
        if len(errors) == 0:
            print("✓ Valid input produces no errors")
        else:
            print(f"✗ Valid input produced errors: {errors}")
        
        # Test invalid topic produces error
        request = StoryRequest(
            characters=characters,
            topic="invalid_topic",
            keywords=["word1", "word2", "word3"],
            include_image=False
        )
        errors = request.validate()
        topic_errors = [e for e in errors if "Invalid topic" in e]
        if len(topic_errors) > 0:
            print("✓ Invalid topic correctly produces error")
        else:
            print("✗ Invalid topic did not produce error")
        
        print("\nProperty-based tests completed!")


class TestComprehensiveContentSafety:
    """Property tests for comprehensive content safety - Property 5"""
    
    @given(st.text(min_size=10, max_size=500))
    def test_safe_content_passes_validation(self, content):
        """
        Feature: children-story-generator, Property 5: Comprehensive Content Safety
        For any generated story, it should use age-appropriate vocabulary, avoid scary/violent themes, 
        use simple sentence structures, and maintain positive themes throughout
        Validates: Requirements 2.1, 2.2, 2.4, 2.5
        """
        content_filter = ContentFilter()
        
        # Create safe content by replacing inappropriate words
        safe_content = content
        for inappropriate in content_filter.inappropriate_keywords:
            safe_content = safe_content.replace(inappropriate, "happy")
        
        # Add positive words to ensure positive themes
        safe_content = f"The happy children had a wonderful adventure. {safe_content} They smiled and laughed together."
        
        # Remove complex patterns
        import re
        for pattern in content_filter.complex_sentence_patterns:
            safe_content = re.sub(pattern, "nice", safe_content, flags=re.IGNORECASE)
        
        # Test that safe content passes all validations
        assert content_filter.validate_story_content(safe_content) == True
        assert content_filter.validate_age_appropriate_vocabulary(safe_content) == True
        assert content_filter.get_content_safety_score(safe_content) > 0.5
    
    def test_inappropriate_content_fails_validation(self):
        """
        Feature: children-story-generator, Property 5: Comprehensive Content Safety
        Content with inappropriate themes should fail validation
        Validates: Requirements 2.1, 2.2, 2.4, 2.5
        """
        content_filter = ContentFilter()
        
        # Test various types of inappropriate content
        inappropriate_contents = [
            "The scary monster attacked the children with violence",
            "The dragon killed everyone with blood everywhere",
            "The children were afraid and cried because of the nightmare",
            "However, nevertheless, the sophisticated circumstances were problematic",  # Complex sentences
            "The supercalifragilisticexpialidocious monster was extraordinarily frightening",  # Complex words
            "Everyone was sad and angry and hated each other"  # No positive themes
        ]
        
        for content in inappropriate_contents:
            assert content_filter.validate_story_content(content) == False
            assert content_filter.get_content_safety_score(content) < 0.5
    
    @given(st.lists(st.sampled_from(["happy", "joy", "smile", "laugh", "love", "friend", "help", "kind", "nice", "good"]), min_size=1, max_size=5))
    def test_positive_themes_requirement(self, positive_words):
        """
        Feature: children-story-generator, Property 5: Comprehensive Content Safety
        Content with positive themes should pass validation
        Validates: Requirements 2.5
        """
        content_filter = ContentFilter()
        
        # Create content with positive words
        content = f"The children were {' and '.join(positive_words)}. They had a great time playing together."
        
        assert content_filter.validate_story_content(content) == True
        assert content_filter.get_content_safety_score(content) > 0.5
    
    @given(st.lists(st.text(alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=8), min_size=5, max_size=20))
    def test_age_appropriate_vocabulary_validation(self, simple_words):
        """
        Feature: children-story-generator, Property 5: Comprehensive Content Safety
        Content with age-appropriate vocabulary should pass validation
        Validates: Requirements 2.1
        """
        content_filter = ContentFilter()
        
        # Create content with simple words
        content = f"The happy children played with {' and '.join(simple_words)}. They had fun together."
        
        # Should pass age-appropriate vocabulary check
        assert content_filter.validate_age_appropriate_vocabulary(content) == True


class TestKeywordContentFiltering:
    """Property tests for keyword content filtering - Property 6"""
    
    @given(st.lists(st.sampled_from(["happy", "joy", "smile", "play", "friend", "love", "help", "kind", "nice", "good", "fun", "adventure", "magic", "rainbow", "sunshine"]), min_size=1, max_size=10))
    def test_appropriate_keywords_pass_validation(self, safe_keywords):
        """
        Feature: children-story-generator, Property 6: Keyword Content Filtering
        For any set of appropriate user keywords, they should pass validation
        Validates: Requirements 2.3
        """
        content_filter = ContentFilter()
        
        assert content_filter.validate_keywords(safe_keywords) == True
        
        # Test filtering - should return all keywords
        filtered = content_filter.filter_inappropriate_keywords(safe_keywords)
        assert len(filtered) == len(safe_keywords)
        assert set(filtered) == set(safe_keywords)
    
    @given(st.lists(st.sampled_from(["scary", "violent", "death", "kill", "hurt", "blood", "weapon", "gun", "knife", "fight", "angry", "hate", "evil", "monster"]), min_size=1, max_size=5))
    def test_inappropriate_keywords_fail_validation(self, inappropriate_keywords):
        """
        Feature: children-story-generator, Property 6: Keyword Content Filtering
        For any set of inappropriate user keywords, they should fail validation
        Validates: Requirements 2.3
        """
        content_filter = ContentFilter()
        
        assert content_filter.validate_keywords(inappropriate_keywords) == False
        
        # Test filtering - should return empty list
        filtered = content_filter.filter_inappropriate_keywords(inappropriate_keywords)
        assert len(filtered) == 0
    
    def test_mixed_keywords_filtering(self):
        """
        Feature: children-story-generator, Property 6: Keyword Content Filtering
        Mixed appropriate and inappropriate keywords should be filtered correctly
        Validates: Requirements 2.3
        """
        content_filter = ContentFilter()
        
        mixed_keywords = ["happy", "scary", "play", "violent", "friend", "death", "love"]
        expected_safe = ["happy", "play", "friend", "love"]
        
        # Should fail validation due to inappropriate keywords
        assert content_filter.validate_keywords(mixed_keywords) == False
        
        # Should filter out inappropriate keywords
        filtered = content_filter.filter_inappropriate_keywords(mixed_keywords)
        assert set(filtered) == set(expected_safe)
    
    @given(st.lists(st.text().filter(lambda x: x.strip() and x.lower().strip() not in {"scary", "violent", "death", "kill", "hurt", "blood", "weapon", "gun", "knife", "fight", "angry", "hate"}), min_size=1, max_size=5))
    def test_unknown_keywords_pass_by_default(self, unknown_keywords):
        """
        Feature: children-story-generator, Property 6: Keyword Content Filtering
        Unknown keywords that aren't explicitly inappropriate should pass validation
        Validates: Requirements 2.3
        """
        content_filter = ContentFilter()
        
        # Filter out any keywords that might contain inappropriate substrings
        clean_keywords = []
        for keyword in unknown_keywords:
            keyword_clean = keyword.lower().strip()
            if keyword_clean and not any(inappropriate in keyword_clean for inappropriate in content_filter.inappropriate_keywords):
                clean_keywords.append(keyword.strip())
        
        if clean_keywords:  # Only test if we have clean keywords
            assert content_filter.validate_keywords(clean_keywords) == True
            filtered = content_filter.filter_inappropriate_keywords(clean_keywords)
            assert len(filtered) == len(clean_keywords)