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
            # Configure client with timeout to prevent Railway worker timeouts
            self.client = OpenAI(
                api_key=api_key,
                timeout=25.0  # 25 seconds timeout (Railway default worker timeout is 30s)
            )
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
        
        # Parse adventure items from keywords
        magic_tool = request.keywords[0] if len(request.keywords) > 0 else "wand"
        adventure_pack = request.keywords[1] if len(request.keywords) > 1 else "backpack"  
        animal_friend = request.keywords[2] if len(request.keywords) > 2 else "wolf"
        
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

ADVENTURE ITEMS: Include these items naturally in the story:
- Magic Tool: {magic_tool} (a magical item that helps solve problems)
- Adventure Pack: {adventure_pack} (something the character carries or wears)
- Animal Friend: {animal_friend} (a loyal companion who helps on the journey)

STORY REQUIREMENTS:
- Length: {min_words}-{max_words} words (this is {request.story_length} length for ages {request.age_group})
- Include exactly ONE clear moral or positive lesson
- Use {vocabulary_level} vocabulary appropriate for ages {request.age_group}
- Follow a clear beginning, middle, and end structure
- For ages 3-4: Use VERY SHORT paragraphs (1-2 sentences each) with lots of line breaks
- For ages 5-6: Use SHORT paragraphs (2-3 sentences each) with clear line breaks
- For ages 7+: Use paragraphs (2-4 sentences each) with line breaks between paragraphs
- Add line breaks between paragraphs to make it easier for children to read
- Maintain positive, uplifting themes throughout
- Avoid scary, violent, or inappropriate content
- Make the moral lesson naturally integrated into the narrative
- Show how the adventure items and animal friend help the characters succeed

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
            "3-4": "- Use only simple 1-2 syllable words (cat, dog, run, big, happy, sad, go, see, get, put, help, good, bad, nice, fun)\n- Avoid complex words like 'organized', 'elderly', 'neighborhood', 'discovered', 'realized'\n- Use basic sentence structure: Subject + Verb + Object (Oliver saw Mrs. Rose)\n- Use simple connecting words: and, but, so, then",
            "5-6": "- Use mostly 1-3 syllable words with some 4-syllable words\n- Use compound sentences occasionally\n- Include some descriptive words but keep them simple\n- Avoid abstract concepts",
            "7-8": "- Use varied vocabulary including some 5+ syllable words\n- Use varied sentence structures\n- Include more descriptive and emotional language\n- Can introduce some abstract concepts",
            "9-10": "- Use advanced vocabulary while keeping themes age-appropriate\n- Use complex sentence structures\n- Include sophisticated concepts explained simply\n- Can use more nuanced emotional language"
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
        
        # Parse adventure items from keywords (do this first, outside try block)
        magic_tool = request.keywords[0] if len(request.keywords) > 0 else "wand"
        adventure_pack = request.keywords[1] if len(request.keywords) > 1 else "backpack"  
        animal_friend = request.keywords[2] if len(request.keywords) > 2 else "wolf"
        
        # If OpenAI is not available, return a placeholder
        if not self.client:
            return self._generate_placeholder_story(request)
        
        try:
            # Create the prompt
            prompt = self._create_story_prompt(request)
            
            # Generate story using OpenAI GPT-4 with retry logic
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    print(f"DEBUG: OpenAI API call attempt {attempt + 1}/{max_retries + 1}")
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
                    break  # Success, exit retry loop
                    
                except Exception as api_error:
                    print(f"DEBUG: OpenAI API attempt {attempt + 1} failed: {api_error}")
                    if attempt == max_retries:
                        # Last attempt failed, re-raise the error
                        raise api_error
                    # Wait briefly before retry
                    import time
                    time.sleep(1)
            
            # Extract the story content
            story_text = response.choices[0].message.content
            title, content, moral = self._parse_story_response(story_text)
            
            # Validate the generated content
            if not self._validate_story_content(content, request):
                # If validation fails, try once more with a more specific prompt
                retry_prompt = prompt + "\n\nIMPORTANT: Ensure the story is between 200-400 words and includes all character names prominently."
                
                print("DEBUG: Story validation failed, retrying with specific prompt")
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
                image_url=None,  # Will be set by image generation service
                magic_tool=magic_tool,
                adventure_pack=adventure_pack,
                animal_friend=animal_friend
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
        
        # Parse adventure items from keywords
        magic_tool = request.keywords[0] if len(request.keywords) > 0 else "wand"
        adventure_pack = request.keywords[1] if len(request.keywords) > 1 else "backpack"  
        animal_friend = request.keywords[2] if len(request.keywords) > 2 else "wolf"
        
        topic_stories = {
            "space": f"Once upon a time, {names_text} went to space. They flew to a magic planet with pretty colors.\n\nThey took their {magic_tool} with them. They wore their {adventure_pack} too.\n\nTheir friend was a nice {animal_friend}. The {animal_friend} helped them fly through the stars.\n\nThey met some space friends. The space friends needed help with their star machine.\n\nUsing their {magic_tool}, they helped fix it. Their {animal_friend} friend had good ideas.\n\nThey made the machine work again. Now the sky had lots of pretty stars!\n\nThe space friends were so happy. They gave {names_text} special star stickers.\n\nWhen they came home, they felt good. They learned that helping others makes everyone happy.",
            
            "community": f"Oliver lived in a nice town. Oliver saw Mrs. Rose in her yard.\n\nMrs. Rose was sad. Her garden had too many weeds.\n\nShe could not fix it by herself. She needed help.\n\nOliver got his magic {magic_tool}. He put on his special {adventure_pack}.\n\nHe called his {animal_friend} friend to come help. They had a good idea.\n\nThey asked all the kids in town to help. Everyone wanted to help Mrs. Rose!\n\nThe {magic_tool} helped cut the weeds. The {adventure_pack} held all the seeds.\n\nThe {animal_friend} showed them where to plant flowers. It was like a fun game!\n\nWhen Mrs. Rose saw her pretty garden, she was so happy. She gave everyone cookies and juice.\n\nOliver learned something good. When friends work together, they can do anything.",
            
            "dragons": f"In a big forest, {names_text} met a dragon named Sparkle. Sparkle looked very sad.\n\nSparkle could not make fire anymore. This made him feel bad.\n\nHe used his fire to light up lamps. The lamps helped animals find their way home.\n\nThey had their strong {magic_tool}. They wore their safe {adventure_pack}.\n\nTheir {animal_friend} friend came too. {names_text} wanted to help Sparkle.\n\nThey went to look for a magic flower. The flower could give Sparkle his fire back!\n\nTheir {animal_friend} friend found the right path. Their {magic_tool} helped them solve puzzles.\n\nTheir {adventure_pack} kept them safe from thorns. They helped other animals on the way.\n\nThey found the flower in a cave. It was so pretty and bright!\n\nWhen Sparkle ate the flower, his fire came back. The forest had warm light again.\n\nAll the animals cheered. The lamps lit up all the paths. Sparkle was so happy!",
            
            "fairies": f"Behind a big tree, {names_text} found a fairy garden. But all the flowers looked sick!\n\nThe magic water had stopped working. The fairy queen was very sad.\n\nThey brought their magic {magic_tool}. They had their special {adventure_pack} too.\n\nTheir {animal_friend} friend came with them. The {animal_friend} could talk to all the garden animals!\n\nThe fairy queen told them what was wrong. The water needed happy laughs from nice kids.\n\n{names_text} had a fun idea. They would play games with all the fairies!\n\nThey used their {magic_tool} to make pretty lights. Their {adventure_pack} had treats for everyone.\n\nTheir {animal_friend} friend told funny jokes. All the fairies laughed and giggled!\n\nWhen they all laughed together, something magic happened. The water started to work again!\n\nThe flowers became pretty and bright. The fairies were so happy!\n\nThey gave {names_text} a special gift. They would always find magic when they are kind to others."
        }
        
        base_content = topic_stories.get(request.topic, f"{names_text} had an amazing adventure with their {magic_tool}, {adventure_pack}, and {animal_friend} friend, learning that kindness and friendship are the most important things in the world.")
        
        # Use the complete story - don't truncate as it breaks the narrative
        # Only extend if the story is too short
        words = base_content.split()
        if len(words) < min_words:
            # Extend if too short
            extension = f"\n\nThey smiled and laughed together. They shared their joy with everyone.\n\nThey learned good things. They learned about being friends and helping others.\n\nTheir {magic_tool} helped them be brave. Their {adventure_pack} helped them be ready.\n\nTheir {animal_friend} friend showed them how to be loyal. It was the best day ever!"
            content = base_content + extension
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
            image_url=None,
            magic_tool=magic_tool,
            adventure_pack=adventure_pack,
            animal_friend=animal_friend
        )