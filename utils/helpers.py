import json
import os
from datetime import datetime, timedelta


SESSION_FILE = "session.json"


class SessionManager:


    @staticmethod
    def create_session(user_data):


        session_data = {
            'user_id': user_data.get('user_id'),
            'user_name': user_data.get('user_name'),
            'user_email': user_data.get('user_email'),
            'user_role': user_data.get('user_role'),
            'created_at': str(datetime.now()),
            'expires_at': str(datetime.now() + timedelta(hours=24))
        }
       
        try:
            with open(SESSION_FILE, 'w') as f:
                json.dump(session_data, f, indent=4)
            print(f"Session created for {user_data.get('user_email')}")
        except Exception as e:
            print(f"Error creating session: {e}")
       
        return session_data
   
    @staticmethod
    def get_current_session():


        if not os.path.exists(SESSION_FILE):
            return None
       
        try:
            with open(SESSION_FILE, 'r') as f:
                session_data = json.load(f)
           
            # session end or no
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                SessionManager.clear_session()
                return None
           
            return session_data
        except Exception as e:
            print(f"Error reading session: {e}")
            return None
   
    @staticmethod
    def get_current_user():
        session = SessionManager.get_current_session()
        if session:
            return {
                'user_id': session['user_id'],
                'user_name': session['user_name'],
                'user_email': session['user_email'],
                'user_role': session['user_role']
            }
        return None
   
    @staticmethod
    def clear_session():
        try:
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
                print("Session cleared")
        except Exception as e:
            print(f"Error clearing session: {e}")
   
    @staticmethod
    def is_logged_in():
        return SessionManager.get_current_session() is not None
   
    @staticmethod
    def is_admin():
        session = SessionManager.get_current_session()
        return session and session.get('user_role') == 'admin'




def format_price(price):
    return f"Rs.{price:,.2f}"


def validate_image_file(filename):
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
   
    if not filename:
        return False, "No file selected"
   
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
   
    return True, ""


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text, max_length=50):
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def calculate_total(items):
    total = 0
    for item in items:
        total += item.get('price', 0) * item.get('quantity', 0)
    return total



