# db/product_queries.py
"""
Product CRUD operations for ORA Jewelry Store
Table: products
Columns:
- product_id (PK)
- product_name (TEXT, NOT NULL)
- product_price (REAL, NOT NULL, CHECK >= 0)
- product_quantity (INTEGER, NOT NULL, CHECK >= 0)
- product_image (TEXT, optional)
- product_description (TEXT, optional)
- created_at (TIMESTAMP default)
"""

import sqlite3
from db.database import get_connection, close_connection


# =========================
# CREATE
# =========================
def create_product(name, price, quantity, image_path=None, description=None):
    """
    Create a new product.
    Returns: (success: bool, message: str, product_id: int|None)
    """
    if not name or name.strip() == "":
        return False, "Product name is required", None

    try:
        price = float(price)
        if price < 0:
            return False, "Price must be >= 0", None
    except ValueError:
        return False, "Price must be a valid number", None

    try:
        quantity = int(quantity)
        if quantity < 0:
            return False, "Quantity must be >= 0", None
    except ValueError:
        return False, "Quantity must be a valid integer", None

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO products (product_name, product_price, product_quantity, product_image, product_description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name.strip(), price, quantity, image_path, description),
        )
        conn.commit()
        product_id = cursor.lastrowid
        close_connection(conn)
        return True, "Product created successfully", product_id

    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}", None


# =========================
# READ
# =========================
def get_product_by_id(product_id):
    """
    Get a single product by ID.
    Returns: product dict or None
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT product_id, product_name, product_price, product_quantity,
               product_image, product_description, created_at
        FROM products
        WHERE product_id = ?
        """,
        (product_id,),
    )
    row = cursor.fetchone()
    close_connection(conn)

    if not row:
        return None

    return {
        "product_id": row[0],
        "product_name": row[1],
        "product_price": row[2],
        "product_quantity": row[3],
        "product_image": row[4],
        "product_description": row[5],
        "created_at": row[6],
    }


def get_all_products():
    """
    Get all products (newest first).
    Returns: list[dict]
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT product_id, product_name, product_price, product_quantity,
               product_image, product_description, created_at
        FROM products
        ORDER BY created_at DESC
        """
    )
    rows = cursor.fetchall()
    close_connection(conn)

    products = []
    for row in rows:
        products.append(
            {
                "product_id": row[0],
                "product_name": row[1],
                "product_price": row[2],
                "product_quantity": row[3],
                "product_image": row[4],
                "product_description": row[5],
                "created_at": row[6],
            }
        )
    return products


def search_products(query_text):
    """
    Search products by name/description (case-insensitive-ish).
    Returns: list[dict]
    """
    q = (query_text or "").strip()
    if not q:
        return get_all_products()

    conn = get_connection()
    cursor = conn.cursor()

    like = f"%{q}%"
    cursor.execute(
        """
        SELECT product_id, product_name, product_price, product_quantity,
               product_image, product_description, created_at
        FROM products
        WHERE product_name LIKE ? OR product_description LIKE ?
        ORDER BY created_at DESC
        """,
        (like, like),
    )
    rows = cursor.fetchall()
    close_connection(conn)

    results = []
    for row in rows:
        results.append(
            {
                "product_id": row[0],
                "product_name": row[1],
                "product_price": row[2],
                "product_quantity": row[3],
                "product_image": row[4],
                "product_description": row[5],
                "created_at": row[6],
            }
        )
    return results


# =========================
# UPDATE
# =========================
def update_product(product_id, name=None, price=None, quantity=None, image_path=None, description=None):
    """
    Update product fields (any subset).
    Returns: (success: bool, message: str)
    """
    updates = []
    params = []

    if name is not None:
        name = str(name).strip()
        if name == "":
            return False, "Product name cannot be empty"
        updates.append("product_name = ?")
        params.append(name)

    if price is not None:
        try:
            price = float(price)
            if price < 0:
                return False, "Price must be >= 0"
        except ValueError:
            return False, "Price must be a valid number"
        updates.append("product_price = ?")
        params.append(price)

    if quantity is not None:
        try:
            quantity = int(quantity)
            if quantity < 0:
                return False, "Quantity must be >= 0"
        except ValueError:
            return False, "Quantity must be a valid integer"
        updates.append("product_quantity = ?")
        params.append(quantity)

    if image_path is not None:
        # allow empty string to clear image if you want
        updates.append("product_image = ?")
        params.append(image_path)

    if description is not None:
        updates.append("product_description = ?")
        params.append(description)

    if not updates:
        return False, "No fields to update"

    params.append(product_id)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"UPDATE products SET {', '.join(updates)} WHERE product_id = ?",
            params,
        )
        conn.commit()

        if cursor.rowcount == 0:
            close_connection(conn)
            return False, "Product not found"

        close_connection(conn)
        return True, "Product updated successfully"

    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}"


def update_stock(product_id, new_quantity):
    """
    Update only stock/quantity (admin stock management).
    Returns: (success: bool, message: str)
    """
    try:
        new_quantity = int(new_quantity)
        if new_quantity < 0:
            return False, "Quantity must be >= 0"
    except ValueError:
        return False, "Quantity must be a valid integer"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE products SET product_quantity = ? WHERE product_id = ?",
            (new_quantity, product_id),
        )
        conn.commit()

        if cursor.rowcount == 0:
            close_connection(conn)
            return False, "Product not found"

        close_connection(conn)
        return True, "Stock updated successfully"

    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}"


def adjust_stock(product_id, delta):
    """
    Adjust stock by delta (+/-). Prevents stock going below 0.
    Returns: (success: bool, message: str)
    """
    try:
        delta = int(delta)
    except ValueError:
        return False, "Delta must be an integer"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT product_quantity FROM products WHERE product_id = ?",
            (product_id,),
        )
        row = cursor.fetchone()
        if not row:
            close_connection(conn)
            return False, "Product not found"

        current_qty = int(row[0])
        new_qty = current_qty + delta

        if new_qty < 0:
            close_connection(conn)
            return False, "Not enough stock (would go below 0)"

        cursor.execute(
            "UPDATE products SET product_quantity = ? WHERE product_id = ?",
            (new_qty, product_id),
        )
        conn.commit()
        close_connection(conn)
        return True, f"Stock adjusted successfully (now {new_qty})"

    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}"


# =========================
# DELETE
# =========================
def delete_product(product_id):
    """
    Delete a product by ID.
    NOTE: Your schema uses ON DELETE CASCADE in cart/sales, so related rows will be removed too.
    Returns: (success: bool, message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        conn.commit()

        if cursor.rowcount == 0:
            close_connection(conn)
            return False, "Product not found"

        close_connection(conn)
        return True, "Product deleted successfully"

    except sqlite3.Error as e:
        close_connection(conn)
        return False, f"Database error: {str(e)}"
