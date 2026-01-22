# main.py
"""
Main entry point for ORA Jewelry Store Application
Option B fix: use .after(0, ...) so screen switching happens
after the current button-click event finishes.
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox



from db.database import init_database
from themes.theme import setup_theme, configure_window, Colors
from ui.auth_ui import LoginScreen, RegistrationScreen
from utils.helpers import SessionManager
from ui.admin_ui import AdminDashboard


class ORAJewelryApp:
    """
    Main application class - the "remote control" for switching screens
    """

    def __init__(self):
        # Step 1: Setup the foundation
        print("🚀 Starting ORA Jewelry Store...")
        init_database()          # Create database tables
        setup_theme()            # Apply purple & white theme

        # Step 2: Create the main window
        self.root = ctk.CTk()
        configure_window(self.root, "ORA Jewelry Store")

        # Step 3: Start with the login screen
        self.show_login_screen()

        print("✅ App is ready!")

    # =========================
    # SAFE SCREEN SWITCH HELPERS
    # =========================
    def _clear_root(self):
        """Destroy all widgets in root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # =========================
    # SCREEN ROUTING (PUBLIC)
    # =========================
    def show_login_screen(self):
        """
        Public: schedule login screen render on next event-loop tick
        """
        self.root.after(0, self._show_login_screen)

    def show_registration_screen(self):
        """
        Public: schedule registration screen render on next event-loop tick
        """
        self.root.after(0, self._show_registration_screen)

    # =========================
    # SCREEN ROUTING (INTERNAL)
    # =========================
    def _show_login_screen(self):
        """
        Internal: actually render Login Screen
        """
        print("📺 Switching to: Login Screen")
        self._clear_root()

        self.login_screen = LoginScreen(
            parent=self.root,
            on_success=self.handle_login_success,          # Button: "Login"
            on_register=self.show_registration_screen      # Button: "Register here"
        )

    def _show_registration_screen(self):
        """
        Internal: actually render Registration Screen
        """
        print("📺 Switching to: Registration Screen")
        self._clear_root()

        self.reg_screen = RegistrationScreen(
            parent=self.root,
            on_success=self.handle_registration_success,   # Button: "Create Account"
            on_back=self.show_login_screen                 # Button: "Login here"
        )

    # =========================
    # AUTH SUCCESS HANDLERS
    # =========================
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

        # Go back to login screen safely
        self.show_login_screen()

    # =========================
    # DASHBOARDS (PLACEHOLDERS)
    # =========================
    def show_admin_dashboard(self, user_data):
        """
        Step 6: Admin Dashboard - User Management
        """
        print("👑 Showing Admin Dashboard (User Management)")
        self._clear_root()

        self.admin_dashboard = AdminDashboard(
            parent=self.root,
            on_logout=self.logout
        )


    # =========================
    # LOGOUT
    # =========================
    def logout(self):
        """
        Logout the current user
        """
        print("👋 Logging out...")

        # Clear the session
        SessionManager.clear_session()

        # Show logout message
        messagebox.showinfo("Logged Out", "You have been logged out successfully.")

        # Go back to login screen safely
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
