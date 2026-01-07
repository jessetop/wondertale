#!/usr/bin/env python3
"""
Simple test to check OpenAI connection
"""

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded from .env file")
except ImportError:
    print("⚠ Warning: python-dotenv not installed")

import os

# Check API key
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✓ OpenAI API key found (length: {len(api_key)})")
else:
    print("✗ OpenAI API key not found")
    exit(1)

# Test OpenAI import and connection
try:
    from openai import OpenAI
    print("✓ OpenAI package imported successfully")
    
    # Create client
    client = OpenAI(api_key=api_key, timeout=10.0)
    print("✓ OpenAI client created")
    
    # Test simple API call
    print("🔄 Testing OpenAI API connection...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, API is working!' in exactly 5 words."}
        ],
        max_tokens=20,
        temperature=0.1
    )
    
    result = response.choices[0].message.content
    print(f"✓ OpenAI API response: {result}")
    print("🎉 OpenAI connection test successful!")
    
except ImportError as e:
    print(f"✗ Failed to import OpenAI: {e}")
except Exception as e:
    print(f"✗ OpenAI API test failed: {e}")