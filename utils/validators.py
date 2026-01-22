import re


def validate_email(email):
    if not email or email.strip() == "":
        return False, "Email is required"
   
    # Email text checker
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
   
    if not re.match(pattern, email):
        return False, "Invalid email format"
   
    return True, ""


def validate_password(password):
    #Making password strongggggg
    if not password or password.strip() == "":
        return False, "Password is required"
   
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
   
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
   
    if not (has_letter and has_number):
        return False, "Password must contain both letters and numbers"
   
    return True, ""


def validate_name(name):


    if not name or name.strip() == "":
        return False, "Name is required"
   
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
   
    if len(name.strip()) > 50:
        return False, "Name must be less than 50 characters"
   
    return True, ""


def validate_registration(name, email, password, confirm_password):


    # name checker
    valid, error = validate_name(name)
    if not valid:
        return False, error
   
    # name checker
    valid, error = validate_email(email)
    if not valid:
        return False, error
   
    # password checker
    valid, error = validate_password(password)
    if not valid:
        return False, error
   
    # password same or no
    if password != confirm_password:
        return False, "Passwords do not match"
   
    return True, "Validation successful"



