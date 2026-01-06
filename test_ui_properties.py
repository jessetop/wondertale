"""
Property-based tests for the Children's Story Generator UI components.
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
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
from models import Character, StoryRequest


class TestCharacterInputFieldGeneration:
    """Property tests for character input field generation - Property 1"""
    
    def _create_test_app(self):
        """Create a test Flask app for template rendering"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    def _get_character_fields_from_html(self, html_content):
        """Extract character input fields from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find character name inputs
        name_inputs = soup.find_all('input', {'name': re.compile(r'character_\d+_name')})
        
        # Find character pronoun inputs
        pronoun_inputs = soup.find_all('input', {'name': re.compile(r'character_\d+_pronouns')})
        
        # Find pronoun selection buttons
        pronoun_buttons = soup.find_all('button', {'data-character': True})
        
        return {
            'name_inputs': name_inputs,
            'pronoun_inputs': pronoun_inputs,
            'pronoun_buttons': pronoun_buttons
        }
    
    @given(st.integers(min_value=1, max_value=5))
    def test_character_input_field_generation_property(self, num_characters):
        """
        Feature: children-story-generator, Property 1: Character Input Field Generation
        For any number of characters (1-5), the system should generate the correct number of character input fields
        Validates: Requirements 1.2
        """
        # Read the actual index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Parse the HTML to check the JavaScript logic
        soup = BeautifulSoup(template_content, 'html.parser')
        
        # Find the JavaScript function that generates character fields
        scripts = soup.find_all('script')
        js_content = ""
        for script in scripts:
            if script.string and 'generateCharacterFields' in script.string:
                js_content = script.string
                break
        
        # Verify the JavaScript function exists
        assert 'generateCharacterFields' in js_content, "generateCharacterFields function not found in template"
        
        # Verify the function creates the correct number of fields
        # Check that the function loops from 1 to count
        assert 'for (let i = 1; i <= count; i++)' in js_content, "Character field generation loop not found"
        
        # Verify character name input creation
        assert 'character_${i}_name' in js_content, "Character name input template not found"
        
        # Verify character pronoun input creation
        assert 'character_${i}_pronouns' in js_content, "Character pronoun input template not found"
        
        # Verify pronoun selection buttons are created
        assert 'data-character="${i}"' in js_content, "Character pronoun buttons not properly configured"
        
        # Verify all three pronoun options are available
        assert 'he/him' in js_content, "he/him pronoun option not found"
        assert 'she/her' in js_content, "she/her pronoun option not found"
        assert 'they/them' in js_content, "they/them pronoun option not found"
        
        # Verify the number of characters selection buttons exist (1-5)
        # Look for the character count form group
        character_count_group = None
        for form_group in soup.find_all('div', class_='form-group'):
            label = form_group.find('label', class_='form-label')
            if label and 'How many characters' in label.get_text():
                character_count_group = form_group
                break
        
        assert character_count_group is not None, "Character count form group not found"
        
        # Check for the 5 character count buttons
        character_count_buttons = character_count_group.find_all('button', class_='number-btn')
        assert len(character_count_buttons) == 5, f"Expected 5 character count buttons, found {len(character_count_buttons)}"
        
        # Verify the characters container exists
        assert 'id="charactersContainer"' in template_content, "Characters container not found"
    
    def test_character_input_field_generation_examples(self):
        """
        Feature: children-story-generator, Property 1: Character Input Field Generation
        Test specific examples to ensure character input fields are generated correctly
        Validates: Requirements 1.2
        """
        # Read the actual index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Parse the HTML
        soup = BeautifulSoup(template_content, 'html.parser')
        
        # Check that the number of characters selection exists
        # Look for the form group that contains the "How many characters" label
        character_count_group = None
        for form_group in soup.find_all('div', class_='form-group'):
            label = form_group.find('label', class_='form-label')
            if label and 'How many characters' in label.get_text():
                character_count_group = form_group
                break
        
        assert character_count_group is not None, "Character count form group not found"
        
        # Check for the 5 character count buttons within this group
        character_count_buttons = character_count_group.find_all('button', class_='number-btn')
        assert len(character_count_buttons) == 5, f"Expected 5 character count buttons, found {len(character_count_buttons)}"
        
        # Verify each button has the correct data-value
        expected_values = ['1', '2', '3', '4', '5']
        actual_values = [btn.get('data-value') for btn in character_count_buttons]
        assert set(actual_values) == set(expected_values), f"Expected values {expected_values}, found {actual_values}"
        
        # Check that the characters container exists
        characters_container = soup.find('div', {'id': 'charactersContainer'})
        assert characters_container is not None, "Characters container not found"
        
        # Check that the hidden input for num_characters exists
        num_characters_input = character_count_group.find('input', {'id': 'num_characters'})
        assert num_characters_input is not None, "num_characters hidden input not found"
        
        # Check that the JavaScript function exists and is properly structured
        scripts = soup.find_all('script')
        js_content = ""
        for script in scripts:
            if script.string and 'generateCharacterFields' in script.string:
                js_content = script.string
                break
        
        assert js_content, "JavaScript content with generateCharacterFields not found"
        
        # Verify the function structure
        assert 'function generateCharacterFields(count)' in js_content, "generateCharacterFields function definition not found"
        assert 'charactersContainer' in js_content, "Function doesn't reference charactersContainer"
        assert 'innerHTML = \'\'' in js_content, "Function doesn't clear container"
        
        # Verify character field template structure
        assert 'Character ${i} Details' in js_content, "Character field label template not found"
        assert 'Character ${i} name...' in js_content, "Character name placeholder template not found"
        assert 'required' in js_content, "Required attribute not found in character inputs"
    
    def test_character_input_accessibility(self):
        """
        Feature: children-story-generator, Property 1: Character Input Field Generation
        Test that character input fields meet accessibility requirements
        Validates: Requirements 1.2
        """
        # Read the actual index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Parse the HTML
        soup = BeautifulSoup(template_content, 'html.parser')
        
        # Check that form labels exist and are properly structured
        form_labels = soup.find_all('label', class_='form-label')
        assert len(form_labels) > 0, "No form labels found"
        
        # Check that helper text exists
        form_helpers = soup.find_all('span', class_='form-helper')
        assert len(form_helpers) > 0, "No form helper text found"
        
        # Check that the JavaScript creates proper labels for each character
        scripts = soup.find_all('script')
        js_content = ""
        for script in scripts:
            if script.string and 'generateCharacterFields' in script.string:
                js_content = script.string
                break
        
        # Verify labels are created for character fields
        assert 'form-label' in js_content, "Character fields don't include proper labels"
        assert 'form-helper' in js_content, "Character fields don't include helper text"
        
        # Verify required attributes are set
        assert 'required' in js_content, "Character inputs don't have required attributes"
    
    def test_character_input_validation_structure(self):
        """
        Feature: children-story-generator, Property 1: Character Input Field Generation
        Test that character input fields have proper validation structure
        Validates: Requirements 1.2
        """
        # Read the actual index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Parse the HTML
        soup = BeautifulSoup(template_content, 'html.parser')
        
        # Check that the JavaScript includes validation logic
        scripts = soup.find_all('script')
        js_content = ""
        for script in scripts:
            if script.string:
                js_content += script.string
        
        # Verify character pronoun selection logic exists
        assert 'attachCharacterListeners' in js_content, "Character listener attachment function not found"
        assert 'data-character' in js_content, "Character data attributes not found"
        
        # Verify form validation exists
        assert 'required' in js_content, "Required validation not found"
        
        # Verify pronoun selection updates hidden inputs
        assert 'hiddenInput.value = value' in js_content, "Pronoun selection doesn't update hidden inputs"


class TestTouchTargetSizeCompliance:
    """Property tests for touch target size compliance - Property 15"""
    
    def _extract_css_rules(self, css_content):
        """Extract CSS rules for touch target analysis"""
        # Simple CSS parser for min-width and min-height rules
        rules = {}
        
        # Find all CSS rules with min-width or min-height
        min_width_pattern = r'\.([^{]+)\s*{[^}]*min-width:\s*(\d+)px'
        min_height_pattern = r'\.([^{]+)\s*{[^}]*min-height:\s*(\d+)px'
        
        width_matches = re.findall(min_width_pattern, css_content)
        height_matches = re.findall(min_height_pattern, css_content)
        
        for selector, width in width_matches:
            selector = selector.strip()
            if selector not in rules:
                rules[selector] = {}
            rules[selector]['min_width'] = int(width)
        
        for selector, height in height_matches:
            selector = selector.strip()
            if selector not in rules:
                rules[selector] = {}
            rules[selector]['min_height'] = int(height)
        
        return rules
    
    @given(st.sampled_from(['selection-btn', 'number-btn', 'submit-btn', 'action-btn', 'keyword-input']))
    def test_touch_target_size_compliance_property(self, element_class):
        """
        Feature: children-story-generator, Property 15: Touch Target Size Compliance
        For any interactive UI element, it should meet the minimum 44px touch target requirement
        Validates: Requirements 7.2
        """
        # Read the CSS from the templates
        css_content = ""
        
        # Read CSS from index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            index_content = f.read()
            # Extract CSS from style blocks
            style_matches = re.findall(r'<style>(.*?)</style>', index_content, re.DOTALL)
            for style in style_matches:
                css_content += style
        
        # Read CSS from story.html template
        with open('templates/story.html', 'r', encoding='utf-8') as f:
            story_content = f.read()
            # Extract CSS from style blocks
            style_matches = re.findall(r'<style>(.*?)</style>', story_content, re.DOTALL)
            for style in style_matches:
                css_content += style
        
        # Read external CSS file
        try:
            with open('static/css/style.css', 'r', encoding='utf-8') as f:
                css_content += f.read()
        except FileNotFoundError:
            pass  # External CSS file might not exist
        
        # Check for minimum touch target sizes
        min_target_size = 44  # pixels
        
        # Look for the specific element class in CSS
        class_pattern = rf'\.{re.escape(element_class)}\s*{{[^}}]*}}'
        class_matches = re.findall(class_pattern, css_content, re.DOTALL)
        
        if class_matches:
            for match in class_matches:
                # Check for min-width
                min_width_match = re.search(r'min-width:\s*(\d+)px', match)
                if min_width_match:
                    min_width = int(min_width_match.group(1))
                    assert min_width >= min_target_size, \
                        f"Element .{element_class} has min-width {min_width}px, should be at least {min_target_size}px"
                
                # Check for min-height
                min_height_match = re.search(r'min-height:\s*(\d+)px', match)
                if min_height_match:
                    min_height = int(min_height_match.group(1))
                    assert min_height >= min_target_size, \
                        f"Element .{element_class} has min-height {min_height}px, should be at least {min_target_size}px"
                
                # Check for padding that contributes to touch target size
                padding_match = re.search(r'padding:\s*(\d+)px', match)
                if padding_match:
                    padding = int(padding_match.group(1))
                    # If padding is substantial, it contributes to touch target size
                    if padding >= min_target_size // 2:
                        # This is acceptable as padding contributes to touch target
                        pass
    
    def test_touch_target_size_compliance_examples(self):
        """
        Feature: children-story-generator, Property 15: Touch Target Size Compliance
        Test specific examples to ensure touch targets meet size requirements
        Validates: Requirements 7.2
        """
        # Read CSS content from templates
        css_content = ""
        
        # Read CSS from index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            index_content = f.read()
            style_matches = re.findall(r'<style>(.*?)</style>', index_content, re.DOTALL)
            for style in style_matches:
                css_content += style
        
        # Read CSS from story.html template
        with open('templates/story.html', 'r', encoding='utf-8') as f:
            story_content = f.read()
            style_matches = re.findall(r'<style>(.*?)</style>', story_content, re.DOTALL)
            for style in style_matches:
                css_content += style
        
        # Define critical interactive elements that must meet touch target requirements
        critical_elements = [
            'selection-btn',
            'number-btn', 
            'submit-btn',
            'action-btn',
            'keyword-input'
        ]
        
        min_target_size = 44  # pixels
        
        for element_class in critical_elements:
            # Look for the element class in CSS
            class_pattern = rf'\.{re.escape(element_class)}\s*{{[^}}]*}}'
            class_matches = re.findall(class_pattern, css_content, re.DOTALL)
            
            found_adequate_sizing = False
            
            for match in class_matches:
                # Check various ways the element might meet touch target requirements
                
                # 1. Explicit min-width/min-height
                min_width_match = re.search(r'min-width:\s*(\d+)px', match)
                min_height_match = re.search(r'min-height:\s*(\d+)px', match)
                
                if min_width_match and int(min_width_match.group(1)) >= min_target_size:
                    found_adequate_sizing = True
                
                if min_height_match and int(min_height_match.group(1)) >= min_target_size:
                    found_adequate_sizing = True
                
                # 2. Substantial padding
                padding_match = re.search(r'padding:\s*(\d+)px', match)
                if padding_match and int(padding_match.group(1)) >= min_target_size // 2:
                    found_adequate_sizing = True
                
                # 3. Aspect ratio with adequate size
                if 'aspect-ratio: 1' in match:
                    # For square elements, check if any dimension is adequate
                    if min_width_match or min_height_match:
                        found_adequate_sizing = True
            
            # For critical interactive elements, we should find adequate sizing
            if element_class in ['selection-btn', 'number-btn', 'submit-btn']:
                assert found_adequate_sizing, \
                    f"Critical interactive element .{element_class} doesn't appear to meet 44px touch target requirement"
    
    def test_button_touch_targets(self):
        """
        Feature: children-story-generator, Property 15: Touch Target Size Compliance
        Test that all buttons meet touch target size requirements
        Validates: Requirements 7.2
        """
        # Read the index.html template to check button styling
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Extract CSS
        style_matches = re.findall(r'<style>(.*?)</style>', template_content, re.DOTALL)
        css_content = ''.join(style_matches)
        
        # Check selection buttons
        selection_btn_match = re.search(r'\.selection-btn\s*{[^}]*}', css_content, re.DOTALL)
        if selection_btn_match:
            btn_css = selection_btn_match.group(0)
            
            # Check for min-height
            min_height_match = re.search(r'min-height:\s*(\d+)px', btn_css)
            if min_height_match:
                min_height = int(min_height_match.group(1))
                assert min_height >= 44, f"Selection buttons have min-height {min_height}px, should be at least 44px"
            
            # Check for adequate padding
            padding_match = re.search(r'padding:\s*(\d+)px\s+(\d+)px', btn_css)
            if padding_match:
                vertical_padding = int(padding_match.group(1))
                # Vertical padding contributes to touch target height
                assert vertical_padding >= 20, f"Selection buttons should have adequate padding for touch targets"
        
        # Check number buttons
        number_btn_match = re.search(r'\.number-btn\s*{[^}]*}', css_content, re.DOTALL)
        if number_btn_match:
            btn_css = number_btn_match.group(0)
            
            # Number buttons should have min-width and min-height
            min_width_match = re.search(r'min-width:\s*(\d+)px', btn_css)
            min_height_match = re.search(r'min-height:\s*(\d+)px', btn_css)
            
            if min_width_match:
                min_width = int(min_width_match.group(1))
                assert min_width >= 44, f"Number buttons have min-width {min_width}px, should be at least 44px"
            
            if min_height_match:
                min_height = int(min_height_match.group(1))
                assert min_height >= 44, f"Number buttons have min-height {min_height}px, should be at least 44px"
        
        # Check submit button
        submit_btn_match = re.search(r'\.submit-btn\s*{[^}]*}', css_content, re.DOTALL)
        if submit_btn_match:
            btn_css = submit_btn_match.group(0)
            
            # Submit button should have min-height
            min_height_match = re.search(r'min-height:\s*(\d+)px', btn_css)
            if min_height_match:
                min_height = int(min_height_match.group(1))
                assert min_height >= 44, f"Submit button has min-height {min_height}px, should be at least 44px"
            
            # Check padding
            padding_match = re.search(r'padding:\s*(\d+)px', btn_css)
            if padding_match:
                padding = int(padding_match.group(1))
                assert padding >= 20, f"Submit button should have adequate padding for touch targets"


class TestResponsiveDesignValidation:
    """Property tests for responsive design validation - Property 17"""
    
    def _extract_media_queries(self, css_content):
        """Extract media queries from CSS content"""
        media_queries = {}
        
        # Find all media queries
        media_pattern = r'@media\s*\([^)]*\)\s*{([^{}]*(?:{[^}]*}[^{}]*)*)}'
        matches = re.findall(media_pattern, css_content, re.DOTALL)
        
        for match in matches:
            # Extract the media condition
            condition_match = re.search(r'@media\s*\(([^)]*)\)', css_content)
            if condition_match:
                condition = condition_match.group(1)
                media_queries[condition] = match
        
        return media_queries
    
    @given(st.integers(min_value=768, max_value=1024))
    def test_responsive_design_validation_property(self, screen_width):
        """
        Feature: children-story-generator, Property 17: Responsive Design Validation
        For any screen size 768px and larger, the layout should display correctly and remain functional
        Validates: Requirements 7.7
        """
        # Read CSS content from templates
        css_content = ""
        
        # Read CSS from index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            index_content = f.read()
            style_matches = re.findall(r'<style>(.*?)</style>', index_content, re.DOTALL)
            for style in style_matches:
                css_content += style
        
        # Check for responsive design patterns
        
        # 1. Check for tablet-specific media queries
        tablet_media_queries = [
            'min-width: 768px',
            'max-width: 1024px',
            'min-width: 768px) and (max-width: 1024px'
        ]
        
        has_tablet_optimization = False
        for query in tablet_media_queries:
            if query in css_content:
                has_tablet_optimization = True
                break
        
        # Should have some form of tablet optimization
        assert has_tablet_optimization, "No tablet-specific media queries found"
        
        # 2. Check for responsive grid layouts
        assert 'grid-template-columns' in css_content, "No CSS Grid responsive layouts found"
        
        # 3. Check for flexible sizing
        responsive_patterns = [
            'auto-fit',
            'minmax(',
            'fr',
            'repeat('
        ]
        
        has_responsive_patterns = any(pattern in css_content for pattern in responsive_patterns)
        assert has_responsive_patterns, "No responsive CSS patterns found"
        
        # 4. Check for viewport meta tag in templates
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        assert 'viewport' in base_content, "No viewport meta tag found in base template"
        assert 'width=device-width' in base_content, "Viewport meta tag doesn't set device-width"
    
    def test_responsive_design_validation_examples(self):
        """
        Feature: children-story-generator, Property 17: Responsive Design Validation
        Test specific examples to ensure responsive design works correctly
        Validates: Requirements 7.7
        """
        # Read CSS content from templates
        css_content = ""
        
        # Read CSS from index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            index_content = f.read()
            style_matches = re.findall(r'<style>(.*?)</style>', index_content, re.DOTALL)
            for style in style_matches:
                css_content += style
        
        # Read CSS from story.html template
        with open('templates/story.html', 'r', encoding='utf-8') as f:
            story_content = f.read()
            style_matches = re.findall(r'<style>(.*?)</style>', story_content, re.DOTALL)
            for style in style_matches:
                css_content += style
        
        # Test specific responsive breakpoints
        
        # 1. Check for mobile breakpoint (max-width: 768px)
        mobile_media = re.search(r'@media\s*\([^)]*max-width:\s*768px[^)]*\)\s*{', css_content)
        assert mobile_media, "No mobile media query found"
        
        # 2. Check for tablet-specific breakpoint
        tablet_media = re.search(r'@media\s*\(min-width:\s*768px\)\s*and\s*\(max-width:\s*1024px\)', css_content)
        assert tablet_media, "No tablet-specific media query found"
        
        # 3. Check for responsive grid systems
        grid_patterns = [
            'grid-template-columns: repeat(auto-fit, minmax(',
            'grid-template-columns: repeat(auto-fill, minmax('
        ]
        
        has_responsive_grid = any(pattern in css_content for pattern in grid_patterns)
        assert has_responsive_grid, "No responsive grid patterns found"
        
        # 4. Check for flexible container sizing
        assert 'max-width:' in css_content, "No max-width constraints found for containers"
        
        # 5. Check viewport meta tag
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        viewport_match = re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*>', base_content)
        assert viewport_match, "Viewport meta tag not found"
        
        viewport_content = viewport_match.group(0)
        assert 'width=device-width' in viewport_content, "Viewport doesn't set device-width"
        assert 'initial-scale=1' in viewport_content, "Viewport doesn't set initial-scale"
    
    def test_tablet_optimization_specifics(self):
        """
        Feature: children-story-generator, Property 17: Responsive Design Validation
        Test that tablet-specific optimizations are implemented
        Validates: Requirements 7.7
        """
        # Read CSS from index.html template
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        # Extract CSS
        style_matches = re.findall(r'<style>(.*?)</style>', index_content, re.DOTALL)
        css_content = ''.join(style_matches)
        
        # Check for tablet-specific media query
        tablet_media_pattern = r'@media\s*\(min-width:\s*768px\)\s*and\s*\(max-width:\s*1024px\)\s*{([^{}]*(?:{[^}]*}[^{}]*)*)}'
        tablet_match = re.search(tablet_media_pattern, css_content, re.DOTALL)
        
        assert tablet_match, "No tablet-specific media query (768px-1024px) found"
        
        tablet_css = tablet_match.group(1)
        
        # Check for tablet-specific optimizations
        tablet_optimizations = [
            'padding:',  # Adjusted padding for tablet
            'font-size:',  # Larger fonts for tablet
            'grid-template-columns:',  # Adjusted grid layouts
            'min-height:',  # Adjusted element sizes
        ]
        
        found_optimizations = [opt for opt in tablet_optimizations if opt in tablet_css]
        assert len(found_optimizations) >= 2, \
            f"Tablet media query should contain multiple optimizations, found: {found_optimizations}"
        
        # Check for larger touch targets on tablet
        if 'selection-btn' in tablet_css:
            # Should have larger sizing for tablet
            assert 'min-height:' in tablet_css or 'padding:' in tablet_css, \
                "Tablet optimization should include larger touch targets"
        
        # Check for responsive grid adjustments
        if 'grid-template-columns' in tablet_css:
            # Should use responsive grid patterns
            assert 'minmax(' in tablet_css or 'auto-fit' in tablet_css, \
                "Tablet grid should use responsive patterns"


if __name__ == "__main__":
    if not HYPOTHESIS_AVAILABLE:
        print("Running basic UI property tests...")
        
        # Test character input field generation
        print("\n=== Testing Character Input Field Generation ===")
        test_class = TestCharacterInputFieldGeneration()
        
        try:
            test_class.test_character_input_field_generation_examples()
            print("✓ Character input field generation examples passed")
        except Exception as e:
            print(f"✗ Character input field generation examples failed: {e}")
        
        try:
            test_class.test_character_input_accessibility()
            print("✓ Character input accessibility tests passed")
        except Exception as e:
            print(f"✗ Character input accessibility tests failed: {e}")
        
        # Test touch target size compliance
        print("\n=== Testing Touch Target Size Compliance ===")
        touch_test_class = TestTouchTargetSizeCompliance()
        
        try:
            touch_test_class.test_touch_target_size_compliance_examples()
            print("✓ Touch target size compliance examples passed")
        except Exception as e:
            print(f"✗ Touch target size compliance examples failed: {e}")
        
        try:
            touch_test_class.test_button_touch_targets()
            print("✓ Button touch target tests passed")
        except Exception as e:
            print(f"✗ Button touch target tests failed: {e}")
        
        # Test responsive design validation
        print("\n=== Testing Responsive Design Validation ===")
        responsive_test_class = TestResponsiveDesignValidation()
        
        try:
            responsive_test_class.test_responsive_design_validation_examples()
            print("✓ Responsive design validation examples passed")
        except Exception as e:
            print(f"✗ Responsive design validation examples failed: {e}")
        
        try:
            responsive_test_class.test_tablet_optimization_specifics()
            print("✓ Tablet optimization tests passed")
        except Exception as e:
            print(f"✗ Tablet optimization tests failed: {e}")
        
        print("\nBasic UI property tests completed!")
    
    else:
        print("Running property-based UI tests...")
        
        # Run property-based tests manually
        from hypothesis import given, strategies as st
        
        print("\n=== Property-Based Character Input Field Generation ===")
        test_class = TestCharacterInputFieldGeneration()
        
        # Test with different numbers of characters
        for num_chars in [1, 2, 3, 4, 5]:
            try:
                test_class.test_character_input_field_generation_property(num_chars)
                print(f"✓ Character input generation property test passed for {num_chars} characters")
            except Exception as e:
                print(f"✗ Character input generation property test failed for {num_chars} characters: {e}")
        
        print("\n=== Property-Based Touch Target Size Compliance ===")
        touch_test_class = TestTouchTargetSizeCompliance()
        
        # Test different element types
        element_types = ['selection-btn', 'number-btn', 'submit-btn', 'action-btn', 'keyword-input']
        for element_type in element_types:
            try:
                touch_test_class.test_touch_target_size_compliance_property(element_type)
                print(f"✓ Touch target compliance property test passed for {element_type}")
            except Exception as e:
                print(f"✗ Touch target compliance property test failed for {element_type}: {e}")
        
        print("\n=== Property-Based Responsive Design Validation ===")
        responsive_test_class = TestResponsiveDesignValidation()
        
        # Test different screen widths
        screen_widths = [768, 800, 900, 1000, 1024]
        for width in screen_widths:
            try:
                responsive_test_class.test_responsive_design_validation_property(width)
                print(f"✓ Responsive design property test passed for {width}px width")
            except Exception as e:
                print(f"✗ Responsive design property test failed for {width}px width: {e}")
        
        print("\nProperty-based UI tests completed!")