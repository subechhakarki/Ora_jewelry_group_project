import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

from db.cart_queries import (
    add_to_cart, get_cart_items, remove_from_cart,
    update_cart_quantity, cart_totals, clear_cart
)
from db.order_queries import create_orders_from_cart

from themes.theme import (
    Colors, Fonts,
    get_button_style, get_label_style, get_input_style
)

THUMB_SIZE = (56, 56)


def _project_root():
    return os.path.dirname(os.path.dirname(__file__))


def _resolve_image_path(db_path: str | None):
    if not db_path:
        return None
    if os.path.isabs(db_path):
        return db_path
    return os.path.join(_project_root(), db_path)


def _load_thumb(db_path: str | None):
    path = _resolve_image_path(db_path)
    if not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        return ctk.CTkImage(light_image=img, dark_image=img, size=THUMB_SIZE)
    except Exception:
        return None


class AddToCartDialog(ctk.CTkToplevel):
    def __init__(self, parent, user_id: int, product: dict, on_added=None):
        super().__init__(parent)
        self.user_id = user_id
        self.product = product
        self.on_added = on_added

        self.title("Add to Cart")
        self.geometry("420x280")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        frame = ctk.CTkFrame(self, fg_color=Colors.BG_LIGHT, corner_radius=14)
        frame.pack(fill="both", expand=True, padx=14, pady=14)

        name = self.product.get("product_name", "Product")
        stock = int(self.product.get("product_quantity", 0))
        price = self.product.get("product_price", 0)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(14, 8))

        thumb = _load_thumb(self.product.get("product_image"))
        thumb_box = ctk.CTkFrame(header, fg_color=Colors.BG_WHITE, corner_radius=12, width=62, height=62)
        thumb_box.pack(side="left")
        thumb_box.pack_propagate(False)

        if thumb:
            ctk.CTkLabel(thumb_box, text="", image=thumb).pack(expand=True)
        else:
            ctk.CTkLabel(thumb_box, text="No image", text_color=Colors.TEXT_SECONDARY,
                         font=(Fonts.FAMILY, Fonts.SMALL)).pack(expand=True)

        text_box = ctk.CTkFrame(header, fg_color="transparent")
        text_box.pack(side="left", padx=12, fill="x", expand=True)

        ctk.CTkLabel(text_box, text=name, **get_label_style("heading")).pack(anchor="w")
        ctk.CTkLabel(
            text_box,
            text=f"Price: Rs {price} • Stock: {stock}",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        ).pack(anchor="w", pady=(2, 0))

        qty_row = ctk.CTkFrame(frame, fg_color="transparent")
        qty_row.pack(fill="x", padx=14, pady=(10, 10))

        ctk.CTkLabel(qty_row, text="Quantity", **get_label_style("normal")).pack(side="left")
        self.qty_var = ctk.StringVar(value="1")
        self.qty_entry = ctk.CTkEntry(qty_row, width=90, textvariable=self.qty_var, **get_input_style())
        self.qty_entry.pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            frame,
            text="If item already exists, quantity increases.",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        ).pack(anchor="w", padx=14, pady=(0, 14))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 14))
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(btn_row, text="Cancel", command=self.destroy, **get_button_style("secondary")) \
            .grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(btn_row, text="Add", command=self._add, **get_button_style("primary")) \
            .grid(row=0, column=1, sticky="ew", padx=(8, 0))

    def _add(self):
        try:
            qty = int(self.qty_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid", "Quantity must be a number.")
            return

        product_id = int(self.product["product_id"])
        ok, msg = add_to_cart(self.user_id, product_id, qty)

        if ok:
            messagebox.showinfo("Cart", msg)
            if self.on_added:
                self.on_added()
            self.destroy()
        else:
            messagebox.showerror("Cart", msg)


class CartScreen(ctk.CTkFrame):
    def __init__(self, parent, user_id: int, on_back=None, show_back: bool = True):
        super().__init__(parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.parent = parent
        self.user_id = user_id
        self.on_back = on_back
        self.show_back = show_back
        

        self._thumb_cache = {}
        self._items = []

        self._build_ui()
        self.refresh()

    def _get_thumb(self, db_path: str | None):
        if not db_path:
            return None
        if db_path in self._thumb_cache:
            return self._thumb_cache[db_path]
        img = _load_thumb(db_path)
        self._thumb_cache[db_path] = img
        return img

    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")

        ctk.CTkLabel(top, text="Your Cart", **get_label_style("heading")).pack(side="left", padx=20, pady=14)

        if self.show_back:
            ctk.CTkButton(
                top, text="Back", command=self._go_back, width=110,
                **get_button_style("secondary")
            ).pack(side="right", padx=20, pady=14)


        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(12, 6))
        header.grid_columnconfigure(0, weight=3)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=1)
        header.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(header, text="Product", text_color=Colors.TEXT_SECONDARY, font=(Fonts.FAMILY, Fonts.SMALL)) \
            .grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Price", text_color=Colors.TEXT_SECONDARY, font=(Fonts.FAMILY, Fonts.SMALL)) \
            .grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(header, text="Qty", text_color=Colors.TEXT_SECONDARY, font=(Fonts.FAMILY, Fonts.SMALL)) \
            .grid(row=0, column=2, sticky="e")
        ctk.CTkLabel(header, text="Total", text_color=Colors.TEXT_SECONDARY, font=(Fonts.FAMILY, Fonts.SMALL)) \
            .grid(row=0, column=3, sticky="e")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        self.bottom = ctk.CTkFrame(self, fg_color=Colors.BG_WHITE, corner_radius=18)
        self.bottom.pack(fill="x", padx=20, pady=(0, 20))

        self.summary_label = ctk.CTkLabel(
            self.bottom,
            text="",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        self.summary_label.pack(side="left", padx=16, pady=14)

        self.checkout_btn = ctk.CTkButton(
            self.bottom,
            text="Checkout",
            command=self._checkout,
            width=160,
            **get_button_style("primary"),
        )
        self.checkout_btn.pack(side="right", padx=16, pady=14)

        self.clear_btn = ctk.CTkButton(
            self.bottom,
            text="Clear Cart",
            command=self._clear_cart,
            width=140,
            **get_button_style("secondary"),
        )
        self.clear_btn.pack(side="right", padx=(0, 10), pady=14)

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        self._items = get_cart_items(self.user_id)
        totals = cart_totals(self.user_id)

        self.summary_label.configure(
            text=f"Items: {totals['item_count']} • Unique: {totals['unique_items']} • Subtotal: Rs {totals['subtotal']:.2f}"
        )

        has_items = bool(self._items)
        self.checkout_btn.configure(state="normal" if has_items else "disabled")
        self.clear_btn.configure(state="normal" if has_items else "disabled")

        if not self._items:
            ctk.CTkLabel(self.list_frame, text="Cart is empty.", **get_label_style("small")).pack(pady=24)
            return

        for it in self._items:
            self._row(it)

    def _row(self, item: dict):
        row = ctk.CTkFrame(self.list_frame, fg_color=Colors.BG_WHITE, corner_radius=14)
        row.pack(fill="x", padx=6, pady=6)

        grid = ctk.CTkFrame(row, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=12)
        grid.grid_columnconfigure(0, weight=3)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=1)
        grid.grid_columnconfigure(3, weight=1)

        left = ctk.CTkFrame(grid, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        thumb_box = ctk.CTkFrame(left, fg_color=Colors.BG_LIGHT, corner_radius=12, width=62, height=62)
        thumb_box.pack(side="left")
        thumb_box.pack_propagate(False)

        thumb = self._get_thumb(item.get("product_image"))
        if thumb:
            ctk.CTkLabel(thumb_box, text="", image=thumb).pack(expand=True)
        else:
            ctk.CTkLabel(
                thumb_box,
                text="No image",
                text_color=Colors.TEXT_SECONDARY,
                font=(Fonts.FAMILY, Fonts.SMALL),
            ).pack(expand=True)

        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(side="left", padx=12)

        ctk.CTkLabel(info, text=item["product_name"], font=(Fonts.FAMILY, 14, "bold"),
                     text_color=Colors.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(
            info,
            text=f"Stock: {item['stock_quantity']}",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        ).pack(anchor="w", pady=(2, 0))

        unit_price = float(item["product_price"])
        qty = int(item["cart_quantity"])
        line_total = unit_price * qty

        ctk.CTkLabel(
            grid,
            text=f"Rs {unit_price:.2f}",
            text_color=Colors.TEXT_PRIMARY,
            font=(Fonts.FAMILY, Fonts.NORMAL),
        ).grid(row=0, column=1, sticky="e")

        qty_box = ctk.CTkFrame(grid, fg_color="transparent")
        qty_box.grid(row=0, column=2, sticky="e")

        qty_var = ctk.StringVar(value=str(qty))
        qty_entry = ctk.CTkEntry(qty_box, width=70, textvariable=qty_var, **get_input_style())
        qty_entry.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            qty_box,
            text="Update",
            width=90,
            command=lambda: self._set_qty(item["product_id"], qty_var.get()),
            **get_button_style("secondary"),
        ).pack(side="left")

        ctk.CTkLabel(
            grid,
            text=f"Rs {line_total:.2f}",
            text_color=Colors.TEXT_PRIMARY,
            font=(Fonts.FAMILY, Fonts.NORMAL, "bold"),
        ).grid(row=0, column=3, sticky="e")

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(fill="x", padx=14, pady=(0, 12))

        ctk.CTkButton(
            actions,
            text="Remove",
            command=lambda: self._remove(item["product_id"]),
            width=120,
            **get_button_style("danger"),
        ).pack(side="right")

    def _set_qty(self, product_id: int, qty_text: str):
        try:
            new_qty = int(str(qty_text).strip())
        except ValueError:
            messagebox.showerror("Invalid", "Quantity must be a number.")
            return

        ok, msg = update_cart_quantity(self.user_id, int(product_id), new_qty)
        if ok:
            self.refresh()
        else:
            messagebox.showerror("Cart", msg)

    def _checkout(self):
        confirm = messagebox.askyesno("Confirm Checkout", "Are you sure you want to place this order?")
        if not confirm:
            return

        ok, msg, created = create_orders_from_cart(self.user_id)
        if not ok:
            messagebox.showerror("Checkout Failed", msg)
            return

        ok2, msg2 = clear_cart(self.user_id)
        if not ok2:
            messagebox.showerror("Warning", f"Order created but cart not cleared:\n{msg2}")
        else:
            messagebox.showinfo("Order Placed", msg)

        self.refresh()

    def _clear_cart(self):
        confirm = messagebox.askyesno("Clear Cart", "Remove all items from your cart?")
        if not confirm:
            return
        ok, msg = clear_cart(self.user_id)
        if ok:
            self.refresh()
        else:
            messagebox.showerror("Cart", msg)

    def _remove(self, product_id: int):
        ok, msg = remove_from_cart(self.user_id, int(product_id))
        if ok:
            self.refresh()
        else:
            messagebox.showerror("Cart", msg)

    def _go_back(self):
        if self.on_back:
            self.on_back()
