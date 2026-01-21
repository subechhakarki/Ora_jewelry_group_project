# utils/security.py
"""
Password security utilities for ORA Jewelry Store
Uses SHA-256 hashing with salt for secure password storage
"""

import hashlib
import secrets
import string

def hash_password(password, salt=None):
    """
    Hash a password using SHA-256 with salt
    
    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)
    
    Returns:
        (hashed_password, salt)
    """
    if salt is None:
        # Generate a random 16-character salt
        salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    
    # Create SHA-256 hash of password + salt
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    
    return hashed, salt

def verify_password(password, hashed_password, salt):
    """
    Verify if a password matches the stored hash
    
    Args:
        password: Plain text password to check
        hashed_password: Stored hashed password
        salt: Stored salt
    
    Returns:
        bool: True if password matches
    """
    test_hash, _ = hash_password(password, salt)
    return test_hash == hashed_password

def generate_secure_token(length=32):
    """
    Generate a secure random token for sessions
    """
    return secrets.token_urlsafe(length)