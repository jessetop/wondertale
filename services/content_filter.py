"""
Content Filter Service
Ensures all generated content is age-appropriate for children 3-8
"""

import re
from typing import List, Set

class ContentFilter:
    """Service for validating content safety and age-appropriateness"""
    
    def __init__(self):
        """Initialize content filter with safety rules"""
        # Inappropriate keywords that should be filtered out
        self.inappropriate_keywords = {
            # Violence and scary content
            "scary", "violent", "death", "die", "kill", "hurt", "blood", "pain",
            "weapon", "gun", "knife", "sword", "fight", "battle", "war", "attack",
            "angry", "hate", "evil", "monster", "ghost", "zombie", "demon",
            "nightmare", "terror", "fear", "afraid", "scream", "cry", "sad",
            
            # Adult themes
            "alcohol", "beer", "wine", "drunk", "smoke", "cigarette", "drug",
            "money", "rich", "poor", "work", "job", "boss", "fire", "fired",
            
            # Inappropriate language
            "stupid", "dumb", "idiot", "fool", "loser", "ugly", "fat", "skinny",
            "shut up", "go away", "i hate", "you suck", "bad", "worst",
            
            # Potentially scary animals/creatures
            "shark", "snake", "spider", "wolf", "bear", "lion", "tiger",
            "crocodile", "alligator", "scorpion", "bat", "rat", "mouse"
        }
        
        # Age-appropriate vocabulary for 3-8 year olds
        self.age_appropriate_words = {
            # Basic emotions (positive)
            "happy", "joy", "smile", "laugh", "giggle", "excited", "proud",
            "love", "like", "enjoy", "fun", "wonderful", "amazing", "great",
            
            # Family and friends
            "family", "mom", "dad", "sister", "brother", "friend", "buddy",
            "grandma", "grandpa", "aunt", "uncle", "cousin", "neighbor",
            
            # Animals (friendly)
            "dog", "cat", "rabbit", "bird", "fish", "horse", "cow", "pig",
            "sheep", "duck", "chicken", "butterfly", "bee", "ladybug",
            
            # Nature (safe)
            "tree", "flower", "grass", "sun", "moon", "star", "cloud", "rain",
            "rainbow", "garden", "park", "beach", "mountain", "river", "lake",
            
            # Activities
            "play", "run", "jump", "dance", "sing", "read", "draw", "paint",
            "build", "create", "explore", "discover", "learn", "help", "share",
            
            # Objects
            "toy", "book", "ball", "bike", "car", "train", "plane", "boat",
            "house", "home", "school", "playground", "swing", "slide",
            
            # Food (healthy)
            "apple", "banana", "orange", "berry", "carrot", "bread", "milk",
            "water", "sandwich", "soup", "cookie", "cake", "ice cream"
        }
        
        # Simple sentence patterns that are age-appropriate
        self.complex_sentence_patterns = [
            r'\b\w{12,}\b',  # Words longer than 11 characters (increased from 9)
            r'[;:]',  # Semicolons and colons (too complex)
            r'\b(however|therefore|nevertheless|furthermore|moreover|consequently)\b',  # Complex conjunctions
            r'\b(although|whereas|despite|unless|provided|assuming)\b',  # Complex conditional words
        ]
    
    def validate_keywords(self, keywords: List[str]) -> bool:
        """
        Ensure keywords are child-appropriate
        Requirements: 2.3 - validate keywords are child-appropriate before inclusion
        """
        if not keywords:
            return True
            
        for keyword in keywords:
            keyword_clean = keyword.lower().strip()
            if not keyword_clean:
                continue
                
            # Check against inappropriate keywords
            if keyword_clean in self.inappropriate_keywords:
                return False
                
            # Check for inappropriate word combinations
            for inappropriate in self.inappropriate_keywords:
                if inappropriate in keyword_clean:
                    return False
        
        return True
    
    def validate_story_content(self, content: str) -> bool:
        """
        Verify story meets safety standards
        Requirements: 2.1, 2.2, 2.4, 2.5 - age-appropriate vocabulary, no scary/violent themes, 
        simple sentences, positive themes
        """
        if not content or not content.strip():
            return False
            
        content_lower = content.lower()
        
        # Check for inappropriate keywords
        for inappropriate in self.inappropriate_keywords:
            if inappropriate in content_lower:
                return False
        
        # Check for overly complex sentence structures (Requirement 2.4)
        for pattern in self.complex_sentence_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        # Check for positive themes (Requirement 2.5)
        # Story should contain some positive words
        positive_words = {"happy", "joy", "smile", "laugh", "love", "friend", "help", 
                         "kind", "nice", "good", "wonderful", "amazing", "great", "fun"}
        
        has_positive_content = any(word in content_lower for word in positive_words)
        if not has_positive_content:
            return False
        
        return True
    
    def validate_age_appropriate_vocabulary(self, content: str) -> bool:
        """
        Check if vocabulary is appropriate for ages 3-8
        Requirements: 2.1 - ensure all vocabulary is appropriate for ages 3-8
        """
        if not content:
            return True
            
        # Split content into words and check each
        words = re.findall(r'\b\w+\b', content.lower())
        
        for word in words:
            # Skip very short words (articles, prepositions, etc.)
            if len(word) <= 2:
                continue
                
            # Check if word is inappropriate
            if word in self.inappropriate_keywords:
                return False
                
            # Check if word is too complex (more than 8 characters for this age group)
            if len(word) > 8:
                # Allow some common longer words that kids know
                allowed_long_words = {"beautiful", "wonderful", "adventure", "together", 
                                    "playground", "butterfly", "grandmother", "grandfather",
                                    "astronauts", "astronaut", "discoveries", "discovery",
                                    "friendship", "community", "neighborhood", "celebrate"}
                if word not in allowed_long_words:
                    return False
        
        return True
    
    def validate_theme_safety(self, topic: str, keywords: List[str]) -> bool:
        """
        Validate that topic and keywords create safe themes
        Requirements: 2.2 - avoid scary, violent, or inappropriate themes
        """
        # First validate keywords individually
        if not self.validate_keywords(keywords):
            return False
        
        # Check topic-specific safety
        safe_topics = {"space", "community", "dragons", "fairies"}
        if topic not in safe_topics:
            return False
        
        # Check for dangerous combinations
        self.dangerous_combinations = {
            "space": ["crash", "explosion", "lost", "danger"],
            "dragons": ["fire", "burn", "destroy", "attack", "fierce"],
            "fairies": ["curse", "spell", "disappear", "trap"],
            "community": ["stranger", "lost", "alone", "emergency"]  # Removed "help" as it's positive
        }
        
        if topic in self.dangerous_combinations:
            topic_dangers = self.dangerous_combinations[topic]
            for keyword in keywords:
                if keyword.lower().strip() in topic_dangers:
                    return False
        
        return True
    
    def filter_inappropriate_keywords(self, keywords: List[str]) -> List[str]:
        """
        Filter out inappropriate keywords from a list
        Requirements: 2.3 - validate keywords are child-appropriate before inclusion
        """
        filtered_keywords = []
        
        for keyword in keywords:
            keyword_clean = keyword.strip()
            if keyword_clean and self.validate_keywords([keyword_clean]):
                filtered_keywords.append(keyword_clean)
        
        return filtered_keywords
    
    def get_content_safety_score(self, content: str) -> float:
        """
        Get a safety score for content (0.0 = unsafe, 1.0 = completely safe)
        This can be used for gradual filtering or warnings
        """
        if not content:
            return 0.0
        
        score = 1.0
        content_lower = content.lower()
        
        # Deduct points for inappropriate content
        inappropriate_count = sum(1 for word in self.inappropriate_keywords if word in content_lower)
        score -= (inappropriate_count * 0.3)  # Increased penalty from 0.2 to 0.3
        
        # Deduct points for complex sentences
        complex_pattern_count = sum(1 for pattern in self.complex_sentence_patterns 
                                  if re.search(pattern, content, re.IGNORECASE))
        score -= (complex_pattern_count * 0.3)  # Increased penalty from 0.1 to 0.3
        
        # Add points for positive content
        positive_words = {"happy", "joy", "smile", "laugh", "love", "friend", "help", 
                         "kind", "nice", "good", "wonderful", "amazing", "great", "fun"}
        positive_count = sum(1 for word in positive_words if word in content_lower)
        score += min(positive_count * 0.05, 0.2)  # Cap bonus at 0.2
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1