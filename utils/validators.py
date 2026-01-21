# utils/validators.py

import re

def validate_email(email):
    """
    Validate email format
    Returns: (is_valid: bool, error_message: str)
    """
    if not email or email.strip() == "":
        return False, "Email is required"
    
    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, ""

def validate_password(password):
    """
    Validate password strength
    Requirements:
    - At least 6 characters
    - Contains at least one letter and one number
    
    Returns: (is_valid: bool, error_message: str)
    """
    if not password or password.strip() == "":
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Check for at least one letter and one number
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        return False, "Password must contain both letters and numbers"
    
    return True, ""

def validate_name(name):
    """
    Validate user name
    Returns: (is_valid: bool, error_message: str)
    """
    if not name or name.strip() == "":
        return False, "Name is required"
    
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name.strip()) > 50:
        return False, "Name must be less than 50 characters"
    
    return True, ""

def validate_registration(name, email, password, confirm_password):
    """
    Validate complete registration form
    Returns: (is_valid: bool, error_message: str)
    """
    # Validate name
    valid, error = validate_name(name)
    if not valid:
        return False, error
    
    # Validate email
    valid, error = validate_email(email)
    if not valid:
        return False, error
    
    # Validate password
    valid, error = validate_password(password)
    if not valid:
        return False, error
    
    # Check if passwords match
    if password != confirm_password:
        return False, "Passwords do not match"
    
    return True, "Validation successful"