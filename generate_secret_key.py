#!/usr/bin/env python3
"""
Generate a secure secret key for Flask production use
"""

import secrets

def generate_secret_key():
    """Generate a cryptographically secure secret key"""
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    key = generate_secret_key()
    print("Generated Flask Secret Key:")
    print(key)
    print("\nAdd this to Railway environment variables as:")
    print(f"FLASK_SECRET_KEY={key}")