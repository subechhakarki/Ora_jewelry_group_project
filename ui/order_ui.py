import customtkinter as ctk
from tkinter import messagebox


from db.order_queries import get_orders_by_user,get_all_orders, order_stats, update_order_status
from themes.theme import (
    Colors, Fonts,
    get_button_style, get_card_style, get_label_style, get_input_style
)


try:
    from utils.helpers import format_price
except Exception:
    def format_price(x):
        try:
            return f"Rs {float(x):.2f}"
        except Exception:
            return f"Rs {x}"




class UserOrderHistoryScreen(ctk.CTkFrame):


    def __init__(self, parent, user_id: int, on_back=None, show_back: bool = True):
        super().__init__(parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.parent = parent
        self.user_id = user_id
        self.on_back = on_back
        self.show_back = show_back

        self._build_ui()
        self.refresh()



    def _build_ui(self):


        top = ctk.CTkFrame(self, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")


        title = ctk.CTkLabel(top, text="📦 My Orders", **get_label_style("heading"))
        title.pack(side="left", padx=20, pady=14)


        if self.show_back:
            back = ctk.CTkButton(
                top, text="← Back", command=self._go_back, width=110, **get_button_style("secondary")
            )
            back.pack(side="right", padx=20, pady=14)



        self.status = ctk.CTkLabel(
            self,
            text="",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        self.status.pack(anchor="w", padx=20, pady=(12, 6))


        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))


    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()


        orders = get_orders_by_user(self.user_id)
        self.status.configure(text=f"Total orders: {len(orders)}")


        if not orders:
            empty = ctk.CTkLabel(self.list_frame, text="No orders yet.", **get_label_style("small"))
            empty.pack(pady=20)
            return


        for order in orders:
            self._order_card(order)


    def _order_card(self, o: dict):
        card = ctk.CTkFrame(self.list_frame, **get_card_style())
        card.pack(fill="x", padx=8, pady=8)


        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(12, 6))


        name = ctk.CTkLabel(top, text=o.get("product_name", "Unknown Product"), **get_label_style("normal"))
        name.pack(side="left")


        status = o.get("order_status", "on-going")
        status_badge = ctk.CTkLabel(
            top,
            text=status,
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        status_badge.pack(side="right")


        qty = int(o.get("sale_quantity", 0))
        total = format_price(o.get("total_price", 0))
        price = format_price(o.get("product_price", 0))
        date = o.get("order_date", "")


        info = ctk.CTkLabel(
            card,
            text=f"Qty: {qty}   •   Unit: {price}   •   Total: {total}\nDate: {date}",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
            justify="left",
        )
        info.pack(anchor="w", padx=14, pady=(0, 10))


        desc = (o.get("product_description") or "").strip()
        if len(desc) > 110:
            desc = desc[:110] + "..."


        if desc:
            desc_lbl = ctk.CTkLabel(
                card,
                text=desc,
                text_color=Colors.TEXT_SECONDARY,
                font=(Fonts.FAMILY, Fonts.SMALL),
                wraplength=560,
                justify="left",
            )
            desc_lbl.pack(anchor="w", padx=14, pady=(0, 12))


    def _go_back(self):
        if self.on_back:
            self.on_back()








class AdminOrderDashboardScreen(ctk.CTkFrame):


    def __init__(self, parent, on_back=None):
        super().__init__(parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.parent = parent
        self.on_back = on_back


        self.status_var = ctk.StringVar(value="all")
        self.search_var = ctk.StringVar(value="")


        self._build_ui()
        self.refresh()


    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")


        title = ctk.CTkLabel(top, text="📋 Admin — Orders Dashboard", **get_label_style("heading"))
        title.pack(side="left", padx=20, pady=14)


        back = ctk.CTkButton(
            top, text="← Back", command=self._go_back, width=110, **get_button_style("secondary")
        )
        back.pack(side="right", padx=20, pady=14)


        filters = ctk.CTkFrame(self, fg_color="transparent")
        filters.pack(fill="x", padx=20, pady=(14, 8))


        status_lbl = ctk.CTkLabel(filters, text="Status:", **get_label_style("small"))
        status_lbl.pack(side="left", padx=(0, 8))


        self.status_menu = ctk.CTkOptionMenu(
            filters,
            variable=self.status_var,
            values=["all", "on-going", "delivering", "finished", "cancelled"],
            command=lambda _: self.refresh(),
        )
        self.status_menu.pack(side="left", padx=(0, 12))


        self.search_entry = ctk.CTkEntry(
            filters,
            textvariable=self.search_var,
            placeholder_text="Search by user, product, or order id...",
            **get_input_style(),
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.refresh())


        search_btn = ctk.CTkButton(filters, text="Search", command=self.refresh, **get_button_style("secondary"))
        search_btn.pack(side="left", padx=(0, 10))


        clear_btn = ctk.CTkButton(filters, text="Clear", command=self._clear_filters, **get_button_style("secondary"))
        clear_btn.pack(side="left")


        self.stats_label = ctk.CTkLabel(
            self,
            text="",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        self.stats_label.pack(anchor="w", padx=20, pady=(0, 8))


        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))


    def _clear_filters(self):
        self.status_var.set("all")
        self.search_var.set("")
        self.refresh()


    def refresh(self):


        for w in self.list_frame.winfo_children():
            w.destroy()


        stats = order_stats()
        self.stats_label.configure(
            text=(
                f"Total: {stats['total']}  •  "
                f"On-going: {stats['on-going']}  •  "
                f"Delivering: {stats['delivering']}  •  "
                f"Finished: {stats['finished']}  •  "
                f"Cancelled: {stats['cancelled']}"
            )
        )


        status = self.status_var.get()
        q = self.search_var.get()


        orders = get_all_orders(status=status, search_text=q)


        if not orders:
            empty = ctk.CTkLabel(self.list_frame, text="No orders found.", **get_label_style("small"))
            empty.pack(pady=20)
            return


        for o in orders:
            self._order_card(o)


    def _order_card(self, o: dict):
        card = ctk.CTkFrame(self.list_frame, **get_card_style())
        card.pack(fill="x", padx=8, pady=8)


        sale_id = int(o.get("sale_id", 0))
        current_status = o.get("order_status", "on-going")


        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 6))


        left = ctk.CTkLabel(
            header,
            text=f"Order #{sale_id}  •  {o.get('product_name', 'Unknown')}",
            **get_label_style("normal"),
        )
        left.pack(side="left")


        status_lbl = ctk.CTkLabel(
            header,
            text=current_status,
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        status_lbl.pack(side="right")


        user_name = o.get("user_name", "Unknown User")
        user_email = o.get("user_email", "")
        qty = int(o.get("sale_quantity", 0))
        total = format_price(o.get("total_price", 0))
        date = o.get("order_date", "")


        info = ctk.CTkLabel(
            card,
            text=(
                f"Customer: {user_name} ({user_email})\n"
                f"Qty: {qty}   •   Total: {total}\n"
                f"Date: {date}"
            ),
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
            justify="left",
        )
        info.pack(anchor="w", padx=14, pady=(0, 10))


        action = ctk.CTkFrame(card, fg_color="transparent")
        action.pack(fill="x", padx=14, pady=(0, 12))
        action.grid_columnconfigure(0, weight=1)
        action.grid_columnconfigure(1, weight=0)
        action.grid_columnconfigure(2, weight=0)


        next_map = {
            "on-going": ["delivering", "cancelled"],
            "delivering": ["finished", "cancelled"],
            "finished": [],
            "cancelled": [],
        }
        choices = next_map.get(current_status, [])
        status_var = ctk.StringVar(value=choices[0] if choices else current_status)


        if not choices:
            terminal = ctk.CTkLabel(
                action,
                text="Status locked (finished/cancelled)",
                text_color=Colors.TEXT_SECONDARY,
                font=(Fonts.FAMILY, Fonts.SMALL),
            )
            terminal.grid(row=0, column=0, sticky="w")
            return


        status_menu = ctk.CTkOptionMenu(
            action,
            variable=status_var,
            values=choices,
        )
        status_menu.grid(row=0, column=1, sticky="e", padx=(8, 8))


        def _apply():
            new_status = status_var.get()
            ok = messagebox.askyesno("Confirm", f"Update Order #{sale_id} to '{new_status}'?")
            if not ok:
                return


            if new_status == "cancelled":
                from db.order_queries import cancel_order
                from db.product_queries import restock_product


                success, msg, info = cancel_order(sale_id)
                if success:
                    pid = int(info["product_id"])
                    q = int(info["sale_quantity"])
                    ok2, msg2 = restock_product(pid, q)
                    if not ok2:
                        messagebox.showwarning("Cancelled, but restock failed", msg2)
                    messagebox.showinfo("Updated", msg)
                    self.refresh()
                else:
                    messagebox.showerror("Error", msg)
                return


            success, msg = update_order_status(sale_id, new_status)
            if success:
                messagebox.showinfo("Updated", msg)
                self.refresh()
            else:
                messagebox.showerror("Error", msg)


        update_btn = ctk.CTkButton(
            action, text="Update", command=_apply, **get_button_style("primary"), width=80
        )
        update_btn.grid(row=0, column=2, sticky="e", padx=(8, 0))




    def _go_back(self):
        if self.on_back:
            self.on_back()
           
           



