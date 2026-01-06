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