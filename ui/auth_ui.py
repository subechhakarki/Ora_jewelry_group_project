# ui/auth_ui.py

import customtkinter as ctk
from themes.theme import *
from utils.validators import validate_registration, validate_email, validate_password
from db.user_queries import create_user, verify_login
import tkinter.messagebox as messagebox

# ============================================
# REGISTRATION SCREEN
# ============================================

class RegistrationScreen:
    """
    User Registration Screen
    """
    def __init__(self, parent, on_success=None, on_back=None):
        """
        Args:
            parent: Parent window/frame
            on_success: Callback function when registration succeeds
            on_back: Callback function for back button
        """
        self.parent = parent
        self.on_success = on_success
        self.on_back = on_back
        
        self.create_ui()
    
    def create_ui(self):
        """Create the registration interface"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        
        # Center container
        center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Registration card
        card = ctk.CTkFrame(center_frame, **get_card_style(), width=450)
        card.pack(padx=Layout.PADDING_LARGE, pady=Layout.PADDING_LARGE)
        
        # Logo/Title
        title = ctk.CTkLabel(
            card, 
            text="💎 ORA Jewelry Store",
            **get_label_style("title")
        )
        title.pack(pady=(Layout.PADDING_LARGE, Layout.PADDING_SMALL))
        
        subtitle = ctk.CTkLabel(
            card,
            text="Create your account",
            **get_label_style("heading")
        )
        subtitle.pack(pady=(0, Layout.PADDING_LARGE))
        
        # Name input
        name_label = ctk.CTkLabel(card, text="Full Name", **get_label_style("normal"))
        name_label.pack(anchor="w", padx=Layout.PADDING_LARGE, pady=(Layout.PADDING_SMALL, 0))
        
        self.name_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter your full name",
            width=400,
            **get_input_style()
        )
        self.name_entry.pack(padx=Layout.PADDING_LARGE, pady=(5, Layout.PADDING_SMALL))
        
        # Email input
        email_label = ctk.CTkLabel(card, text="Email", **get_label_style("normal"))
        email_label.pack(anchor="w", padx=Layout.PADDING_LARGE, pady=(Layout.PADDING_SMALL, 0))
        
        self.email_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter your email",
            width=400,
            **get_input_style()
        )
        self.email_entry.pack(padx=Layout.PADDING_LARGE, pady=(5, Layout.PADDING_SMALL))
        
        # Password input
        password_label = ctk.CTkLabel(card, text="Password", **get_label_style("normal"))
        password_label.pack(anchor="w", padx=Layout.PADDING_LARGE, pady=(Layout.PADDING_SMALL, 0))
        
        self.password_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter password (min 6 chars)",
            show="●",
            width=400,
            **get_input_style()
        )
        self.password_entry.pack(padx=Layout.PADDING_LARGE, pady=(5, Layout.PADDING_SMALL))
        
        # Confirm password input
        confirm_label = ctk.CTkLabel(card, text="Confirm Password", **get_label_style("normal"))
        confirm_label.pack(anchor="w", padx=Layout.PADDING_LARGE, pady=(Layout.PADDING_SMALL, 0))
        
        self.confirm_entry = ctk.CTkEntry(
            card,
            placeholder_text="Re-enter password",
            show="●",
            width=400,
            **get_input_style()
        )
        self.confirm_entry.pack(padx=Layout.PADDING_LARGE, pady=(5, Layout.PADDING_MEDIUM))
        
        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            card,
            text="",
            text_color=Colors.ERROR,
            font=(Fonts.FAMILY, Fonts.SMALL)
        )
        self.error_label.pack(pady=(0, Layout.PADDING_SMALL))
        
        # Register button
        register_btn = ctk.CTkButton(
            card,
            text="Create Account",
            width=400,
            command=self.handle_registration,
            **get_button_style("primary")
        )
        register_btn.pack(padx=Layout.PADDING_LARGE, pady=(Layout.PADDING_SMALL, Layout.PADDING_MEDIUM))
        
        # Back to login link
        login_frame = ctk.CTkFrame(card, fg_color="transparent")
        login_frame.pack(pady=(0, Layout.PADDING_LARGE))
        
        login_label = ctk.CTkLabel(
            login_frame,
            text="Already have an account?",
            **get_label_style("small")
        )
        login_label.pack(side="left", padx=(0, 5))
        
        login_btn = ctk.CTkButton(
            login_frame,
            text="Login here",
            fg_color="transparent",
            text_color=Colors.PRIMARY,
            hover_color=Colors.BG_GRAY,
            width=80,
            height=25,
            font=(Fonts.FAMILY, Fonts.SMALL, "underline"),
            command=self.handle_back
        )
        login_btn.pack(side="left")
        
        # Bind Enter key
        self.confirm_entry.bind("<Return>", lambda e: self.handle_registration())
    
    def handle_registration(self):
        """Handle registration button click"""
        # Clear previous error
        self.error_label.configure(text="")
        
        # Get input values
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_entry.get()
        
        # Validate inputs
        is_valid, message = validate_registration(name, email, password, confirm_password)
        
        if not is_valid:
            self.show_error(message)
            return
        
        # Create user in database (password will be hashed automatically)
        success, message, user_id = create_user(name, email, password, role='user')
        
        if success:
            messagebox.showinfo("Success", "Account created successfully!\nYou can now login.")
            if self.on_success:
                self.on_success()
        else:
            self.show_error(message)
    
    def show_error(self, message):
        """Display error message"""
        self.error_label.configure(text=f"⚠️ {message}")
    
    def handle_back(self):
        """Handle back button click"""
        if self.on_back:
            self.on_back()
    
    def destroy(self):
        """Destroy the registration screen"""
        self.main_frame.destroy()

# ============================================
# LOGIN SCREEN
# ============================================

class LoginScreen:
    """
    User Login Screen
    """
    def __init__(self, parent, on_success=None, on_register=None):
        """
        Args:
            parent: Parent window/frame
            on_success: Callback function when login succeeds (receives user_data)
            on_register: Callback function for register button
        """
        self.parent = parent
        self.on_success = on_success
        self.on_register = on_register
        
        self.create_ui()
    
    def create_ui(self):
        """Create the login interface"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        
        # Center container
        center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Login card
        card = ctk.CTkFrame(center_frame, **get_card_style(), width=450)
        card.pack(padx=Layout.PADDING_LARGE, pady=Layout.PADDING_LARGE)
        
        # Logo/Title
        title = ctk.CTkLabel(
            card, 
            text="💎 ORA Jewelry Store",
            **get_label_style("title")
        )
        title.pack(pady=(Layout.PADDING_LARGE, Layout.PADDING_SMALL))
        
        subtitle = ctk.CTkLabel(
            card,
            text="Welcome back!",
            **get_label_style("heading")
        )
        subtitle.pack(pady=(0, Layout.PADDING_LARGE))
        
        # Email input
        email_label = ctk.CTkLabel(card, text="Email", **get_label_style("normal"))
        email_label.pack(anchor="w", padx=Layout.PADDING_LARGE, pady=(Layout.PADDING_SMALL, 0))
        
        self.email_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter your email",
            width=400,
            **get_input_style()
        )
        self.email_entry.pack(padx=Layout.PADDING_LARGE, pady=(5, Layout.PADDING_SMALL))
        
        # Password input
        password_label = ctk.CTkLabel(card, text="Password", **get_label_style("normal"))
        password_label.pack(anchor="w", padx=Layout.PADDING_LARGE, pady=(Layout.PADDING_SMALL, 0))
        
        self.password_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter your password",
            show="●",
            width=400,
            **get_input_style()
        )
        self.password_entry.pack(padx=Layout.PADDING_LARGE, pady=(5, Layout.PADDING_MEDIUM))
        
        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            card,
            text="",
            text_color=Colors.ERROR,
            font=(Fonts.FAMILY, Fonts.SMALL)
        )
        self.error_label.pack(pady=(0, Layout.PADDING_SMALL))
        
        # Login button
        login_btn = ctk.CTkButton(
            card,
            text="Login",
            width=400,
            command=self.handle_login,
            **get_button_style("primary")
        )
        login_btn.pack(padx=Layout.PADDING_LARGE, pady=(Layout.PADDING_SMALL, Layout.PADDING_MEDIUM))
        
        # Register link
        register_frame = ctk.CTkFrame(card, fg_color="transparent")
        register_frame.pack(pady=(0, Layout.PADDING_LARGE))
        
        register_label = ctk.CTkLabel(
            register_frame,
            text="Don't have an account?",
            **get_label_style("small")
        )
        register_label.pack(side="left", padx=(0, 5))
        
        register_btn = ctk.CTkButton(
            register_frame,
            text="Register here",
            fg_color="transparent",
            text_color=Colors.PRIMARY,
            hover_color=Colors.BG_GRAY,
            width=80,
            height=25,
            font=(Fonts.FAMILY, Fonts.SMALL, "underline"),
            command=self.handle_register
        )
        register_btn.pack(side="left")
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
    
    def handle_login(self):
        """Handle login button click"""
        # Clear previous error
        self.error_label.configure(text="")
        
        # Get input values
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        # Basic validation
        if not email or not password:
            self.show_error("Please enter both email and password")
            return
        
        # Validate email format
        valid, error = validate_email(email)
        if not valid:
            self.show_error(error)
            return
        
        # Verify login credentials
        success, message, user_data = verify_login(email, password)
        
        if success:
            if self.on_success:
                self.on_success(user_data)
        else:
            self.show_error(message)
    
    def show_error(self, message):
        """Display error message"""
        self.error_label.configure(text=f"⚠️ {message}")
    
    def handle_register(self):
        """Handle register button click"""
        if self.on_register:
            self.on_register()
    
    def destroy(self):
        """Destroy the login screen"""
        self.main_frame.destroy()