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
from themes.theme import Colors



class UserShell(ctk.CTkFrame):
    def __init__(self, parent, app, user_data):
        super().__init__(parent, fg_color="#F7F5F2")
        self.app = app
        self.user_data = user_data
        self.current_view = None

        self.pack(fill="both", expand=True)

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, width=240)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        # Content area
        self.content = ctk.CTkFrame(self, fg_color="#F7F5F2", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

        self._build_sidebar()
        self.show_browse()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
        self.current_view = None

    def _build_sidebar(self):
        ctk.CTkLabel(
            self.sidebar,
            text="💎 ORA Jewelry",
            font=("Segoe UI", 18, "bold"),
            text_color="#3B1D6F"
        ).pack(anchor="w", padx=18, pady=(18, 8))

        ctk.CTkLabel(
            self.sidebar,
            text=f"Hi, {self.user_data.get('user_name','User')}",
            font=("Segoe UI", 12),
            text_color="#6B6B6B"
        ).pack(anchor="w", padx=18, pady=(0, 18))

        # Nav buttons
        nav_btn_style = {
            "width": 200,
            "height": 42,
            "corner_radius": 12,
            "fg_color": Colors.PRIMARY,          # theme color
            "hover_color": Colors.PRIMARY_DARK,  # darker hover
            "text_color": Colors.TEXT_WHITE,
            "font": ("Segoe UI", 13, "bold")
        }

        ctk.CTkButton(
            self.sidebar,
            text="💎 Browse Products",
            command=self.show_browse,
            **nav_btn_style
        ).pack(pady=6, padx=15)

        ctk.CTkButton(
            self.sidebar,
            text="🛒 View Cart",
            command=self.show_cart,
            **nav_btn_style
        ).pack(pady=6, padx=15)

        ctk.CTkButton(
            self.sidebar,
            text="📦 My Orders",
            command=self.show_orders,
            **nav_btn_style
        ).pack(pady=6, padx=15)

        ctk.CTkFrame(self.sidebar, fg_color="transparent", height=18).pack()

        ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            command=self.app.logout,
            width=200,
            fg_color="#EF4444",
            hover_color="#DC2626"
        ).pack(padx=18, pady=(18, 10))


        
    def show_browse(self):
        self._clear_content()
        from ui.product_ui import UserProductBrowseScreen
        self.current_view = UserProductBrowseScreen(
            parent=self.content,
            user_data=self.user_data,
            on_back=None,
            show_back=False
        )


    def show_cart(self):
        self._clear_content()
        from ui.cart_ui import CartScreen
        self.current_view = CartScreen(
            parent=self.content,
            user_id=self.user_data["user_id"],
            on_back=None,
            show_back=False
        )
        self.current_view.pack(fill="both", expand=True)

    def show_orders(self):
        self._clear_content()
        from ui.order_ui import UserOrderHistoryScreen
        self.current_view = UserOrderHistoryScreen(
            parent=self.content,
            user_id=self.user_data["user_id"],
            on_back=None,
            show_back=False
        )
        self.current_view.pack(fill="both", expand=True)






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
        print("USER DASHBOARD: SIDEBAR VERSION LOADED")
        self._clear_root()

        try:
            self.user_shell = UserShell(self.root, app=self, user_data=user_data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("UI Error", f"Failed to load sidebar dashboard:\n\n{e}")



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





