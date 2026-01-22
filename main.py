# main.py
"""
Main entry point for ORA Jewelry Store Application
Option B fix: use .after(0, ...) so screen switching happens
after the current button-click event finishes.
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox

from db.database import init_database
from themes.theme import setup_theme, configure_window
from ui.auth_ui import LoginScreen, RegistrationScreen
from utils.helpers import SessionManager
from ui.admin_ui import AdminDashboard
from ui.product_ui import UserProductBrowseScreen


class ORAJewelryApp:
    """
    Main application class - the "remote control" for switching screens
    """

    def __init__(self):
        print("🚀 Starting ORA Jewelry Store...")
        init_database()
        setup_theme()

        self.root = ctk.CTk()
        configure_window(self.root, "ORA Jewelry Store")

        self.current_user = None  # keep user info for navigation

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
        self.root.after(0, self._show_login_screen)

    def show_registration_screen(self):
        self.root.after(0, self._show_registration_screen)

    # =========================
    # SCREEN ROUTING (INTERNAL)
    # =========================
    def _show_login_screen(self):
        print("📺 Switching to: Login Screen")
        self._clear_root()

        self.login_screen = LoginScreen(
            parent=self.root,
            on_success=self.handle_login_success,
            on_register=self.show_registration_screen
        )

    def _show_registration_screen(self):
        print("📺 Switching to: Registration Screen")
        self._clear_root()

        self.reg_screen = RegistrationScreen(
            parent=self.root,
            on_success=self.handle_registration_success,
            on_back=self.show_login_screen
        )

    # =========================
    # AUTH SUCCESS HANDLERS
    # =========================
    def handle_login_success(self, user_data):
        """
        Called when login is successful
        user_data: user_id, user_name, user_email, user_role
        """
        print(f"✅ Login successful! Welcome {user_data['user_name']}")

        self.current_user = user_data

        SessionManager.create_session(user_data)

        messagebox.showinfo(
            "Welcome!",
            f"Login successful!\nWelcome back, {user_data['user_name']}!"
        )

        if user_data["user_role"] == "admin":
            self.show_admin_dashboard(user_data)
        else:
            self.show_user_dashboard(user_data)

    def handle_registration_success(self):
        print("✅ Registration successful!")

        messagebox.showinfo(
            "Success!",
            "Account created successfully!\nYou can now login with your credentials."
        )

        self.show_login_screen()

    # =========================
    # DASHBOARDS
    # =========================
    def show_admin_dashboard(self, user_data):
        print("👑 Showing Admin Dashboard (User Management)")
        self._clear_root()

        self.admin_dashboard = AdminDashboard(
            parent=self.root,
            on_logout=self.logout
        )

    def show_user_dashboard(self, user_data):
        """
        Simple user dashboard with a Browse Products button (Step 8)
        """
        print("👤 Showing User Dashboard")
        self._clear_root()

        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        title = ctk.CTkLabel(
            main_frame,
            text=f"👋 Welcome, {user_data['user_name']}!",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=(0, 20))

        browse_btn = ctk.CTkButton(
            main_frame,
            text="💎 Browse Products",
            command=lambda: self.open_browse_products(user_data),
            width=260,
            height=48,
            corner_radius=999,  # pill
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=("Segoe UI", 14, "bold")
        )
        browse_btn.pack(pady=10)

        logout_btn = ctk.CTkButton(
            main_frame,
            text="Logout",
            command=self.logout,
            width=260,
            height=45,
            corner_radius=999,  # pill
            font=("Segoe UI", 13)
        )
        logout_btn.pack(pady=10)

    # =========================
    # STEP 8: PRODUCT BROWSING
    # =========================
    def open_browse_products(self, user_data):
        """
        Open product browsing screen for all users (Step 8).
        """
        print("🛍️ Opening Product Browse Screen")
        self._clear_root()

        self.browse_screen = UserProductBrowseScreen(
            parent=self.root,
            user_data=user_data,
            on_back=lambda: self.show_user_dashboard(user_data)
        )

    # =========================
    # LOGOUT
    # =========================
    def logout(self):
        print("👋 Logging out...")

        SessionManager.clear_session()
        self.current_user = None

        messagebox.showinfo("Logged Out", "You have been logged out successfully.")
        self.show_login_screen()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("=" * 50)
    print("ORA JEWELRY STORE - STARTING APPLICATION")
    print("=" * 50)

    app = ORAJewelryApp()
    app.run()
