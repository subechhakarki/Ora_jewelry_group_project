# main.py
"""
Main entry point for ORA Jewelry Store Application
"""

import customtkinter as ctk
from db.database import init_database
from themes.theme import setup_theme, configure_window, Colors
from ui.auth_ui import LoginScreen, RegistrationScreen
from utils.helpers import SessionManager
import tkinter.messagebox as messagebox

class ORAJewelryApp:
    """
    Main application class - the "remote control" for switching screens
    """
    def __init__(self):
        # Step 1: Setup the foundation
        print("🚀 Starting ORA Jewelry Store...")
        init_database()      # Create database tables
        setup_theme()        # Apply purple & white theme
        
        # Step 2: Create the main window
        self.root = ctk.CTk()
        configure_window(self.root, "ORA Jewelry Store")
        
        # Step 3: Start with the login screen
        self.show_login_screen()
        
        print("✅ App is ready!")
    
    def show_login_screen(self):
        """
        Show the Login Screen (TV Channel 1)
        """
        print("📺 Switching to: Login Screen")
        
        # Clear any old screens
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create Login Screen and give it the remote control buttons:
        # 1. If login succeeds → go to dashboard
        # 2. If click "Register here" → go to registration screen
        self.login_screen = LoginScreen(
            parent=self.root,
            on_success=self.handle_login_success,      # Button: "Login"
            on_register=self.show_registration_screen  # Button: "Register here"
        )
    
    def show_registration_screen(self):
        """
        Show the Registration Screen (TV Channel 2)
        """
        print("📺 Switching to: Registration Screen")
        
        # Clear any old screens
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create Registration Screen and give it the remote control buttons:
        # 1. If registration succeeds → go back to login
        # 2. If click "Login here" → go back to login
        self.reg_screen = RegistrationScreen(
            parent=self.root,
            on_success=self.handle_registration_success,  # Button: "Create Account"
            on_back=self.show_login_screen               # Button: "Login here"
        )
    
    def handle_login_success(self, user_data):
        """
        Called when login is successful
        user_data contains: user_id, user_name, user_email, user_role
        """
        print(f"✅ Login successful! Welcome {user_data['user_name']}")
        
        # Save the login session
        SessionManager.create_session(user_data)
        
        # Show welcome message
        messagebox.showinfo(
            "Welcome!",
            f"Login successful!\nWelcome back, {user_data['user_name']}!"
        )
        
        # Route to the right dashboard based on role
        if user_data['user_role'] == 'admin':
            self.show_admin_dashboard(user_data)
        else:
            self.show_user_dashboard(user_data)
    
    def handle_registration_success(self):
        """
        Called when registration is successful
        """
        print("✅ Registration successful!")
        
        # Show success message
        messagebox.showinfo(
            "Success!",
            "Account created successfully!\nYou can now login with your credentials."
        )
        
        # Automatically go back to login screen
        self.show_login_screen()
    
    def show_admin_dashboard(self, user_data):
        """
        Show Admin Dashboard (to be built in Step 19)
        For now, just show a placeholder
        """
        print("👑 Showing Admin Dashboard")
        
        # Clear screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Temporary placeholder
        main_frame = ctk.CTkFrame(self.root, fg_color=Colors.BG_LIGHT)
        main_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            main_frame,
            text=f"👑 ADMIN DASHBOARD\n\nWelcome, {user_data['user_name']}!",
            font=("Segoe UI", 28, "bold"),
            text_color="#8B5CF6"
        )
        welcome_label.pack(pady=40)
        
        info_label = ctk.CTkLabel(
            main_frame,
            text="This is the admin dashboard.\nYou can manage users, products, and orders here.\n\n(Step 19 will build the complete dashboard)",
            font=("Segoe UI", 16),
            text_color="#6B7280"
        )
        info_label.pack(pady=20)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            main_frame,
            text="Logout",
            command=self.logout,
            width=200,
            height=45,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=("Segoe UI", 14, "bold")
        )
        logout_btn.pack(pady=30)
    
    def show_user_dashboard(self, user_data):
        """
        Show User Dashboard (to be built in Step 18)
        For now, just show a placeholder
        """
        print("👤 Showing User Dashboard")
        
        # Clear screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Temporary placeholder
        main_frame = ctk.CTkFrame(self.root, fg_color=Colors.BG_LIGHT)
        main_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            main_frame,
            text=f"👤 USER DASHBOARD\n\nWelcome, {user_data['user_name']}!",
            font=("Segoe UI", 28, "bold"),
            text_color="#8B5CF6"
        )
        welcome_label.pack(pady=40)
        
        info_label = ctk.CTkLabel(
            main_frame,
            text="This is your dashboard.\nYou can browse jewelry, manage cart, and view orders here.\n\n(Step 18 will build the complete dashboard)",
            font=("Segoe UI", 16),
            text_color="#6B7280"
        )
        info_label.pack(pady=20)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            main_frame,
            text="Logout",
            command=self.logout,
            width=200,
            height=45,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=("Segoe UI", 14, "bold")
        )
        logout_btn.pack(pady=30)
    
    def logout(self):
        """
        Logout the current user
        """
        print("👋 Logging out...")
        
        # Clear the session
        SessionManager.clear_session()
        
        # Show logout message
        messagebox.showinfo("Logged Out", "You have been logged out successfully.")
        
        # Go back to login screen
        self.show_login_screen()
    
    def run(self):
        """
        Start the application
        """
        self.root.mainloop()

# ============================================
# START THE APPLICATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("ORA JEWELRY STORE - STARTING APPLICATION")
    print("=" * 50)
    
    app = ORAJewelryApp()
    app.run()