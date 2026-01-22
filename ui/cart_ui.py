import customtkinter as ctk
from tkinter import messagebox


from db.cart_queries import add_to_cart, get_cart_items, remove_from_cart, update_cart_quantity, cart_totals, clear_cart
from db.order_queries import create_orders_from_cart




from themes.theme import (
    Colors, Layout, Fonts,
    get_button_style, get_card_style, get_label_style, get_input_style
)




class AddToCartDialog(ctk.CTkToplevel):


    def __init__(self, parent, user_id: int, product: dict, on_added=None):
        super().__init__(parent)
        self.user_id = user_id
        self.product = product
        self.on_added = on_added


        self.title("Add to Cart")
        self.geometry("380x260")
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


        title = ctk.CTkLabel(frame, text=f"🛒 {name}", **get_label_style("heading"))
        title.pack(anchor="w", padx=14, pady=(14, 6))


        meta = ctk.CTkLabel(
            frame,
            text=f"Price: Rs {price}   •   Stock: {stock}",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        meta.pack(anchor="w", padx=14, pady=(0, 12))


        qty_row = ctk.CTkFrame(frame, fg_color="transparent")
        qty_row.pack(fill="x", padx=14, pady=(0, 12))


        qty_lbl = ctk.CTkLabel(qty_row, text="Quantity:", **get_label_style("normal"))
        qty_lbl.pack(side="left")


        self.qty_var = ctk.StringVar(value="1")
        self.qty_entry = ctk.CTkEntry(qty_row, width=90, textvariable=self.qty_var, **get_input_style())
        self.qty_entry.pack(side="left", padx=(10, 0))


        hint = ctk.CTkLabel(
            frame,
            text="Tip: if item already exists in cart, quantity will increase.",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        hint.pack(anchor="w", padx=14, pady=(0, 14))


        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 14))
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)


        cancel = ctk.CTkButton(btn_row, text="Cancel", command=self.destroy, **get_button_style("secondary"))
        cancel.grid(row=0, column=0, sticky="ew", padx=(0, 8))


        add = ctk.CTkButton(btn_row, text="Add", command=self._add, **get_button_style("primary"))
        add.grid(row=0, column=1, sticky="ew", padx=(8, 0))


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


    def __init__(self, parent, user_id: int, on_back=None):
        super().__init__(parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.parent = parent
        self.user_id = user_id
        self.on_back = on_back


        self._build_ui()
        self.refresh()


    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")


        title = ctk.CTkLabel(top, text="🛒 Your Cart", **get_label_style("heading"))
        title.pack(side="left", padx=20, pady=14)


        back = ctk.CTkButton(top, text="← Back", command=self._go_back, width=110, **get_button_style("secondary"))
        back.pack(side="right", padx=20, pady=14)


        self.stats = ctk.CTkLabel(self, text="", text_color=Colors.TEXT_SECONDARY, font=(Fonts.FAMILY, Fonts.SMALL))
        self.stats.pack(anchor="w", padx=20, pady=(12, 6))


        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))


    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()


        items = get_cart_items(self.user_id)
        totals = cart_totals(self.user_id)


        self.stats.configure(
            text=f"Items: {totals['item_count']}  •  Unique: {totals['unique_items']}  •  Subtotal: Rs {totals['subtotal']:.2f}"
        )


        if not items:
            empty = ctk.CTkLabel(self.list_frame, text="Cart is empty.", **get_label_style("small"))
            empty.pack(pady=20)
            return


        for it in items:
            self._row(it)


    def _row(self, item: dict):
        row = ctk.CTkFrame(self.list_frame, fg_color=Colors.BG_WHITE, corner_radius=14)
        row.pack(fill="x", padx=8, pady=8)


        name = ctk.CTkLabel(row, text=item["product_name"], **get_label_style("normal"))
        name.pack(anchor="w", padx=14, pady=(12, 2))


        meta = ctk.CTkLabel(
            row,
            text=f"Price: Rs {item['product_price']}   •   Stock: {item['stock_quantity']}",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        meta.pack(anchor="w", padx=14, pady=(0, 10))


        qty_row = ctk.CTkFrame(row, fg_color="transparent")
        qty_row.pack(fill="x", padx=14, pady=(0, 10))


        qty_label = ctk.CTkLabel(
            qty_row,
            text="Quantity:",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        qty_label.pack(side="left")


        qty_var = ctk.StringVar(value=str(item["cart_quantity"]))
        qty_entry = ctk.CTkEntry(qty_row, width=90, textvariable=qty_var, **get_input_style())
        qty_entry.pack(side="left", padx=(10, 10))


        update_btn = ctk.CTkButton(
            qty_row,
            text="Update",
            command=lambda: self._set_qty(item["product_id"], qty_var.get()),
            width=110,
            **get_button_style("secondary"),
        )
        update_btn.pack(side="left")


        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.pack(fill="x", padx=14, pady=(0, 12))
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)


        rm = ctk.CTkButton(
            btns,
            text="Remove",
            command=lambda: self._remove(item["product_id"]),
            **get_button_style("danger"),
        )
        rm.grid(row=0, column=0, sticky="ew", padx=(0, 8))


        checkout = ctk.CTkButton(
            btns,
            text="Checkout",
            command=self._checkout,
            **get_button_style("primary"),
        )
        checkout.grid(row=0, column=1, sticky="ew", padx=(8, 0))
       
    def _set_qty(self, product_id: int, qty_text: str):
        from db.cart_queries import update_cart_quantity


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
        confirm = messagebox.askyesno(
            "Confirm Checkout",
            "Are you sure you want to place this order?"
        )
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


        print("Checked out")
        self.refresh()






    def _remove(self, product_id: int):
        ok, msg = remove_from_cart(self.user_id, int(product_id))
        if ok:
            self.refresh()
        else:
            messagebox.showerror("Cart", msg)


    def _inc(self, product_id: int, new_qty: int):
        ok, msg = update_cart_quantity(self.user_id, int(product_id), int(new_qty))
        if ok:
            self.refresh()
        else:
            messagebox.showerror("Cart", msg)


    def _go_back(self):
        if self.on_back:
            self.on_back()





