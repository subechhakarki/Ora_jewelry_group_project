import customtkinter as ctk
import tkinter.messagebox as messagebox


from themes.theme import (
    Colors, Layout, Fonts,
    get_button_style, get_card_style, get_label_style, get_input_style
)
from db.user_queries import get_all_users, delete_user, change_user_role, update_user
from utils.helpers import SessionManager


from ui.product_ui import AdminProductManagementScreen
from ui.order_ui import AdminOrderDashboardScreen




class EditUserDialog(ctk.CTkToplevel):
    def __init__(self, parent, user, on_saved=None):
        super().__init__(parent)
        self.user = user
        self.on_saved = on_saved


        self.title("Edit User")
        self.geometry("420x420")
        self.resizable(False, False)


        self.transient(parent)
        self.grab_set()


        container = ctk.CTkFrame(self, **get_card_style())
        container.pack(fill="both", expand=True, padx=20, pady=20)


        title = ctk.CTkLabel(container, text="Edit User", **get_label_style("heading"))
        title.pack(pady=(10, 15))


        # Name
        ctk.CTkLabel(container, text="Name", **get_label_style("normal")).pack(anchor="w", padx=20)
        self.name_entry = ctk.CTkEntry(container, width=340, **get_input_style())
        self.name_entry.pack(padx=20, pady=(5, 12))
        self.name_entry.insert(0, user["user_name"])


        # Email
        ctk.CTkLabel(container, text="Email", **get_label_style("normal")).pack(anchor="w", padx=20)
        self.email_entry = ctk.CTkEntry(container, width=340, **get_input_style())
        self.email_entry.pack(padx=20, pady=(5, 12))
        self.email_entry.insert(0, user["user_email"])


        # Password
        ctk.CTkLabel(container, text="New Password (optional)", **get_label_style("normal")).pack(anchor="w", padx=20)
        self.password_entry = ctk.CTkEntry(container, width=340, show="●", **get_input_style())
        self.password_entry.pack(padx=20, pady=(5, 20))


        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(pady=(0, 10))


        save_btn = ctk.CTkButton(
            btn_row,
            text="Save",
            width=150,
            command=self.save,
            **get_button_style("primary")
        )
        save_btn.pack(side="left", padx=8)


        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            width=150,
            command=self.destroy,
            **get_button_style("secondary")
        )
        cancel_btn.pack(side="left", padx=8)


    def save(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()


        if not name or not email:
            messagebox.showerror("Error", "Name and email are required.")
            return


        pw_to_set = password if password.strip() else None


        success, msg = update_user(
            self.user["user_id"],
            name=name,
            email=email,
            password=pw_to_set
        )


        if success:
            messagebox.showinfo("Success", "User updated successfully.")
            if self.on_saved:
                self.on_saved()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)




class AdminDashboard:
    def __init__(self, parent, on_logout=None):
        self.parent = parent
        self.on_logout = on_logout


        self.users = []
        self.selected_user = None


        self.build_ui()
        self.refresh_users()


    def build_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)




        # Top Bar
        top = ctk.CTkFrame(self.main_frame, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")


        left_top = ctk.CTkFrame(top, fg_color="transparent")
        left_top.pack(side="left", padx=20, pady=14)


        title = ctk.CTkLabel(
            left_top,
            text="👑 Admin Dashboard",
            **get_label_style("heading")
        )
        title.pack(anchor="w")


        subtitle = ctk.CTkLabel(
            left_top,
            text="Manage users, products, and orders",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL)
        )
        subtitle.pack(anchor="w", pady=(2, 0))


        right_top = ctk.CTkFrame(top, fg_color="transparent")
        right_top.pack(side="right", padx=20, pady=14)


        logout_btn = ctk.CTkButton(
            right_top,
            text="Logout",
            command=self.logout,
            width=120,
            **get_button_style("secondary")
        )
        logout_btn.pack(side="right")


        # Quick Actions
        quick = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        quick.pack(fill="x", padx=20, pady=(16, 10))


        quick.grid_columnconfigure(0, weight=1)
        quick.grid_columnconfigure(1, weight=1)
        quick.grid_columnconfigure(2, weight=1)


        self._nav_card(
            parent=quick,
            col=0,
            title="🧑‍💼 Manage Users",
            desc="Edit users, promote/demote, delete accounts",
            btn_text="You're here",
            btn_style="secondary",
            command=None,
            disabled=True
        )


        self._nav_card(
            parent=quick,
            col=1,
            title="🛍️ Manage Products",
            desc="CRUD products, update stock, delete listings",
            btn_text="Open",
            btn_style="primary",
            command=self.open_product_management
        )


        self._nav_card(
            parent=quick,
            col=2,
            title="📦 Manage Orders",
            desc="View all orders, filter by status, search",
            btn_text="Open",
            btn_style="primary",
            command=self.open_order_management
        )


        # Body split
        body = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)


        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)


        left = ctk.CTkFrame(body, **get_card_style())
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)


        header_row = ctk.CTkFrame(left, fg_color="transparent")
        header_row.pack(fill="x", padx=20, pady=(15, 8))


        left_title = ctk.CTkLabel(header_row, text="All Users", **get_label_style("heading"))
        left_title.pack(side="left")


        self.status_label = ctk.CTkLabel(header_row, text="", **get_label_style("small"))
        self.status_label.pack(side="right")


        search_row = ctk.CTkFrame(left, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=(0, 10))


        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Search users by name/email (optional)",
            **get_input_style()
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.refresh_users())


        search_btn = ctk.CTkButton(
            search_row,
            text="Search",
            command=self.refresh_users,
            width=110,
            **get_button_style("secondary")
        )
        search_btn.pack(side="left")


        self.user_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.user_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))


        right = ctk.CTkFrame(body, **get_card_style())
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=0)


        right_title = ctk.CTkLabel(right, text="Selected User", **get_label_style("heading"))
        right_title.pack(anchor="w", padx=20, pady=(15, 10))


        self.detail_label = ctk.CTkLabel(
            right,
            text="Select a user to see details.",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.NORMAL)
        )
        self.detail_label.pack(anchor="w", padx=20, pady=(0, 20))


        self.btn_edit = ctk.CTkButton(
            right,
            text="Edit User",
            command=self.edit_user,
            width=220,
            state="disabled",
            **get_button_style("primary")
        )
        self.btn_edit.pack(padx=20, pady=(0, 10))


        self.btn_toggle_role = ctk.CTkButton(
            right,
            text="Promote/Demote",
            command=self.toggle_role,
            width=220,
            state="disabled",
            **get_button_style("secondary")
        )
        self.btn_toggle_role.pack(padx=20, pady=(0, 10))


        self.btn_delete = ctk.CTkButton(
            right,
            text="Delete User",
            command=self.delete_selected_user,
            width=220,
            state="disabled",
            **get_button_style("danger")
        )
        self.btn_delete.pack(padx=20, pady=(0, 10))


        self.btn_refresh = ctk.CTkButton(
            right,
            text="Refresh",
            command=self.refresh_users,
            width=220,
            **get_button_style("secondary")
        )
        self.btn_refresh.pack(padx=20, pady=(10, 20))


    def _nav_card(self, parent, col, title, desc, btn_text, btn_style, command, disabled=False):
        card = ctk.CTkFrame(parent, **get_card_style())
        card.grid(row=0, column=col, sticky="nsew", padx=8)


        t = ctk.CTkLabel(card, text=title, **get_label_style("heading"))
        t.pack(anchor="w", padx=16, pady=(14, 6))


        d = ctk.CTkLabel(
            card,
            text=desc,
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
            wraplength=260,
            justify="left"
        )
        d.pack(anchor="w", padx=16, pady=(0, 12))


        btn = ctk.CTkButton(
            card,
            text=btn_text,
            command=command if not disabled else None,
            state="disabled" if disabled else "normal",
            **get_button_style(btn_style)
        )
        btn.pack(fill="x", padx=16, pady=(0, 14))




    def open_product_management(self):
        self.destroy()
        self.product_manager = AdminProductManagementScreen(
            parent=self.parent,
            on_back=self._back_to_users
        )


    def open_order_management(self):
        self.destroy()
        self.order_manager = AdminOrderDashboardScreen(
            parent=self.parent,
            on_back=self._back_to_users
        )
        self.order_manager.pack(fill="both", expand=True)


    def _back_to_users(self):
        if hasattr(self, "product_manager"):
            try:
                self.product_manager.destroy()
            except Exception:
                pass


        if hasattr(self, "order_manager"):
            try:
                self.order_manager.destroy()
            except Exception:
                pass


        AdminDashboard(self.parent, on_logout=self.on_logout)


    def refresh_users(self):
        q = ""
        if hasattr(self, "search_entry"):
            q = (self.search_entry.get() or "").strip().lower()


        self.users = get_all_users()


        if q:
            self.users = [
                u for u in self.users
                if q in (u.get("user_name", "").lower()) or q in (u.get("user_email", "").lower())
            ]


        self.selected_user = None
        self._render_user_list()
        self._set_selected_user(None)
        self.status_label.configure(text=f"Total users: {len(self.users)}")


    def _render_user_list(self):
        for w in self.user_list.winfo_children():
            w.destroy()


        if not self.users:
            empty = ctk.CTkLabel(self.user_list, text="No users found.", **get_label_style("small"))
            empty.pack(pady=15)
            return


        for user in self.users:
            row = ctk.CTkFrame(self.user_list, fg_color=Colors.BG_WHITE, corner_radius=12)
            row.pack(fill="x", padx=5, pady=6)


            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True, padx=12, pady=10)


            name = ctk.CTkLabel(left, text=user["user_name"], **get_label_style("normal"))
            name.pack(anchor="w")


            email = ctk.CTkLabel(
                left,
                text=user["user_email"],
                text_color=Colors.TEXT_SECONDARY,
                font=(Fonts.FAMILY, Fonts.SMALL)
            )
            email.pack(anchor="w", pady=(2, 0))


            badge = ctk.CTkLabel(
                row,
                text=user["user_role"].upper(),
                text_color=Colors.TEXT_WHITE,
                fg_color=Colors.PRIMARY if user["user_role"] == "admin" else Colors.INFO,
                corner_radius=8,
                padx=10,
                pady=3,
                font=(Fonts.FAMILY, Fonts.SMALL, "bold")
            )
            badge.pack(side="right", padx=12)


            row.bind("<Button-1>", lambda e, u=user: self._set_selected_user(u))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, u=user: self._set_selected_user(u))


    def _set_selected_user(self, user):
        self.selected_user = user


        if not user:
            self.detail_label.configure(text="Select a user to see details.")
            self.btn_edit.configure(state="disabled")
            self.btn_toggle_role.configure(state="disabled")
            self.btn_delete.configure(state="disabled")
            return


        self.detail_label.configure(
            text=(
                f"Name: {user['user_name']}\n"
                f"Email: {user['user_email']}\n"
                f"Role: {user['user_role']}\n"
                f"Created: {user['created_at']}"
            )
        )


        is_default_admin = (user["user_email"].lower() == "admin@ora.com")
        self.btn_edit.configure(state="normal")
        self.btn_toggle_role.configure(state="normal")
        self.btn_delete.configure(state="disabled" if is_default_admin else "normal")


    def edit_user(self):
        if not self.selected_user:
            return


        def _after_save():
            self.refresh_users()


        EditUserDialog(self.parent, self.selected_user, on_saved=_after_save)


    def toggle_role(self):
        if not self.selected_user:
            return


        current = self.selected_user["user_role"]
        new_role = "user" if current == "admin" else "admin"


        if self.selected_user["user_email"].lower() == "admin@ora.com" and new_role == "user":
            messagebox.showwarning("Not allowed", "You cannot demote the default admin account.")
            return


        ok = messagebox.askyesno("Confirm", f"Change role to '{new_role}'?")
        if not ok:
            return


        success, msg = change_user_role(self.selected_user["user_id"], new_role)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_users()
        else:
            messagebox.showerror("Error", msg)


    def delete_selected_user(self):
        if not self.selected_user:
            return


        if self.selected_user["user_email"].lower() == "admin@ora.com":
            messagebox.showwarning("Not allowed", "You cannot delete the default admin account.")
            return


        ok = messagebox.askyesno(
            "Confirm delete",
            f"Delete user:\n\n{self.selected_user['user_name']} ({self.selected_user['user_email']})?"
        )
        if not ok:
            return


        success, msg = delete_user(self.selected_user["user_id"])
        if success:
            messagebox.showinfo("Deleted", msg)
            self.refresh_users()
        else:
            messagebox.showerror("Error", msg)


    def logout(self):
        SessionManager.clear_session()
        if self.on_logout:
            self.parent.after(0, self.on_logout)


    def destroy(self):
        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            self.main_frame.destroy()





