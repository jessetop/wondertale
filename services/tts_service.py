"""
Text-to-Speech Service using OpenAI TTS API
Provides natural, child-friendly voice generation for stories
"""

import os
import tempfile
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. TTS functionality will be limited.")


class TTSService:
    """Text-to-Speech service using OpenAI's TTS API"""
    
    def __init__(self):
        """Initialize TTS service with OpenAI client"""
        if not OPENAI_AVAILABLE:
            self.client = None
            return
            
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not found. TTS functionality will be limited.")
            self.client = None
            return
            
        self.client = OpenAI(api_key=api_key)
        
        # Voice options optimized for children's stories
        self.voices = {
            'friendly': {
                'voice': 'nova',  # Female, warm and friendly
                'name': 'Friendly',
                'description': 'A warm, friendly voice perfect for bedtime stories',
                'emoji': '👩'
            },
            'cheerful': {
                'voice': 'onyx',  # Male, clear and engaging
                'name': 'Cheerful', 
                'description': 'An upbeat, cheerful voice that brings stories to life',
                'emoji': '👨'
            },
            'magical': {
                'voice': 'shimmer',  # Expressive, great for fantasy
                'name': 'Magical',
                'description': 'An enchanting voice perfect for magical adventures',
                'emoji': '🌟'
            }
        }
        
        # Create audio cache directory
        self.cache_dir = Path(tempfile.gettempdir()) / 'wondertales_audio'
        self.cache_dir.mkdir(exist_ok=True)
    
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        return OPENAI_AVAILABLE and self.client is not None
    
    def get_voices(self) -> Dict[str, Dict[str, Any]]:
        """Get available voice options"""
        return self.voices
    
    def generate_audio(self, text: str, voice_key: str = 'friendly') -> Optional[str]:
        """
        Generate audio file from text using OpenAI TTS
        
        Args:
            text: The story text to convert to speech
            voice_key: Voice option key ('friendly', 'cheerful', 'magical')
            
        Returns:
            Path to generated audio file, or None if generation failed
        """
        if not self.is_available():
            return None
            
        if voice_key not in self.voices:
            voice_key = 'friendly'  # Default fallback
            
        try:
            # Create cache key from text and voice
            cache_key = hashlib.md5(f"{text}_{voice_key}".encode()).hexdigest()
            cache_file = self.cache_dir / f"{cache_key}.mp3"
            
            # Return cached file if it exists
            if cache_file.exists():
                return str(cache_file)
            
            # Generate audio using OpenAI TTS
            voice_config = self.voices[voice_key]
            
            response = self.client.audio.speech.create(
                model="tts-1",  # Use tts-1 for faster generation, tts-1-hd for higher quality
                voice=voice_config['voice'],
                input=text,
                speed=0.9  # Slightly slower for children
            )
            
            # Save audio to cache file
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            return str(cache_file)
            
        except Exception as e:
            print(f"Error generating TTS audio: {e}")
            return None
    
    def cleanup_old_cache(self, max_age_hours: int = 24):
        """Clean up old cached audio files"""
        try:
            import time
            current_time = time.time()
            
            for file_path in self.cache_dir.glob("*.mp3"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (max_age_hours * 3600):  # Convert hours to seconds
                    file_path.unlink()
                    
        except Exception as e:
            print(f"Error cleaning up TTS cache: {e}")