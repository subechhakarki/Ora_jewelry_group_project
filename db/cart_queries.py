import sqlite3
from typing import List, Dict, Tuple, Optional


try:
    from db.database import DB_PATH  
except Exception:
    DB_PATH = "ora_jewelry.db"  #if it doesn't work



def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn



def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> Tuple[bool, str]:
    if quantity <= 0:
        return False, "Quantity must be greater than 0."


    conn = _get_conn()
    try:
        cur = conn.cursor()


        # Check product and stock
        cur.execute("SELECT product_quantity, product_name FROM products WHERE product_id = ?", (product_id,))
        prod = cur.fetchone()
        if not prod:
            return False, "Product not found."


        stock = int(prod["product_quantity"])
        name = prod["product_name"]


        # Current cart qty 
        cur.execute(
            "SELECT product_quantity FROM cart WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
        )
        row = cur.fetchone()


        current_qty = int(row["product_quantity"]) if row else 0
        new_qty = current_qty + quantity


        if new_qty > stock:
            return False, f"Not enough stock for '{name}'. Available: {stock}, requested total: {new_qty}."


        # Insert or update thingss
        cur.execute(
            """
            INSERT INTO cart(user_id, product_id, product_quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id)
            DO UPDATE SET product_quantity = excluded.product_quantity, added_at = CURRENT_TIMESTAMP
            """,
            (user_id, product_id, new_qty),
        )


        conn.commit()
        return True, f"Added to cart: {name} (Qty: {new_qty})"


    except Exception as e:
        conn.rollback()
        return False, f"Failed to add to cart: {e}"
    finally:
        conn.close()




def get_cart_items(user_id: int) -> List[Dict]:
    """
    Returns cart items with product details.
    """
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                c.cart_id,
                c.user_id,
                c.product_id,
                c.product_quantity AS cart_quantity,
                c.added_at,
                p.product_name,
                p.product_price,
                p.product_quantity AS stock_quantity,
                p.product_image,
                p.product_description
            FROM cart c
            JOIN products p ON p.product_id = c.product_id
            WHERE c.user_id = ?
            ORDER BY c.added_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()




def update_cart_quantity(user_id: int, product_id: int, new_quantity: int) -> Tuple[bool, str]:
    if new_quantity <= 0:
        return False, "Quantity must be greater than 0."


    conn = _get_conn()
    try:
        cur = conn.cursor()


        cur.execute("SELECT product_quantity, product_name FROM products WHERE product_id = ?", (product_id,))
        prod = cur.fetchone()
        if not prod:
            return False, "Product not found."


        stock = int(prod["product_quantity"])
        name = prod["product_name"]


        if new_quantity > stock:
            return False, f"Not enough stock for '{name}'. Available: {stock}."


        cur.execute(
            """
            UPDATE cart
            SET product_quantity = ?, added_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND product_id = ?
            """,
            (new_quantity, user_id, product_id),
        )


        if cur.rowcount == 0:
            return False, "Item not found in cart."


        conn.commit()
        return True, f"Updated '{name}' to Qty: {new_quantity}"
    except Exception as e:
        conn.rollback()
        return False, f"Failed to update cart: {e}"
    finally:
        conn.close()




def remove_from_cart(user_id: int, product_id: int) -> Tuple[bool, str]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        if cur.rowcount == 0:
            return False, "Item not found in cart."
        conn.commit()
        return True, "Removed item from cart."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to remove item: {e}"
    finally:
        conn.close()




def clear_cart(user_id: int) -> Tuple[bool, str]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()
        return True, "Cart cleared."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to clear cart: {e}"
    finally:
        conn.close()




def cart_totals(user_id: int) -> Dict:
    items = get_cart_items(user_id)
    subtotal = 0
    count = 0
    for it in items:
        qty = int(it["cart_quantity"])
        price = float(it["product_price"])
        subtotal += qty * price
        count += qty
    return {"subtotal": subtotal, "item_count": count, "unique_items": len(items)}





