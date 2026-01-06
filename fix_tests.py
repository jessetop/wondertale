#!/usr/bin/env python3
"""
Script to fix StoryRequest constructor calls in test files by adding missing age_group and story_length parameters.
"""

import re
import os

def fix_story_request_calls(file_path):
    """Fix StoryRequest calls in a file by adding missing parameters."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match StoryRequest calls that are missing age_group and story_length
    pattern = r'(StoryRequest\(\s*\n?\s*characters=[^,]+,\s*\n?\s*topic=[^,]+,\s*\n?\s*keywords=[^,]+,\s*\n?\s*)(include_image=[^)]+\))'
    
    # Replacement that adds age_group and story_length before include_image
    replacement = r'\1age_group="5-6",\n            story_length="medium",\n            \2'
    
    # Apply the replacement
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Handle cases where include_image is not present
    pattern2 = r'(StoryRequest\(\s*\n?\s*characters=[^,]+,\s*\n?\s*topic=[^,]+,\s*\n?\s*keywords=[^,]+)\s*\n?\s*\)'
    replacement2 = r'\1,\n            age_group="5-6",\n            story_length="medium",\n            include_image=False\n        )'
    
    new_content = re.sub(pattern2, replacement2, new_content, flags=re.MULTILINE)
    
    # Write back if changed
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {file_path}")
        return True
    else:
        print(f"No changes needed in {file_path}")
        return False

def main():
    """Fix all test files."""
    test_files = ['test_models.py', 'test_story_generator.py', 'test_story_generator_updated.py']
    
    for file_path in test_files:
        if os.path.exists(file_path):
            fix_story_request_calls(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()