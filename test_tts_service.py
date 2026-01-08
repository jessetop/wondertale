"""
Test script for TTS Service functionality
"""

import os
import sys
from services.tts_service import TTSService

def test_tts_service():
    """Test TTS service initialization and voice availability"""
    print("Testing TTS Service...")
    
    # Initialize service
    tts_service = TTSService()
    
    # Check availability
    is_available = tts_service.is_available()
    print(f"TTS Service Available: {is_available}")
    
    # Get voices
    voices = tts_service.get_voices()
    print(f"Available voices: {list(voices.keys())}")
    
    for voice_key, voice_info in voices.items():
        print(f"  {voice_key}: {voice_info['name']} ({voice_info['emoji']}) - {voice_info['description']}")
    
    # Test audio generation (only if API key is available)
    if is_available:
        print("\nTesting audio generation...")
        test_text = "Hello! This is a test of the AI voice system for WonderTales stories."
        
        audio_path = tts_service.generate_audio(test_text, 'friendly')
        if audio_path:
            print(f"Audio generated successfully: {audio_path}")
            
            # Check file exists
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"Audio file size: {file_size} bytes")
            else:
                print("Warning: Audio file not found")
        else:
            print("Audio generation failed")
    else:
        print("Skipping audio generation test (API key not available)")
    
    print("TTS Service test complete!")

if __name__ == "__main__":
    test_tts_service()