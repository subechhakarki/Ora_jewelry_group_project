# ui/admin_ui.py
import customtkinter as ctk
import tkinter.messagebox as messagebox

from themes.theme import (
    Colors, Layout, Fonts,
    get_button_style, get_card_style, get_label_style, get_input_style
)
from db.user_queries import get_all_users, delete_user, change_user_role, update_user
from utils.helpers import SessionManager

# ✅ CHANGE: import the FULL product management UI (CRUD)
from ui.product_ui import AdminProductManagementScreen


class EditUserDialog(ctk.CTkToplevel):
    """
    Small popup window to edit a user's name/email/password.
    """
    def __init__(self, parent, user, on_saved=None):
        super().__init__(parent)
        self.user = user
        self.on_saved = on_saved

        self.title("Edit User")
        self.geometry("420x420")
        self.resizable(False, False)

        # modal-ish
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

        # Password optional
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
    """
    Admin dashboard (Step 6 users + Step 7 products button)
    """
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

        # Top bar
        top = ctk.CTkFrame(self.main_frame, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")

        title = ctk.CTkLabel(
            top,
            text="👑 Admin Dashboard — User Management",
            **get_label_style("heading")
        )
        title.pack(side="left", padx=20, pady=15)

        products_btn = ctk.CTkButton(
            top,
            text="Manage Products",
            command=self.open_product_management,
            width=160,
            **get_button_style("primary")
        )
        products_btn.pack(side="right", padx=(0, 10), pady=15)

        logout_btn = ctk.CTkButton(
            top,
            text="Logout",
            command=self.logout,
            width=120,
            **get_button_style("secondary")
        )
        logout_btn.pack(side="right", padx=20, pady=15)

        # Body split
        body = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Left: user list
        left = ctk.CTkFrame(body, **get_card_style())
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)

        left_title = ctk.CTkLabel(left, text="All Users", **get_label_style("heading"))
        left_title.pack(anchor="w", padx=20, pady=(15, 5))

        self.status_label = ctk.CTkLabel(left, text="", **get_label_style("small"))
        self.status_label.pack(anchor="w", padx=20, pady=(0, 10))

        self.user_list = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.user_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Right: actions panel
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

    # -----------------------
    # ✅ PRODUCTS NAVIGATION (Full CRUD screen)
    # -----------------------
    def open_product_management(self):
        """
        Switch from User Management dashboard to Product Management dashboard
        """
        self.destroy()
        self.product_manager = AdminProductManagementScreen(
            parent=self.parent,
            on_back=self._back_to_users
        )

    def _back_to_users(self):
        """
        Back from product manager -> admin user dashboard
        """
        self.product_manager.destroy()
        AdminDashboard(self.parent, on_logout=self.on_logout)

    # -----------------------
    # Data + UI refresh
    # -----------------------
    def refresh_users(self):
        self.users = get_all_users()
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
            row = ctk.CTkFrame(self.user_list, fg_color=Colors.BG_WHITE, corner_radius=10)
            row.pack(fill="x", padx=5, pady=6)

            name = ctk.CTkLabel(row, text=user["user_name"], **get_label_style("normal"))
            name.pack(side="left", padx=12, pady=10)

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

    # -----------------------
    # Actions
    # -----------------------
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

    # -----------------------
    # Logout + cleanup
    # -----------------------
    def logout(self):
        SessionManager.clear_session()
        if self.on_logout:
            self.parent.after(0, self.on_logout)

    def destroy(self):
        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            self.main_frame.destroy()
