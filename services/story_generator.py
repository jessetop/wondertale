"""
Story Generation Service
Handles AI-powered story creation with OpenAI GPT
"""

import os
import re
import uuid
from typing import List, Optional
from datetime import datetime

# Import models from the main models module
from models import Character, StoryRequest, GeneratedStory

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Story generation will use placeholder content.")


class StoryGenerator:
    """Service for generating children's stories using OpenAI GPT-4"""
    
    def __init__(self):
        """Initialize the story generator with OpenAI client"""
        self.client = None
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        if not OPENAI_AVAILABLE:
            print("OpenAI not available - using placeholder mode")
            return
            
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            print("Warning: OPENAI_API_KEY not found in environment variables")
    
    def _create_story_prompt(self, request: StoryRequest) -> str:
        """Create a detailed prompt for story generation"""
        # Build character descriptions with proper pronouns
        character_descriptions = []
        for char in request.characters:
            pronoun_info = self._get_pronoun_info(char.pronouns)
            character_descriptions.append(f"{char.name} (use {char.pronouns} pronouns - {pronoun_info})")
        
        characters_text = ", ".join(character_descriptions)
        keywords_text = ", ".join(request.keywords)
        
        # Get target word count range
        min_words, max_words = request.get_target_word_count_range()
        
        # Get vocabulary level for age group
        vocabulary_level = self._get_vocabulary_level(request.age_group)
        
        # Topic-specific context
        topic_contexts = {
            "space": "space exploration, planets, astronauts, rockets, stars, or cosmic adventures",
            "community": "helping others, friendship, neighborhood activities, teamwork, or community service",
            "dragons": "friendly dragons, magical adventures, fantasy worlds, or mythical creatures",
            "fairies": "fairies, magic, enchanted settings, fairy gardens, or magical forests"
        }
        
        topic_context = topic_contexts.get(request.topic, request.topic)
        
        prompt = f"""Write a children's story for ages {request.age_group} with the following requirements:

CHARACTERS: {characters_text}
- Make ALL characters protagonists or key characters in the story
- Use the correct pronouns consistently throughout the story
- Include all character names prominently in the story

TOPIC: {request.topic} - incorporate themes related to {topic_context}

KEYWORDS: Naturally weave these keywords into the story: {keywords_text}

STORY REQUIREMENTS:
- Length: {min_words}-{max_words} words (this is {request.story_length} length for ages {request.age_group})
- Include exactly ONE clear moral or positive lesson
- Use {vocabulary_level} vocabulary appropriate for ages {request.age_group}
- Follow a clear beginning, middle, and end structure
- Maintain positive, uplifting themes throughout
- Avoid scary, violent, or inappropriate content
- Make the moral lesson naturally integrated into the narrative

VOCABULARY LEVEL: {vocabulary_level}
{self._get_vocabulary_guidelines(request.age_group)}

Please format the response as:
TITLE: [Story Title]
STORY: [The complete story]
MORAL: [The moral lesson in one clear sentence]"""

        return prompt
    
    def _get_vocabulary_level(self, age_group: str) -> str:
        """Get vocabulary complexity level for age group"""
        vocabulary_levels = {
            "3-4": "simple",
            "5-6": "elementary", 
            "7-8": "intermediate",
            "9-10": "advanced"
        }
        return vocabulary_levels.get(age_group, "elementary")
    
    def _get_vocabulary_guidelines(self, age_group: str) -> str:
        """Get specific vocabulary guidelines for age group"""
        guidelines = {
            "3-4": "- Use 1-3 syllable words\n- Use basic sentence structures (subject-verb-object)\n- Avoid complex grammar",
            "5-6": "- Use mostly 1-4 syllable words\n- Use compound sentences occasionally\n- Include some descriptive words",
            "7-8": "- Use varied vocabulary including some 5+ syllable words\n- Use varied sentence structures\n- Include more descriptive and emotional language",
            "9-10": "- Use advanced vocabulary while keeping themes age-appropriate\n- Use complex sentence structures\n- Include sophisticated concepts explained simply"
        }
        return guidelines.get(age_group, guidelines["5-6"])
    
    def _get_pronoun_info(self, pronouns: str) -> str:
        """Get grammatical information for pronouns"""
        pronoun_map = {
            "he/him": "he, him, his",
            "she/her": "she, her, hers", 
            "they/them": "they, them, their"
        }
        return pronoun_map.get(pronouns, pronouns)
    
    def _parse_story_response(self, response_text: str) -> tuple[str, str, str]:
        """Parse the OpenAI response to extract title, story, and moral"""
        lines = response_text.strip().split('\n')
        
        title = ""
        story = ""
        moral = ""
        
        current_section = None
        story_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                current_section = "title"
            elif line.startswith("STORY:"):
                story_content = line.replace("STORY:", "").strip()
                if story_content:
                    story_lines.append(story_content)
                current_section = "story"
            elif line.startswith("MORAL:"):
                moral = line.replace("MORAL:", "").strip()
                current_section = "moral"
            elif current_section == "story" and line:
                story_lines.append(line)
        
        story = " ".join(story_lines).strip()
        
        # Fallback parsing if structured format wasn't used
        if not title or not story:
            # Try to extract from unstructured response
            full_text = response_text.strip()
            
            # Look for a title (usually the first line or in quotes)
            first_line = full_text.split('\n')[0].strip()
            if len(first_line) < 100 and not first_line.lower().startswith(('once', 'in', 'there')):
                title = first_line
                story = '\n'.join(full_text.split('\n')[1:]).strip()
            else:
                title = "Your Amazing Adventure"
                story = full_text
            
            # Extract moral from the end if present
            if not moral:
                sentences = story.split('.')
                for sentence in reversed(sentences):
                    sentence = sentence.strip()
                    if any(word in sentence.lower() for word in ['moral', 'lesson', 'learned', 'remember', 'important']):
                        moral = sentence + '.'
                        break
                
                if not moral:
                    moral = "Always be kind and help others."
        
        return title.strip(), story.strip(), moral.strip()
    
    def _validate_story_content(self, story: str, request: StoryRequest) -> bool:
        """Validate that the generated story meets requirements"""
        if not story:
            return False
        
        # Check word count against target range
        word_count = len(story.split())
        min_words, max_words = request.get_target_word_count_range()
        
        # Allow some flexibility (±20% of range)
        flexibility = int((max_words - min_words) * 0.2)
        flexible_min = max(min_words - flexibility, min_words // 2)
        flexible_max = max_words + flexibility
        
        if word_count < flexible_min or word_count > flexible_max:
            return False
        
        # Check that all character names appear in the story
        story_lower = story.lower()
        for character in request.characters:
            if character.name.lower() not in story_lower:
                return False
        
        return True
    
    def generate_story(self, request: StoryRequest) -> GeneratedStory:
        """Generate a story based on the request"""
        # Validate request using the model's validation
        errors = request.validate()
        if errors:
            raise ValueError(f"Invalid request: {', '.join(errors)}")
        
        # If OpenAI is not available, return a placeholder
        if not self.client:
            return self._generate_placeholder_story(request)
        
        try:
            # Create the prompt
            prompt = self._create_story_prompt(request)
            
            # Generate story using OpenAI GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a children's story writer who creates age-appropriate, educational, and entertaining stories for children ages 3-8. Always follow the formatting instructions exactly."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            # Extract the story content
            story_text = response.choices[0].message.content
            title, content, moral = self._parse_story_response(story_text)
            
            # Validate the generated content
            if not self._validate_story_content(content, request):
                # If validation fails, try once more with a more specific prompt
                retry_prompt = prompt + "\n\nIMPORTANT: Ensure the story is between 200-400 words and includes all character names prominently."
                
                retry_response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a children's story writer. Follow the word count and character inclusion requirements strictly."
                        },
                        {"role": "user", "content": retry_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.6
                )
                
                retry_text = retry_response.choices[0].message.content
                title, content, moral = self._parse_story_response(retry_text)
            
            # Create and return the generated story
            target_range = request.get_target_word_count_range()
            return GeneratedStory.create(
                title=title or "Your Amazing Adventure",
                content=content,
                moral=moral or "Always be kind and help others.",
                characters=request.characters,
                topic=request.topic,
                age_group=request.age_group,
                story_length=request.story_length,
                target_word_range=target_range,
                image_url=None  # Will be set by image generation service
            )
            
        except Exception as e:
            print(f"Error generating story with OpenAI: {e}")
            # Return placeholder story on error
            return self._generate_placeholder_story(request)
    
    def _generate_placeholder_story(self, request: StoryRequest) -> GeneratedStory:
        """Generate a placeholder story when OpenAI is not available"""
        character_names = [char.name for char in request.characters]
        names_text = ", ".join(character_names[:-1]) + f" and {character_names[-1]}" if len(character_names) > 1 else character_names[0]
        
        # Get target word count for this age/length combination
        min_words, max_words = request.get_target_word_count_range()
        target_words = (min_words + max_words) // 2  # Aim for middle of range
        
        topic_stories = {
            "space": f"Once upon a time, {names_text} became brave astronauts who traveled to a magical planet made of rainbow crystals. They discovered that the planet's friendly alien inhabitants needed help fixing their broken star-maker machine. Working together with kindness and creativity, they repaired the machine and filled the sky with beautiful twinkling stars. The aliens were so grateful that they gave {names_text} special star badges to remember their adventure. When they returned to Earth, they realized that helping others always makes the universe a brighter place.",
            
            "community": f"In a cozy neighborhood, {names_text} noticed that their elderly neighbor Mrs. Rose looked sad because her garden was overgrown and she couldn't tend to it anymore. They decided to surprise her by organizing all the neighborhood children to help clean up the garden. Everyone brought tools, planted new flowers, and painted a beautiful welcome sign. When Mrs. Rose saw her garden blooming again, she cried happy tears and invited everyone for lemonade and cookies. {names_text} learned that when communities work together, they can create something wonderful.",
            
            "dragons": f"Deep in an enchanted forest, {names_text} met a gentle dragon named Sparkle who had lost the ability to breathe fire. The dragon was very sad because fire-breathing helped him light the magical lanterns that guided forest creatures home at night. {names_text} embarked on a quest to find the legendary Flame Flower that could restore Sparkle's fire. After solving riddles and helping other magical creatures along the way, they found the flower glowing in a hidden cave. When Sparkle ate the flower, his fire returned, and the forest was filled with warm, welcoming light once again.",
            
            "fairies": f"In a secret fairy garden behind the old oak tree, {names_text} discovered that all the flowers were wilting because the garden's magic fountain had stopped working. The fairy queen explained that the fountain needed the laughter of kind children to flow again. {names_text} spent the day playing games, telling jokes, and sharing happy stories with all the garden fairies. As their joyful laughter filled the air, the fountain began to sparkle and flow with crystal-clear water. The flowers bloomed more beautifully than ever, and the fairies granted {names_text} the gift of always finding magic in everyday kindness."
        }
        
        base_content = topic_stories.get(request.topic, f"{names_text} had an amazing adventure and learned that kindness and friendship are the most important things in the world.")
        
        # Adjust content length based on target word count
        words = base_content.split()
        if len(words) > target_words:
            # Truncate if too long
            content = " ".join(words[:target_words])
        elif len(words) < min_words:
            # Extend if too short
            extension = f" They smiled and laughed together, sharing their joy with everyone around them. The adventure taught them valuable lessons about friendship, kindness, and helping others."
            content = base_content + extension
            # Truncate if still too long
            words = content.split()
            if len(words) > max_words:
                content = " ".join(words[:max_words])
        else:
            content = base_content
        
        target_range = request.get_target_word_count_range()
        return GeneratedStory.create(
            title=f"{names_text}'s Amazing {request.topic.title()} Adventure",
            content=content,
            moral="Helping others and working together makes the world a better place.",
            characters=request.characters,
            topic=request.topic,
            age_group=request.age_group,
            story_length=request.story_length,
            target_word_range=target_range,
            image_url=None
        )