# db/user_queries.py

from db.database import get_connection, close_connection
import sqlite3
from utils.security import hash_password, verify_password

# ============================================
# CREATE USER (WITH PASSWORD HASHING)
# ============================================

def create_user(name, email, password, role='user'):
    """
    Create a new user account with hashed password
    
    Args:
        name: User's full name
        email: User's email (must be unique)
        password: User's plain text password
        role: 'user' or 'admin' (default: 'user')
    
    Returns:
        (success: bool, message: str, user_id: int or None)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if email already exists
        cursor.execute("SELECT user_id FROM users WHERE user_email = ?", (email,))
        if cursor.fetchone():
            close_connection(conn)
            return False, "Email already exists", None
        
        # Hash the password
        hashed_password, salt = hash_password(password)
        
        # Insert new user with hashed password and salt
        cursor.execute('''
            INSERT INTO users (user_name, user_email, user_password, user_salt, user_role)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, hashed_password, salt, role))
        
        conn.commit()
        user_id = cursor.lastrowid
        close_connection(conn)
        
        return True, "User created successfully", user_id
        
    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}", None

# ============================================
# LOGIN VERIFICATION
# ============================================

def verify_login(email, password):
    """
    Verify user login credentials
    
    Args:
        email: User's email
        password: Plain text password
    
    Returns:
        (success: bool, message: str, user_data: dict or None)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, user_name, user_email, user_password, user_salt, user_role, created_at
        FROM users WHERE user_email = ?
    ''', (email,))
    
    row = cursor.fetchone()
    close_connection(conn)
    
    if not row:
        return False, "Invalid email or password", None
    
    # Extract user data
    user_data = {
        'user_id': row[0],
        'user_name': row[1],
        'user_email': row[2],
        'user_password': row[3],  # Hashed password
        'user_salt': row[4],      # Salt
        'user_role': row[5],
        'created_at': row[6]
    }
    
    # Verify password using the stored hash and salt
    if verify_password(password, user_data['user_password'], user_data['user_salt']):
        # Remove sensitive data before returning
        user_data.pop('user_password')
        user_data.pop('user_salt')
        return True, "Login successful", user_data
    else:
        return False, "Invalid email or password", None

# ============================================
# GET USER BY EMAIL (WITH SALT)
# ============================================

def get_user_by_email(email):
    """
    Retrieve user by email (includes sensitive fields)
    
    Returns:
        User data as dictionary or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, user_name, user_email, user_password, user_salt, user_role, created_at
        FROM users WHERE user_email = ?
    ''', (email,))
    
    row = cursor.fetchone()
    close_connection(conn)
    
    if row:
        return {
            'user_id': row[0],
            'user_name': row[1],
            'user_email': row[2],
            'user_password': row[3],
            'user_salt': row[4],
            'user_role': row[5],
            'created_at': row[6]
        }
    return None

# ============================================
# GET USER BY ID (WITH SALT)
# ============================================

def get_user_by_id(user_id):
    """
    Retrieve user by ID (includes sensitive fields)
    
    Returns:
        User data as dictionary or None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, user_name, user_email, user_password, user_salt, user_role, created_at
        FROM users WHERE user_id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    close_connection(conn)
    
    if row:
        return {
            'user_id': row[0],
            'user_name': row[1],
            'user_email': row[2],
            'user_password': row[3],
            'user_salt': row[4],
            'user_role': row[5],
            'created_at': row[6]
        }
    return None

# ============================================
# GET ALL USERS (ADMIN ONLY) - SENSITIVE DATA REMOVED
# ============================================

def get_all_users():
    """
    Retrieve all users (without sensitive password data)
    
    Returns:
        List of user dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, user_name, user_email, user_role, created_at
        FROM users
        ORDER BY created_at DESC
    ''')
    
    rows = cursor.fetchall()
    close_connection(conn)
    
    users = []
    for row in rows:
        users.append({
            'user_id': row[0],
            'user_name': row[1],
            'user_email': row[2],
            'user_role': row[3],
            'created_at': row[4]
        })
    
    return users

# ============================================
# UPDATE USER (WITH PASSWORD HASHING)
# ============================================

def update_user(user_id, name=None, email=None, password=None):
    """
    Update user information
    
    Returns:
        (success: bool, message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Build dynamic update query
        updates = []
        params = []
        
        if name:
            updates.append("user_name = ?")
            params.append(name)
        
        if email:
            updates.append("user_email = ?")
            params.append(email)
        
        if password:
            # Hash the new password
            hashed_password, salt = hash_password(password)
            updates.append("user_password = ?")
            updates.append("user_salt = ?")
            params.append(hashed_password)
            params.append(salt)
        
        if not updates:
            close_connection(conn)
            return False, "No fields to update"
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        close_connection(conn)
        
        return True, "User updated successfully"
        
    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}"

# ============================================
# DELETE USER
# ============================================

def delete_user(user_id):
    """
    Delete a user (Admin only)
    
    Returns:
        (success: bool, message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        if cursor.rowcount == 0:
            close_connection(conn)
            return False, "User not found"
        
        conn.commit()
        close_connection(conn)
        return True, "User deleted successfully"
        
    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}"

# ============================================
# CHANGE USER ROLE
# ============================================

def change_user_role(user_id, new_role):
    """
    Promote user to admin or demote admin to user
    
    Args:
        user_id: User ID
        new_role: 'admin' or 'user'
    
    Returns:
        (success: bool, message: str)
    """
    if new_role not in ['admin', 'user']:
        return False, "Invalid role. Must be 'admin' or 'user'"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET user_role = ? WHERE user_id = ?", (new_role, user_id))
        
        if cursor.rowcount == 0:
            close_connection(conn)
            return False, "User not found"
        
        conn.commit()
        close_connection(conn)
        
        action = "promoted to admin" if new_role == 'admin' else "demoted to user"
        return True, f"User {action} successfully"
        
    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}"