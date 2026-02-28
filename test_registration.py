# test_registration.py

import customtkinter as ctk
from themes.theme import setup_theme, configure_window
from ui.auth_ui import RegistrationScreen
from db.database import init_database

def test_registration():
    """Test the registration screen"""
    # Initialize database
    init_database()
    
    # Setup theme
    setup_theme()
    
    # Create main window
    root = ctk.CTk()
    configure_window(root, "ORA Jewelry - Registration Test")
    
    # Callback functions
    def on_success():
        print("✅ Registration successful!")
    
    def on_back():
        print("🔙 Back button clicked")
     # this is user registration to
    # Create registration screen
    reg_screen = RegistrationScreen(root, on_success=on_success, on_back=on_back)
    
    root.mainloop()

if __name__ == "__main__":
    test_registration()