# ui/product_ui.py
"""
ADMIN PRODUCT MANAGEMENT UI (Full CRUD)
Uses db/product_queries.py you have:
- create_product
- get_all_products
- get_product_by_id
- update_product
- update_stock
- adjust_stock
- delete_product
- search_products

This UI provides:
✅ Product list (scroll)
✅ Search
✅ Add product
✅ Edit product (name/price/qty/image/description)
✅ Update stock only
✅ Delete product
✅ Image picker + copy into assets/images
"""

import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog

import os
import shutil
from datetime import datetime

from themes.theme import (
    Colors, Layout, Fonts,
    get_button_style, get_card_style, get_label_style, get_input_style
)
from utils.helpers import validate_image_file, format_price, truncate_text

from db.product_queries import (
    create_product,
    get_all_products,
    update_product,
    update_stock,
    delete_product,
    search_products
)


# -------------------------
# Image helpers
# -------------------------
def _project_root():
    return os.path.dirname(os.path.dirname(__file__))  # project root


def _ensure_images_dir():
    images_dir = os.path.join(_project_root(), "assets", "images")
    os.makedirs(images_dir, exist_ok=True)
    return images_dir


def _copy_image_to_assets(src_path):
    images_dir = _ensure_images_dir()
    ext = os.path.splitext(src_path)[1].lower()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = f"product_{stamp}{ext}"
    dest_path = os.path.join(images_dir, safe_name)
    shutil.copy2(src_path, dest_path)

    # Store relative path in DB
    return os.path.join("assets", "images", safe_name)


# -------------------------
# Dialogs
# -------------------------
class ProductFormDialog(ctk.CTkToplevel):
    """
    Add/Edit Product dialog.
    If product is None => Add mode
    else => Edit mode
    """
    def __init__(self, parent, product=None, on_saved=None):
        super().__init__(parent)
        self.product = product
        self.on_saved = on_saved

        self.selected_image_src = None
        self.image_path_db = None

        self.title("Add Product" if product is None else "Edit Product")
        self.geometry("600x650")
        self.minsize(520, 520)
        self.resizable(True, True)

        self.transient(parent)
        self.grab_set()

        # ✅ Scrollable container so buttons never go missing
        outer = ctk.CTkFrame(self, **get_card_style())
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        self.scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=8, pady=8)

        header = ctk.CTkLabel(
            self.scroll,
            text="Add New Product" if product is None else "Edit Product",
            **get_label_style("heading"),
        )
        header.pack(pady=(10, 10))

        # ---- Name
        ctk.CTkLabel(self.scroll, text="Product Name", **get_label_style("normal")).pack(anchor="w", padx=10)
        self.name_entry = ctk.CTkEntry(self.scroll, width=520, **get_input_style())
        self.name_entry.pack(padx=10, pady=(6, 12))

        # ---- Price
        ctk.CTkLabel(self.scroll, text="Price", **get_label_style("normal")).pack(anchor="w", padx=10)
        self.price_entry = ctk.CTkEntry(self.scroll, width=520, **get_input_style())
        self.price_entry.pack(padx=10, pady=(6, 12))

        # ---- Quantity
        ctk.CTkLabel(self.scroll, text="Quantity / Stock", **get_label_style("normal")).pack(anchor="w", padx=10)
        self.qty_entry = ctk.CTkEntry(self.scroll, width=520, **get_input_style())
        self.qty_entry.pack(padx=10, pady=(6, 12))

        # ---- Image picker
        img_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        img_row.pack(fill="x", padx=10, pady=(0, 12))

        self.image_label = ctk.CTkLabel(img_row, text="No image selected", **get_label_style("small"))
        self.image_label.pack(side="left")

        choose_btn = ctk.CTkButton(
            img_row,
            text="Choose Image",
            command=self.pick_image,
            width=150,
            **get_button_style("secondary"),
        )
        choose_btn.pack(side="right")

        # ---- Description
        ctk.CTkLabel(self.scroll, text="Description (optional)", **get_label_style("normal")).pack(anchor="w", padx=10)
        self.desc_box = ctk.CTkTextbox(
            self.scroll, width=520, height=180,
            fg_color=Colors.BG_WHITE, text_color=Colors.TEXT_PRIMARY
        )
        self.desc_box.pack(padx=10, pady=(6, 12))

        # ---- Error label
        self.error_label = ctk.CTkLabel(self.scroll, text="", text_color=Colors.ERROR, font=(Fonts.FAMILY, Fonts.SMALL))
        self.error_label.pack(pady=(0, 8))

        # ✅ Buttons (this is the “Add/Create” area)
        btn_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row.pack(pady=(8, 12))

        save_btn = ctk.CTkButton(
            btn_row,
            text="Create Product" if product is None else "Save Changes",
            command=self.save,
            width=180,
            **get_button_style("primary"),
        )
        save_btn.pack(side="left", padx=8)

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            command=self.destroy,
            width=180,
            **get_button_style("secondary"),
        )
        cancel_btn.pack(side="left", padx=8)

        # Prefill for edit mode
        if product is not None:
            self.name_entry.insert(0, product.get("product_name", ""))
            self.price_entry.insert(0, str(product.get("product_price", "")))
            self.qty_entry.insert(0, str(product.get("product_quantity", "")))
            self.desc_box.insert("1.0", product.get("product_description", "") or "")
            self.image_path_db = product.get("product_image")
            if self.image_path_db:
                self.image_label.configure(text=os.path.basename(self.image_path_db))

    def pick_image(self):
        self.error_label.configure(text="")

        path = filedialog.askopenfilename(
            title="Select Product Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if not path:
            return

        valid, err = validate_image_file(path)
        if not valid:
            self.error_label.configure(text=f"⚠️ {err}")
            return

        self.selected_image_src = path
        self.image_label.configure(text=os.path.basename(path))

    def save(self):
        self.error_label.configure(text="")

        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        qty = self.qty_entry.get().strip()
        desc = self.desc_box.get("1.0", "end").strip()

        image_path_to_save = self.image_path_db  # default keep existing for edit
        if self.selected_image_src:
            try:
                image_path_to_save = _copy_image_to_assets(self.selected_image_src)
            except Exception as e:
                self.error_label.configure(text=f"⚠️ Image save failed: {e}")
                return

        if self.product is None:
            success, msg, pid = create_product(
                name=name,
                price=price,
                quantity=qty,
                image_path=image_path_to_save,
                description=desc if desc else None
            )
            if success:
                messagebox.showinfo("Success", f"Product created!\nID: {pid}")
                if self.on_saved:
                    self.on_saved()
                self.destroy()
            else:
                self.error_label.configure(text=f"⚠️ {msg}")
        else:
            success, msg = update_product(
                self.product["product_id"],
                name=name,
                price=price,
                quantity=qty,
                image_path=image_path_to_save,          # can be None to clear if you want
                description=desc if desc else None
            )
            if success:
                messagebox.showinfo("Success", "Product updated successfully.")
                if self.on_saved:
                    self.on_saved()
                self.destroy()
            else:
                self.error_label.configure(text=f"⚠️ {msg}")


class StockDialog(ctk.CTkToplevel):
    """
    Update stock only (set exact quantity).
    """
    def __init__(self, parent, product, on_saved=None):
        super().__init__(parent)
        self.product = product
        self.on_saved = on_saved

        self.title("Update Stock")
        self.geometry("420x260")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        container = ctk.CTkFrame(self, **get_card_style())
        container.pack(fill="both", expand=True, padx=18, pady=18)

        header = ctk.CTkLabel(container, text="Update Stock", **get_label_style("heading"))
        header.pack(pady=(10, 8))

        info = ctk.CTkLabel(
            container,
            text=f"{self.product['product_name']}\nCurrent: {self.product['product_quantity']}",
            **get_label_style("normal")
        )
        info.pack(pady=(0, 10))

        ctk.CTkLabel(container, text="New Quantity", **get_label_style("normal")).pack(anchor="w", padx=18)
        self.qty_entry = ctk.CTkEntry(container, width=360, **get_input_style())
        self.qty_entry.pack(padx=18, pady=(6, 10))
        self.qty_entry.insert(0, str(self.product["product_quantity"]))

        self.error_label = ctk.CTkLabel(container, text="", text_color=Colors.ERROR, font=(Fonts.FAMILY, Fonts.SMALL))
        self.error_label.pack(pady=(0, 8))

        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(pady=(4, 0))

        save_btn = ctk.CTkButton(btn_row, text="Save", width=140, command=self.save, **get_button_style("primary"))
        save_btn.pack(side="left", padx=8)

        cancel_btn = ctk.CTkButton(btn_row, text="Cancel", width=140, command=self.destroy, **get_button_style("secondary"))
        cancel_btn.pack(side="left", padx=8)

    def save(self):
        new_qty = self.qty_entry.get().strip()
        success, msg = update_stock(self.product["product_id"], new_qty)
        if success:
            messagebox.showinfo("Success", msg)
            if self.on_saved:
                self.on_saved()
            self.destroy()
        else:
            self.error_label.configure(text=f"⚠️ {msg}")


# -------------------------
# Main Admin Product Screen
# -------------------------
class AdminProductManagementScreen:
    """
    Full Admin Product CRUD screen.
    """
    def __init__(self, parent, on_back=None):
        self.parent = parent
        self.on_back = on_back

        self.products = []
        self.selected_product = None

        self.build_ui()
        self.refresh_products()

    def build_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # Top bar
        top = ctk.CTkFrame(self.main_frame, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")

        title = ctk.CTkLabel(top, text="🛍️ Admin — Product Management", **get_label_style("heading"))
        title.pack(side="left", padx=20, pady=15)

        back_btn = ctk.CTkButton(
            top,
            text="← Back",
            command=self.go_back,
            width=110,
            **get_button_style("secondary")
        )
        back_btn.pack(side="right", padx=(0, 12), pady=15)

        add_btn = ctk.CTkButton(
            top,
            text="➕ Add Product",
            command=self.open_add_dialog,
            width=150,
            **get_button_style("primary")
        )
        add_btn.pack(side="right", padx=(0, 12), pady=15)

        # Body
        body = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Left: list
        left = ctk.CTkFrame(body, **get_card_style())
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Search row
        search_row = ctk.CTkFrame(left, fg_color="transparent")
        search_row.pack(fill="x", padx=18, pady=(15, 10))

        self.search_entry = ctk.CTkEntry(search_row, width=360, placeholder_text="Search by name or description...", **get_input_style())
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search())

        search_btn = ctk.CTkButton(search_row, text="Search", width=110, command=self.search, **get_button_style("secondary"))
        search_btn.pack(side="left")

        clear_btn = ctk.CTkButton(search_row, text="Clear", width=90, command=self.refresh_products, **get_button_style("secondary"))
        clear_btn.pack(side="left", padx=(10, 0))

        self.status_label = ctk.CTkLabel(left, text="", **get_label_style("small"))
        self.status_label.pack(anchor="w", padx=18, pady=(0, 10))

        self.list_frame = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Right: details + actions
        right = ctk.CTkFrame(body, **get_card_style())
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        right_title = ctk.CTkLabel(right, text="Selected Product", **get_label_style("heading"))
        right_title.pack(anchor="w", padx=18, pady=(15, 10))

        self.detail_label = ctk.CTkLabel(
            right,
            text="Select a product to see details.",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.NORMAL)
        )
        self.detail_label.pack(anchor="w", padx=18, pady=(0, 18))

        self.btn_edit = ctk.CTkButton(
            right, text="Edit Product", command=self.open_edit_dialog,
            width=220, state="disabled", **get_button_style("primary")
        )
        self.btn_edit.pack(padx=18, pady=(0, 10))

        self.btn_stock = ctk.CTkButton(
            right, text="Update Stock", command=self.open_stock_dialog,
            width=220, state="disabled", **get_button_style("secondary")
        )
        self.btn_stock.pack(padx=18, pady=(0, 10))

        self.btn_delete = ctk.CTkButton(
            right, text="Delete Product", command=self.delete_selected,
            width=220, state="disabled", **get_button_style("danger")
        )
        self.btn_delete.pack(padx=18, pady=(0, 10))

        self.btn_refresh = ctk.CTkButton(
            right, text="Refresh", command=self.refresh_products,
            width=220, **get_button_style("secondary")
        )
        self.btn_refresh.pack(padx=18, pady=(10, 18))

    # -------------
    # Data loading
    # -------------
    def refresh_products(self):
        self.search_entry.delete(0, "end")
        self.products = get_all_products()
        self.selected_product = None
        self._render_list()
        self._set_selected(None)
        self.status_label.configure(text=f"Total products: {len(self.products)}")

    def search(self):
        q = self.search_entry.get().strip()
        self.products = search_products(q)
        self.selected_product = None
        self._render_list()
        self._set_selected(None)
        self.status_label.configure(text=f"Results: {len(self.products)}")

    def _render_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.products:
            empty = ctk.CTkLabel(self.list_frame, text="No products found.", **get_label_style("small"))
            empty.pack(pady=15)
            return

        for p in self.products:
            row = ctk.CTkFrame(self.list_frame, fg_color=Colors.BG_WHITE, corner_radius=10)
            row.pack(fill="x", padx=6, pady=6)

            name = ctk.CTkLabel(row, text=p["product_name"], **get_label_style("normal"))
            name.pack(side="left", padx=12, pady=10)

            meta = ctk.CTkLabel(
                row,
                text=f"{format_price(p['product_price'])} | Stock: {p['product_quantity']}",
                text_color=Colors.TEXT_SECONDARY,
                font=(Fonts.FAMILY, Fonts.SMALL)
            )
            meta.pack(side="right", padx=12)

            row.bind("<Button-1>", lambda e, prod=p: self._set_selected(prod))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, prod=p: self._set_selected(prod))

    def _set_selected(self, product):
        self.selected_product = product

        if not product:
            self.detail_label.configure(text="Select a product to see details.")
            self.btn_edit.configure(state="disabled")
            self.btn_stock.configure(state="disabled")
            self.btn_delete.configure(state="disabled")
            return

        desc = product.get("product_description") or ""
        img = product.get("product_image") or "None"

        self.detail_label.configure(
            text=(
                f"Name: {product['product_name']}\n"
                f"Price: {format_price(product['product_price'])}\n"
                f"Stock: {product['product_quantity']}\n"
                f"Image: {img}\n\n"
                f"Description:\n{truncate_text(desc, 220)}"
            )
        )

        self.btn_edit.configure(state="normal")
        self.btn_stock.configure(state="normal")
        self.btn_delete.configure(state="normal")

    # -------------
    # Actions
    # -------------
    def open_add_dialog(self):
        def after_save():
            self.refresh_products()

        ProductFormDialog(self.parent, product=None, on_saved=after_save)

    def open_edit_dialog(self):
        if not self.selected_product:
            return

        def after_save():
            self.refresh_products()

        ProductFormDialog(self.parent, product=self.selected_product, on_saved=after_save)

    def open_stock_dialog(self):
        if not self.selected_product:
            return

        def after_save():
            self.refresh_products()

        StockDialog(self.parent, product=self.selected_product, on_saved=after_save)

    def delete_selected(self):
        if not self.selected_product:
            return

        ok = messagebox.askyesno(
            "Confirm delete",
            f"Delete product:\n\n{self.selected_product['product_name']}?"
        )
        if not ok:
            return

        success, msg = delete_product(self.selected_product["product_id"])
        if success:
            messagebox.showinfo("Deleted", msg)
            self.refresh_products()
        else:
            messagebox.showerror("Error", msg)

    # -------------
    # Navigation
    # -------------
    def go_back(self):
        if self.on_back:
            self.parent.after(0, self.on_back)

    def destroy(self):
        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            self.main_frame.destroy()



class UserProductBrowseScreen:
    """
    Step 8: Product browsing interface (for ALL users + admins)
    Card-based layout with grid view + search.
    """

    def __init__(self, parent, on_back=None, user_data=None):
        self.parent = parent
        self.on_back = on_back
        self.user_data = user_data

        self.products = []
        self.build_ui()
        self.load_products()

    def build_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # Top bar (soft + aesthetic)
        top = ctk.CTkFrame(self.main_frame, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")

        title_text = "💎 ORA Jewelry — Browse"
        if self.user_data and self.user_data.get("user_role") == "admin":
            title_text = "💎 ORA Jewelry — Browse (Admin View)"

        title = ctk.CTkLabel(top, text=title_text, **get_label_style("heading"))
        title.pack(side="left", padx=20, pady=14)

        back_btn = ctk.CTkButton(
            top,
            text="← Back",
            command=self.go_back,
            width=110,
            **get_button_style("secondary")
        )
        back_btn.pack(side="right", padx=20, pady=14)

        # Search row
        search_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=(15, 5))

        self.search_entry = ctk.CTkEntry(
            search_row,
            width=360,
            placeholder_text="Search rings, necklaces, diamonds...",
            **get_input_style()
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search())

        search_btn = ctk.CTkButton(
            search_row,
            text="Search",
            command=self.search,
            width=120,
            corner_radius=999,  # ✅ pill
            **get_button_style("primary")
        )
        search_btn.pack(side="left", padx=(0, 10))

        clear_btn = ctk.CTkButton(
            search_row,
            text="Clear",
            command=self.load_products,
            width=90,
            corner_radius=999,  # ✅ pill
            **get_button_style("secondary")
        )
        clear_btn.pack(side="left")

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL)
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 8))

        # Scrollable grid container
        self.grid_scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.grid_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Configure grid columns (3 columns for desktop)
        for col in range(3):
            self.grid_scroll.grid_columnconfigure(col, weight=1)

    # -------------------------
    # Data
    # -------------------------
    def load_products(self):
        from db.product_queries import get_all_products
        self.products = get_all_products()
        self.render_products()
        self.status_label.configure(text=f"Showing {len(self.products)} products")

    def search(self):
        from db.product_queries import search_products
        q = self.search_entry.get().strip()
        self.products = search_products(q)
        self.render_products()
        self.status_label.configure(text=f"Found {len(self.products)} results")

    # -------------------------
    # UI Render
    # -------------------------
    def render_products(self):
        # clear old cards
        for w in self.grid_scroll.winfo_children():
            w.destroy()

        if not self.products:
            empty = ctk.CTkLabel(self.grid_scroll, text="No products found 💔", **get_label_style("small"))
            empty.grid(row=0, column=0, padx=20, pady=20, sticky="w")
            return

        row = 0
        col = 0

        for product in self.products:
            card = self._build_product_card(self.grid_scroll, product)
            card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")

            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _build_product_card(self, parent, product):
        """
        Aesthetic card for one product
        """
        card = ctk.CTkFrame(parent, fg_color=Colors.BG_WHITE, corner_radius=18)
        card.grid_columnconfigure(0, weight=1)

        # "image placeholder" box (we'll show image later in Step 8.5)
        img_box = ctk.CTkFrame(card, fg_color="#F4F1FF", corner_radius=16, height=120)
        img_box.grid(row=0, column=0, padx=14, pady=(14, 10), sticky="ew")
        img_box.grid_propagate(False)

        img_text = "🖼️"
        if product.get("product_image"):
            img_text = "📷"
        img_label = ctk.CTkLabel(img_box, text=img_text, font=(Fonts.FAMILY, 40))
        img_label.place(relx=0.5, rely=0.5, anchor="center")

        # name
        name = ctk.CTkLabel(
            card,
            text=product["product_name"],
            font=(Fonts.FAMILY, 16, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        name.grid(row=1, column=0, padx=14, pady=(0, 4), sticky="w")

        # price + stock
        price_text = f"Rs {product['product_price']}"
        stock_text = f"Stock: {product['product_quantity']}"

        meta = ctk.CTkLabel(
            card,
            text=f"{price_text}   •   {stock_text}",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL)
        )
        meta.grid(row=2, column=0, padx=14, pady=(0, 10), sticky="w")

        # description snippet
        desc = product.get("product_description") or ""
        if len(desc) > 70:
            desc = desc[:70] + "..."

        desc_label = ctk.CTkLabel(
            card,
            text=desc if desc else "✨ Premium jewelry made with love",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, 12),
            wraplength=260,
            justify="left"
        )
        desc_label.grid(row=3, column=0, padx=14, pady=(0, 12), sticky="w")

        # Buttons row
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=4, column=0, padx=14, pady=(0, 14), sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        view_btn = ctk.CTkButton(
            btn_row,
            text="View",
            width=120,
            corner_radius=999,  # ✅ pill
            command=lambda: self.open_product_details(product),
            **get_button_style("secondary")
        )
        view_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        add_btn = ctk.CTkButton(
            btn_row,
            text="Add to Cart",
            width=120,
            corner_radius=999,  # ✅ pill
            command=lambda: self.add_to_cart_placeholder(product),
            **get_button_style("primary")
        )
        add_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        return card

    # -------------------------
    # Actions (Step 9 later)
    # -------------------------
    def open_product_details(self, product):
        messagebox.showinfo(
            "Product Details",
            f"{product['product_name']}\n\n"
            f"Price: Rs {product['product_price']}\n"
            f"Stock: {product['product_quantity']}\n\n"
            f"{product.get('product_description') or ''}"
        )

    def add_to_cart_placeholder(self, product):
        # Step 9 will connect cart table + cart_queries
        messagebox.showinfo("Cart", f"Added to cart (placeholder):\n{product['product_name']}")

    # -------------------------
    # Navigation
    # -------------------------
    def go_back(self):
        if self.on_back:
            self.parent.after(0, self.on_back)

    def destroy(self):
        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            self.main_frame.destroy()
