import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog

import os
import io
import shutil
import urllib.request
from datetime import datetime
from functools import lru_cache
from PIL import Image

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


def _project_root():
    return os.path.dirname(os.path.dirname(__file__))


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
    return os.path.join("assets", "images", safe_name)


class ProductFormDialog(ctk.CTkToplevel):
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

        ctk.CTkLabel(self.scroll, text="Product Name", **get_label_style("normal")).pack(anchor="w", padx=10)
        self.name_entry = ctk.CTkEntry(self.scroll, width=520, **get_input_style())
        self.name_entry.pack(padx=10, pady=(6, 12))

        ctk.CTkLabel(self.scroll, text="Price", **get_label_style("normal")).pack(anchor="w", padx=10)
        self.price_entry = ctk.CTkEntry(self.scroll, width=520, **get_input_style())
        self.price_entry.pack(padx=10, pady=(6, 12))

        ctk.CTkLabel(self.scroll, text="Quantity / Stock", **get_label_style("normal")).pack(anchor="w", padx=10)
        self.qty_entry = ctk.CTkEntry(self.scroll, width=520, **get_input_style())
        self.qty_entry.pack(padx=10, pady=(6, 12))

        img_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        img_row.pack(fill="x", padx=10, pady=(0, 12))

        self.image_label = ctk.CTkLabel(img_row, text="No image selected", **get_label_style("small"))
        self.image_label.pack(side="left")

        choose_btn = ctk.CTkButton(
            img_row,
            text="Choose Image",
            command=self.pick_image,
            **self._btn_style("secondary", width=150),
        )
        choose_btn.pack(side="right")

        ctk.CTkLabel(self.scroll, text="Description (optional)", **get_label_style("normal")).pack(anchor="w", padx=10)
        self.desc_box = ctk.CTkTextbox(
            self.scroll, width=520, height=180,
            fg_color=Colors.BG_WHITE, text_color=Colors.TEXT_PRIMARY
        )
        self.desc_box.pack(padx=10, pady=(6, 12))

        self.error_label = ctk.CTkLabel(
            self.scroll, text="", text_color=Colors.ERROR, font=(Fonts.FAMILY, Fonts.SMALL)
        )
        self.error_label.pack(pady=(0, 8))

        btn_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row.pack(pady=(8, 12))

        save_btn = ctk.CTkButton(
            btn_row,
            text="Create Product" if product is None else "Save Changes",
            command=self.save,
            **self._btn_style("primary", width=180),
        )
        save_btn.pack(side="left", padx=8)

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            command=self.destroy,
            **self._btn_style("secondary", width=180),
        )
        cancel_btn.pack(side="left", padx=8)

        if product is not None:
            self.name_entry.insert(0, product.get("product_name", ""))
            self.price_entry.insert(0, str(product.get("product_price", "")))
            self.qty_entry.insert(0, str(product.get("product_quantity", "")))
            self.desc_box.insert("1.0", product.get("product_description", "") or "")
            self.image_path_db = product.get("product_image")
            if self.image_path_db:
                self.image_label.configure(text=os.path.basename(self.image_path_db))

    @staticmethod
    def _btn_style(kind: str, **overrides):
        style = dict(get_button_style(kind))
        style.update(overrides)
        return style

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
            self.error_label.configure(text=str(err))
            return

        self.selected_image_src = path
        self.image_label.configure(text=os.path.basename(path))

    def save(self):
        self.error_label.configure(text="")

        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        qty = self.qty_entry.get().strip()
        desc = self.desc_box.get("1.0", "end").strip()

        image_path_to_save = self.image_path_db
        if self.selected_image_src:
            try:
                image_path_to_save = _copy_image_to_assets(self.selected_image_src)
            except Exception as e:
                self.error_label.configure(text=f"Image save failed: {e}")
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
                self.error_label.configure(text=str(msg))
        else:
            success, msg = update_product(
                self.product["product_id"],
                name=name,
                price=price,
                quantity=qty,
                image_path=image_path_to_save,
                description=desc if desc else None
            )
            if success:
                messagebox.showinfo("Success", "Product updated successfully.")
                if self.on_saved:
                    self.on_saved()
                self.destroy()
            else:
                self.error_label.configure(text=str(msg))


class StockDialog(ctk.CTkToplevel):
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

        save_btn = ctk.CTkButton(btn_row, text="Save", command=self.save, **self._btn_style("primary", width=140))
        save_btn.pack(side="left", padx=8)

        cancel_btn = ctk.CTkButton(btn_row, text="Cancel", command=self.destroy, **self._btn_style("secondary", width=140))
        cancel_btn.pack(side="left", padx=8)

    @staticmethod
    def _btn_style(kind: str, **overrides):
        style = dict(get_button_style(kind))
        style.update(overrides)
        return style

    def save(self):
        new_qty = self.qty_entry.get().strip()
        success, msg = update_stock(self.product["product_id"], new_qty)
        if success:
            messagebox.showinfo("Success", msg)
            if self.on_saved:
                self.on_saved()
            self.destroy()
        else:
            self.error_label.configure(text=str(msg))


class AdminProductManagementScreen:
    def __init__(self, parent, on_back=None):
        self.parent = parent
        self.on_back = on_back

        self.products = []
        self.selected_product = None

        self._thumb_refs = {}
        self._sidebar_img_ref = None

        self.build_ui()
        self.refresh_products()

    def build_ui(self):
        self.main_frame = ctk.CTkFrame(self.parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        top = ctk.CTkFrame(self.main_frame, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")

        title_left = ctk.CTkFrame(top, fg_color="transparent")
        title_left.pack(side="left", padx=18, pady=14)

        title = ctk.CTkLabel(title_left, text="Admin — Product Management", **get_label_style("heading"))
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_left,
            text="Search, preview, edit, stock update, and delete products.",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        actions_right = ctk.CTkFrame(top, fg_color="transparent")
        actions_right.pack(side="right", padx=12, pady=14)

        back_btn = ctk.CTkButton(actions_right,text="Back",command=self.go_back,
            **self._btn_style("secondary", width=110)
        )
        back_btn.pack(side="right", padx=(10, 0))


                
        add_btn = ctk.CTkButton(actions_right, text="Add Product", command=self.open_add_dialog, **self._btn_style("primary", width=160))
        add_btn.pack(side="right", padx=(10, 0))

        body = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=18)

        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, **get_card_style())
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        search_block = ctk.CTkFrame(left, fg_color="transparent")
        search_block.pack(fill="x", padx=16, pady=(16, 10))

        search_title = ctk.CTkLabel(search_block, text="Product List", **get_label_style("heading"))
        search_title.grid(row=0, column=0, sticky="w")

        self.status_label = ctk.CTkLabel(search_block, text="", **get_label_style("small"))
        self.status_label.grid(row=0, column=1, sticky="e")

        search_block.grid_columnconfigure(0, weight=1)
        search_block.grid_columnconfigure(1, weight=0)

        search_row = ctk.CTkFrame(left, fg_color="transparent")
        search_row.pack(fill="x", padx=16, pady=(0, 12))

        self.search_entry = ctk.CTkEntry(search_row, placeholder_text="Search by name or description...", **get_input_style())
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search())

        search_btn = ctk.CTkButton(search_row, text="Search", command=self.search, **self._btn_style("secondary", width=110))
        search_btn.pack(side="left")

        clear_btn = ctk.CTkButton(search_row, text="Clear", command=self.refresh_products, **self._btn_style("secondary", width=90))
        clear_btn.pack(side="left", padx=(10, 0))

        self.list_frame = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        right = ctk.CTkFrame(body, **get_card_style())
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(right, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))

        right_title = ctk.CTkLabel(header, text="Selected Product", **get_label_style("heading"))
        right_title.pack(anchor="w")

        preview_card = ctk.CTkFrame(right, fg_color=Colors.BG_WHITE, corner_radius=14)
        preview_card.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        preview_card.grid_columnconfigure(0, weight=1)

        self.preview_title = ctk.CTkLabel(
            preview_card,
            text="No product selected",
            font=(Fonts.FAMILY, Fonts.NORMAL),
            text_color=Colors.TEXT_SECONDARY,
        )
        self.preview_title.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        self.preview_img_label = ctk.CTkLabel(preview_card, text="")
        self.preview_img_label.grid(row=1, column=0, sticky="n", padx=14, pady=(0, 10))

        self.detail_label = ctk.CTkLabel(
            preview_card,
            text="Select a product from the list to see details here.",
            justify="left",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        self.detail_label.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self.btn_edit = ctk.CTkButton(actions, text="Edit", command=self.open_edit_dialog, state="disabled", **self._btn_style("primary"))
        self.btn_edit.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))

        self.btn_stock = ctk.CTkButton(actions, text="Update Stock", command=self.open_stock_dialog, state="disabled", **self._btn_style("secondary"))
        self.btn_stock.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))

        self.btn_delete = ctk.CTkButton(actions, text="Delete", command=self.delete_selected, state="disabled", **self._btn_style("danger"))
        self.btn_delete.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        self.btn_refresh = ctk.CTkButton(actions, text="Refresh", command=self.refresh_products, **self._btn_style("secondary"))
        self.btn_refresh.grid(row=1, column=1, sticky="ew", padx=(8, 0))

        self.parent.bind_all("<Control-f>", lambda e: self.search_entry.focus_set())
        self.parent.bind_all("<Escape>", lambda e: self._set_selected(None))

    @staticmethod
    def _btn_style(kind: str, **overrides):
        style = dict(get_button_style(kind))
        style.update(overrides)
        return style

    def refresh_products(self):
        self.search_entry.delete(0, "end")
        self.products = get_all_products()
        self.selected_product = None
        self._thumb_refs.clear()
        self._render_list()
        self._set_selected(None)
        self._set_status(total=len(self.products), mode="all")

    def search(self):
        q = self.search_entry.get().strip()
        self.products = search_products(q)
        self.selected_product = None
        self._thumb_refs.clear()
        self._render_list()
        self._set_selected(None)
        self._set_status(total=len(self.products), mode="search")

    def _set_status(self, total: int, mode: str):
        self.status_label.configure(text=f"Results: {total}" if mode == "search" else f"Total: {total}")

    def _render_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.products:
            empty = ctk.CTkLabel(
                self.list_frame,
                text="No products found.\nTry clearing search or adding a new product.",
                **get_label_style("small"),
            )
            empty.pack(pady=18)
            return

        for p in self.products:
            self._create_product_card(p)

    def _create_product_card(self, p: dict):
        card = ctk.CTkFrame(self.list_frame, fg_color=Colors.BG_WHITE, corner_radius=14)
        card.pack(fill="x", padx=8, pady=8)

        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(2, weight=0)

        thumb_label = ctk.CTkLabel(card, text="")
        thumb_label.grid(row=0, column=0, rowspan=2, sticky="w", padx=12, pady=12)

        img_src = p.get("product_image") or ""
        thumb_img = self._safe_ctk_image(img_src, size=(52, 52))
        if thumb_img is not None:
            thumb_label.configure(image=thumb_img)
            self._thumb_refs[p.get("product_id", id(p))] = thumb_img
        else:
            thumb_label.configure(text="No image", text_color=Colors.TEXT_SECONDARY, font=(Fonts.FAMILY, Fonts.SMALL))

        name = ctk.CTkLabel(card, text=p.get("product_name", "Unnamed"), **get_label_style("normal"))
        name.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(12, 2))

        desc = (p.get("product_description") or "").strip()
        desc_line = truncate_text(desc, 70) if desc else "No description."
        desc_lbl = ctk.CTkLabel(
            card,
            text=desc_line,
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        desc_lbl.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 12))

        meta = ctk.CTkLabel(
            card,
            text=f"{format_price(p.get('product_price', 0))}\nStock: {p.get('product_quantity', 0)}",
            justify="right",
            text_color=Colors.TEXT_SECONDARY,
            font=(Fonts.FAMILY, Fonts.SMALL),
        )
        meta.grid(row=0, column=2, rowspan=2, sticky="e", padx=12, pady=12)

        card.bind("<Button-1>", lambda e, prod=p: self._set_selected(prod))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, prod=p: self._set_selected(prod))

    def _set_selected(self, product):
        self.selected_product = product

        if not product:
            self.preview_title.configure(text="No product selected", text_color=Colors.TEXT_SECONDARY)
            self.detail_label.configure(text="Select a product from the list to see details here.")
            self.preview_img_label.configure(image=None, text="")
            self.btn_edit.configure(state="disabled")
            self.btn_stock.configure(state="disabled")
            self.btn_delete.configure(state="disabled")
            return

        self.preview_title.configure(text=product.get("product_name", "Unnamed"), text_color=Colors.TEXT_PRIMARY)

        img_src = product.get("product_image") or ""
        big_img = self._safe_ctk_image(img_src, size=(220, 220))
        if big_img is not None:
            self.preview_img_label.configure(image=big_img, text="")
            self._sidebar_img_ref = big_img
        else:
            self.preview_img_label.configure(image=None, text="No image", text_color=Colors.TEXT_SECONDARY)
            self._sidebar_img_ref = None

        desc = (product.get("product_description") or "").strip() or "No description provided."
        pid = product.get("product_id", "—")
        price = format_price(product.get("product_price", 0))
        stock = product.get("product_quantity", 0)
        img_text = product.get("product_image") or "None"

        details = (
            f"ID: {pid}\n"
            f"Price: {price}\n"
            f"Stock: {stock}\n"
            f"Image: {img_text}\n\n"
            f"Description:\n{truncate_text(desc, 260)}"
        )
        self.detail_label.configure(text=details, text_color=Colors.TEXT_PRIMARY)

        self.btn_edit.configure(state="normal")
        self.btn_stock.configure(state="normal")
        self.btn_delete.configure(state="normal")

    def _safe_ctk_image(self, src: str, size=(64, 64)):
        if not src:
            return None
        try:
            img = self._load_pil_image(src)
            if img is None:
                return None
            img = img.convert("RGBA")
            img = self._fit_center_crop(img, size)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception:
            return None

    @staticmethod
    @lru_cache(maxsize=128)
    def _load_pil_image(src: str):
        src = src.strip()

        if src.startswith("http://") or src.startswith("https://"):
            with urllib.request.urlopen(src, timeout=5) as resp:
                data = resp.read()
            return Image.open(io.BytesIO(data))

        if os.path.exists(src):
            return Image.open(src)

        rel = os.path.join(os.getcwd(), src)
        if os.path.exists(rel):
            return Image.open(rel)

        return None

    @staticmethod
    def _fit_center_crop(img: Image.Image, target_size):
        tw, th = target_size
        w, h = img.size
        target_ratio = tw / th
        img_ratio = w / h

        if img_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))

        return img.resize((tw, th), Image.LANCZOS)

    def open_add_dialog(self):
        def after_save():
            self._load_pil_image.cache_clear()
            self.refresh_products()
        ProductFormDialog(self.parent, product=None, on_saved=after_save)

    def open_edit_dialog(self):
        if not self.selected_product:
            return
        def after_save():
            self._load_pil_image.cache_clear()
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
            f"Delete product:\n\n{self.selected_product.get('product_name', 'Unnamed')}?"
        )
        if not ok:
            return

        img_path = self.selected_product.get("product_image")
        abs_img = img_path
        if img_path and not os.path.isabs(img_path):
            abs_img = os.path.join(_project_root(), img_path)

        if abs_img and os.path.exists(abs_img):
            try:
                os.remove(abs_img)
            except Exception:
                pass

        success, msg = delete_product(self.selected_product["product_id"])
        if success:
            messagebox.showinfo("Deleted", msg)
            self._load_pil_image.cache_clear()
            self.refresh_products()
        else:
            messagebox.showerror("Error", msg)

    def go_back(self):
        if self.on_back:
            self.parent.after(0, self.on_back)

    def destroy(self):
        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            self.main_frame.destroy()


class UserProductBrowseScreen:

    CARD_W = 350
    CARD_H = 380
    GAP_X = 12
    GAP_Y = 12

    def __init__(self, parent, on_back=None, user_data=None, show_back: bool = True):
        self.parent = parent
        self.on_back = on_back
        self.user_data = user_data
        self.show_back = show_back


        self.products = []
        self._img_refs = {}

        self._last_cols = None
        self._resize_job = None

        self.build_ui()
        self.load_products()

    @staticmethod
    def _btn_style(kind: str, **overrides):
        style = dict(get_button_style(kind))
        style.update(overrides)
        return style

    def add_to_cart(self, product):
        if not self.user_data or not self.user_data.get("user_id"):
            messagebox.showerror("Login required", "Please login to add items to cart.")
            return

        from ui.cart_ui import AddToCartDialog
        user_id = int(self.user_data["user_id"])
        AddToCartDialog(self.parent, user_id=user_id, product=product, on_added=None)

    def build_ui(self):
        def _enable_mousewheel(self, widget):
            def _on_mousewheel(event):
                try:
                    self.grid_scroll._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                except Exception:
                    pass

            def _bind(_):
                widget.bind_all("<MouseWheel>", _on_mousewheel)

            def _unbind(_):
                widget.unbind_all("<MouseWheel>")

            widget.bind("<Enter>", _bind)
            widget.bind("<Leave>", _unbind)

        self.main_frame = ctk.CTkFrame(self.parent, fg_color=Colors.BG_LIGHT, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        top = ctk.CTkFrame(self.main_frame, fg_color=Colors.BG_WHITE, corner_radius=0)
        top.pack(fill="x")

        title_text = "ORA Jewelry — Browse"
        if self.user_data and self.user_data.get("user_role") == "admin":
            title_text = "ORA Jewelry — Browse (Admin View)"

        title = ctk.CTkLabel(top, text=title_text, **get_label_style("heading"))
        title.pack(side="left", padx=20, pady=14)

        if self.show_back:
            back_btn = ctk.CTkButton(top, text="Back", command=self.go_back, **self._btn_style("secondary", width=110))
            back_btn.pack(side="right", padx=20, pady=14)


        search_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        search_row.pack(fill="x", padx=20, pady=(15, 5))

        self.search_entry = ctk.CTkEntry(
            search_row,
            width=360,
            placeholder_text="Search products...",
            **get_input_style(),
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search())

        search_btn = ctk.CTkButton(search_row, text="Search", command=self.search, **self._btn_style("primary", width=120))
        search_btn.pack(side="left", padx=(0, 10))

        clear_btn = ctk.CTkButton(search_row, text="Clear", command=self.load_products, **self._btn_style("secondary", width=90))
        clear_btn.pack(side="left")

        self.status_label = ctk.CTkLabel(
            self.main_frame, text="", text_color=Colors.TEXT_SECONDARY, font=(Fonts.FAMILY, Fonts.SMALL)
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 8))

        self.grid_scroll = ctk.CTkScrollableFrame(
        self.main_frame,
        fg_color=Colors.BG_LIGHT,   # not transparent
        corner_radius=0
)

        self.grid_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # responsive columns
        self.grid_scroll.bind("<Configure>", self._on_grid_resize)
        self._enable_mousewheel()

    def _enable_mousewheel(self):
        def _on_mousewheel(event):
            try:
                self.grid_scroll._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        def _bind(_event):
            self.grid_scroll.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind(_event):
            self.grid_scroll.unbind_all("<MouseWheel>")

        self.grid_scroll.bind("<Enter>", _bind)
        self.grid_scroll.bind("<Leave>", _unbind)

    def _on_grid_resize(self, _event):
        if self._resize_job is not None:
            try:
                self.parent.after_cancel(self._resize_job)
            except Exception:
                pass
        self._resize_job = self.parent.after(120, self._maybe_reflow)

    def _maybe_reflow(self):
        self._resize_job = None
        cols = self._calc_columns()
        if cols != self._last_cols:
            self.render_products()

    def _calc_columns(self):
        w = self.grid_scroll.winfo_width()
        if w <= 20:
            w = self.parent.winfo_width()
        if w <= 20:
            w = 1000

        per = self.CARD_W + self.GAP_X * 2
        cols = max(2, min(6, int(w // per)))
        return cols

    def load_products(self):
        self.search_entry.delete(0, "end")
        self.products = get_all_products()
        self._img_refs.clear()
        self.render_products()
        self.status_label.configure(text=f"Showing {len(self.products)} products")

    def search(self):
        q = self.search_entry.get().strip()
        self.products = search_products(q)
        self._img_refs.clear()
        self.render_products()
        self.status_label.configure(text=f"Found {len(self.products)} results")

    def render_products(self):
        for w in self.grid_scroll.winfo_children():
            w.destroy()

        if not self.products:
            empty = ctk.CTkLabel(self.grid_scroll, text="No products found.", **get_label_style("small"))
            empty.grid(row=0, column=0, padx=20, pady=20, sticky="w")
            self._last_cols = None
            return

        cols = self._calc_columns()
        self._last_cols = cols

        for c in range(cols):
            self.grid_scroll.grid_columnconfigure(c, weight=1, uniform="prod")

        row = 0
        col = 0

        for product in self.products:
            card = self._build_product_card(self.grid_scroll, product)
            card.grid(row=row, column=col, padx=self.GAP_X, pady=self.GAP_Y, sticky="nsew")

            col += 1
            if col >= cols:
                col = 0
                row += 1
                
        # make sure scrollbar updates correctly
        try:
            self.grid_scroll.update_idletasks()
            self.grid_scroll._parent_canvas.configure(scrollregion=self.grid_scroll._parent_canvas.bbox("all"))
        except Exception:
            pass


    def _build_product_card(self, parent, product):
        #the frame for each product
        card = ctk.CTkFrame(parent, fg_color=Colors.BG_WHITE, corner_radius=12, width=self.CARD_W, height=self.CARD_H)
        card.grid_propagate(False)


        def open_details(_=None):
            self.open_product_details(product)

        card.bind("<Button-1>", open_details)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=10)
        content.bind("<Button-1>", open_details)

        IMG_SIZE = 220  # square image size 
        img_box = ctk.CTkFrame(content,fg_color=Colors.BG_LIGHT,corner_radius=12, width=IMG_SIZE, height=IMG_SIZE)
        img_box.pack(anchor="w") 
        img_box.pack_propagate(False)
        img_box.bind("<Button-1>", open_details)

        img_label = ctk.CTkLabel(img_box, text="")
        img_label.place(relx=0.5, rely=0.5, anchor="center")
        img_label.bind("<Button-1>", open_details)

        img_src = (product.get("product_image") or "").strip()
        ctk_img = self._safe_ctk_image(img_src, size=(IMG_SIZE, IMG_SIZE))
        if ctk_img:
            img_label.configure(image=ctk_img, text="")
            self._img_refs[f"card_{product.get('product_id', id(product))}"] = ctk_img
        else:
            img_label.configure(text="No image", text_color=Colors.TEXT_SECONDARY, font=(Fonts.FAMILY, Fonts.SMALL))

        # name (2 lines max feel)
        name_raw = product.get("product_name", "Unnamed")
        name_text = truncate_text(name_raw, 44)
        name_lbl = ctk.CTkLabel(
            content,
            text=name_text,
            font=(Fonts.FAMILY, 14, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=self.CARD_W - 20,
            justify="left",
        )
        name_lbl.pack(anchor="w", pady=(10, 2))
        name_lbl.bind("<Button-1>", open_details)

        # price + stock row
        price_text = format_price(product.get("product_price", 0))
        stock_qty = int(product.get("product_quantity", 0) or 0)

        meta = ctk.CTkFrame(content, fg_color="transparent")
        meta.pack(fill="x", pady=(0, 6))
        meta.grid_columnconfigure(0, weight=1)
        meta.grid_columnconfigure(1, weight=0)
        meta.bind("<Button-1>", open_details)

        price_lbl = ctk.CTkLabel(
            meta,
            text=price_text,
            font=(Fonts.FAMILY, 13, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        )
        price_lbl.grid(row=0, column=0, sticky="w")
        price_lbl.bind("<Button-1>", open_details)

        stock_text = "In stock" if stock_qty > 0 else "Out of stock"
        stock_color = Colors.TEXT_SECONDARY if stock_qty > 0 else Colors.ERROR

        stock_lbl = ctk.CTkLabel(
            meta,
            text=stock_text,
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=stock_color,
        )
        stock_lbl.grid(row=0, column=1, sticky="e")
        stock_lbl.bind("<Button-1>", open_details)

        # short description (optional, very small)
        desc_raw = (product.get("product_description") or "").strip()
        desc_text = truncate_text(desc_raw, 55) if desc_raw else ""
        if desc_text:
            desc_lbl = ctk.CTkLabel(
                content,
                text=desc_text,
                font=(Fonts.FAMILY, 11),
                text_color=Colors.TEXT_SECONDARY,
                wraplength=self.CARD_W - 20,
                justify="left",
            )
            desc_lbl.pack(anchor="w", pady=(0, 8))
            desc_lbl.bind("<Button-1>", open_details)
        else:
            ctk.CTkFrame(content, fg_color="transparent", height=8).pack(fill="x")

        
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        secondary = self._btn_style("secondary", height=32, corner_radius=10)
        primary = self._btn_style("primary", height=32, corner_radius=10)

        view_btn = ctk.CTkButton(btn_row, text="View", command=open_details, **secondary)
        view_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        add_btn = ctk.CTkButton(
            btn_row,
            text="Add to cart",
            command=lambda: self.add_to_cart(product),
            state="normal" if stock_qty > 0 else "disabled",
            **primary
        )
        add_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        return card

    def _safe_ctk_image(self, src: str, size=(200, 200)):
        if not src:
            return None
        try:
            img = self._load_pil_image(src)
            if img is None:
                return None
            img = img.convert("RGBA")
            img = self._fit_center_crop(img, size)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception:
            return None

    @staticmethod
    @lru_cache(maxsize=128)
    def _load_pil_image(src: str):
        src = src.strip()

        if src.startswith("http://") or src.startswith("https://"):
            with urllib.request.urlopen(src, timeout=5) as resp:
                data = resp.read()
            return Image.open(io.BytesIO(data))

        if os.path.exists(src):
            return Image.open(src)

        rel = os.path.join(os.getcwd(), src)
        if os.path.exists(rel):
            return Image.open(rel)

        abs_from_root = os.path.join(_project_root(), src)
        if os.path.exists(abs_from_root):
            return Image.open(abs_from_root)

        return None

    @staticmethod
    def _fit_center_crop(img: Image.Image, target_size):
        tw, th = target_size
        w, h = img.size
        target_ratio = tw / th
        img_ratio = w / h

        if img_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))

        return img.resize((tw, th), Image.LANCZOS)

    def open_product_details(self, product):
        messagebox.showinfo(
            "Product Details",
            f"{product.get('product_name', '')}\n\n"
            f"Price: {format_price(product.get('product_price', 0))}\n"
            f"Stock: {product.get('product_quantity', 0)}\n\n"
            f"{product.get('product_description') or ''}",
        )

    def go_back(self):
        if self.on_back:
            self.parent.after(0, self.on_back)

    def destroy(self):
        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            self.main_frame.destroy()
