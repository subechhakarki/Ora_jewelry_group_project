import customtkinter as ctk
import tkinter.messagebox as messagebox


from db.database import init_database
from themes.theme import setup_theme, configure_window
from ui.auth_ui import LoginScreen, RegistrationScreen
from utils.helpers import SessionManager
from ui.admin_ui import AdminDashboard
from ui.product_ui import UserProductBrowseScreen
from ui.cart_ui import CartScreen
from ui.order_ui import UserOrderHistoryScreen


class ORAJewelryApp:




    def __init__(self):
        print(" Starting ORA Jewelry Store...")
        init_database()
        setup_theme()


        self.root = ctk.CTk()
        configure_window(self.root, "ORA Jewelry Store")


        self.current_user = None  # keep user info for nav


        self.show_login_screen()
        print(" App is ready!")


    def _clear_root(self):
        """Delete window."""
        for widget in self.root.winfo_children():
            widget.destroy()




    # SCREEN CHANGE TO PUBLIC


    def show_login_screen(self):
        self.root.after(0, self._show_login_screen)


    def show_registration_screen(self):
        self.root.after(0, self._show_registration_screen)




    # SCREEN CHANGE
    def _show_login_screen(self):
        print("Switching to: Login")
        self._clear_root()


        self.login_screen = LoginScreen(
            parent=self.root,
            on_success=self.handle_login_success,
            on_register=self.show_registration_screen
        )


    def _show_registration_screen(self):
        print("Switching to: Registration")
        self._clear_root()


        self.reg_screen = RegistrationScreen(
            parent=self.root,
            on_success=self.handle_registration_success,
            on_back=self.show_login_screen
        )


    # Log in  successful result
    def handle_login_success(self, user_data):


        print(f"Login successful!!!")


        self.current_user = user_data


        SessionManager.create_session(user_data)


        messagebox.showinfo(
            "Welcome!",
            f"Login successful!!!"
        )


        if user_data["user_role"] == "admin":
            self.show_admin_dashboard(user_data)
        else:
            self.show_user_dashboard(user_data)


    def handle_registration_success(self):
        print("Registration successful!!!")


        messagebox.showinfo(
            "Account created",
            "You can now login with your credentials"
        )


        self.show_login_screen()




    # DASHBOARDS
    def show_admin_dashboard(self, user_data):
        print("Admin Dashboard (User Management)")
        self._clear_root()


        self.admin_dashboard = AdminDashboard(
            parent=self.root,
            on_logout=self.logout
        )


    def show_user_dashboard(self, user_data):
        print("Showing User Dashboard")
        self._clear_root()


        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)


        title = ctk.CTkLabel(
            main_frame,
            text=f"Welcome!!!",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=(0, 20))


        browse_btn = ctk.CTkButton(
            main_frame,
            text="💎 Browse Products",
            command=lambda: self.open_browse_products(user_data),
            width=260,
            height=48,
            corner_radius=999,  
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            font=("Segoe UI", 14, "bold")
        )
        browse_btn.pack(pady=10)
        cart_btn = ctk.CTkButton(
            main_frame,
            text="🛒 View Cart",
            command=lambda: self.open_cart(user_data),
            width=260,
            height=48,
            corner_radius=999,
            fg_color="#10B981",  
            hover_color="#059669",
            font=("Segoe UI", 14, "bold")
        )
        cart_btn.pack(pady=10)
       
        orders_btn = ctk.CTkButton(
            main_frame,
            text="📦 My Orders",
            command=lambda: self.open_orders(user_data),
            width=260,
            height=48,
            corner_radius=999,
            fg_color="#F59E0B",  
            hover_color="#D97706",
            font=("Segoe UI", 14, "bold")
        )
        orders_btn.pack(pady=10)




        logout_btn = ctk.CTkButton(
            main_frame,
            text="🚪Logout",
            command=self.logout,
            width=260,
            height=45,
            corner_radius=999,  
            font=("Segoe UI", 13)
        )
        logout_btn.pack(pady=10)




    # PRODUCT


    def open_browse_products(self, user_data):


        print("Opening Product Browse Screen")
        self._clear_root()


        self.browse_screen = UserProductBrowseScreen(
            parent=self.root,
            user_data=user_data,
            on_back=lambda: self.show_user_dashboard(user_data)
        )


    def open_cart(self, user_data):
        print("Opening Cart Screen")
        self._clear_root()


       


        self.cart_screen = CartScreen(
            parent=self.root,
            user_id=user_data["user_id"],
            on_back=lambda: self.show_user_dashboard(user_data)
        )
        self.cart_screen.pack(fill="both", expand=True)
       
       
    def open_orders(self, user_data):
        print("Opening Orders Screen")
        self._clear_root()


           


        self.orders_screen = UserOrderHistoryScreen(
            parent=self.root,
            user_id=user_data["user_id"],
            on_back=lambda: self.show_user_dashboard(user_data)
        )
        self.orders_screen.pack(fill="both", expand=True)








    # LOGOUT


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





