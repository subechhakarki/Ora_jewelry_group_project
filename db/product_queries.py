
import sqlite3
from db.database import get_connection, close_connection
"""
Product Queries Module

This module handles all database operations related to product management,
including create, read, update, delete (CRUD) and stock adjustments.
"""

def create_product(name, price, quantity, image_path=None, description=None):
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



#gets it by product id
def get_product_by_id(product_id):
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




#updating the product 
def update_product(product_id, name=None, price=None, quantity=None, image_path=None, description=None):
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



#only update quantity
def update_stock(product_id, new_quantity):
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




#deleting product
def delete_product(product_id):
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




def reduce_product_stock(product_id, reduce_by, conn=None):
    try:
        reduce_by = int(reduce_by)
        if reduce_by <= 0:
            return False, "reduce_by must be > 0"
    except ValueError:
        return False, "reduce_by must be an integer"


    owns_conn = False
    if conn is None:
        conn = get_connection()
        owns_conn = True


    cursor = conn.cursor()


    try:
        cursor.execute(
            "SELECT product_quantity FROM products WHERE product_id = ?",
            (product_id,),
        )
        row = cursor.fetchone()
        if not row:
            if owns_conn:
                close_connection(conn)
            return False, "Product not found"


        current_qty = int(row[0])
        if reduce_by > current_qty:
            if owns_conn:
                close_connection(conn)
            return False, f"Not enough stock. Available: {current_qty}"


        new_qty = current_qty - reduce_by


        cursor.execute(
            "UPDATE products SET product_quantity = ? WHERE product_id = ?",
            (new_qty, product_id),
        )


        if cursor.rowcount == 0:
            if owns_conn:
                close_connection(conn)
            return False, "Stock update failed"


        if owns_conn:
            conn.commit()
            close_connection(conn)


        return True, f"Stock reduced successfully (now {new_qty})"


    except sqlite3.Error as e:
        if owns_conn:
            conn.rollback()
            close_connection(conn)
        return False, f"Database error: {str(e)}"




def restock_product(product_id, add_qty, conn=None):
    try:
        add_qty = int(add_qty)
        if add_qty <= 0:
            return False, "add_qty must be > 0"
    except ValueError:
        return False, "add_qty must be an integer"


    owns_conn = False
    if conn is None:
        conn = get_connection()
        owns_conn = True


    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT product_quantity FROM products WHERE product_id = ?",
            (product_id,),
        )
        row = cursor.fetchone()
        if not row:
            if owns_conn:
                close_connection(conn)
            return False, "Product not found"


        new_qty = int(row[0]) + add_qty


        cursor.execute(
            "UPDATE products SET product_quantity = ? WHERE product_id = ?",
            (new_qty, product_id),
        )


        if owns_conn:
            conn.commit()
            close_connection(conn)


        return True, f"Restocked successfully (now {new_qty})"


    except sqlite3.Error as e:
        if owns_conn:
            conn.rollback()
            close_connection(conn)
        return False, f"Database error: {str(e)}"





