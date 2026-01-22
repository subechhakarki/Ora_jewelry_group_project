import hashlib
import secrets
import string


def hash_password(password, salt=None):
    if salt is None:
        # Randomly generate random things to hide the password with
        salt = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
   
    # Hiding the password with random stuff
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
   
    return hashed, salt


def verify_password(password, hashed_password, salt):
    test_hash, _ = hash_password(password, salt)
    return test_hash == hashed_password


def generate_secure_token(length=32):
    return secrets.token_urlsafe(length)



