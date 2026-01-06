"""
Content Filter Service
Ensures all generated content is age-appropriate for children 3-8
"""

from typing import List

class ContentFilter:
    """Service for validating content safety and age-appropriateness"""
    
    def __init__(self):
        """Initialize content filter with safety rules"""
        self.inappropriate_keywords = [
            # This list will be expanded in later tasks
            "scary", "violent", "death", "kill", "hurt", "blood",
            "weapon", "gun", "knife", "fight", "angry", "hate"
        ]
        
        self.age_appropriate_vocabulary = True  # Will be implemented in later tasks
    
    def validate_keywords(self, keywords: List[str]) -> bool:
        """Ensure keywords are child-appropriate"""
        for keyword in keywords:
            if keyword.lower().strip() in self.inappropriate_keywords:
                return False
        return True
    
    def validate_story_content(self, content: str) -> bool:
        """Verify story meets safety standards"""
        # Basic validation - will be expanded in later tasks
        content_lower = content.lower()
        
        for inappropriate in self.inappropriate_keywords:
            if inappropriate in content_lower:
                return False
        
        return True
    
    def filter_content(self, content: str) -> str:
        """Filter and clean content to ensure appropriateness"""
        # This will be implemented in later tasks
        return content
    
    def validate_theme_safety(self, topic: str, keywords: List[str]) -> bool:
        """Validate that topic and keywords create safe themes"""
        # Ensure no scary/violent combinations
        if not self.validate_keywords(keywords):
            return False
        
        # Topic-specific safety checks will be added in later tasks
        return True