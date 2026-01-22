import sqlite3
from typing import Tuple, List, Dict

from db.product_queries import reduce_product_stock

try:
    from db.database import DB_PATH
except Exception:
    DB_PATH = "ora_jewelry.db"




def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn




def create_orders_from_cart(user_id: int) -> Tuple[bool, str, int]:

    conn = _get_conn()
    try:
        cur = conn.cursor()


        # get cart items with products price and stock
        cur.execute(
            """
            SELECT
                c.product_id,
                c.product_quantity AS cart_quantity,
                p.product_name,
                p.product_price,
                p.product_quantity AS stock_quantity
            FROM cart c
            JOIN products p ON p.product_id = c.product_id
            WHERE c.user_id = ?
            """,
            (user_id,),
        )
        items = cur.fetchall()


        if not items:
            return False, "Cart is empty.", 0


        # check stock for all items first
        for it in items:
            stock = int(it["stock_quantity"])
            qty = int(it["cart_quantity"])
            if qty > stock:
                return False, f"Not enough stock for '{it['product_name']}'. Available: {stock}", 0


        # make sales rows and reduce stock
    
        created = 0


        for it in items:
            product_id = int(it["product_id"])
            qty = int(it["cart_quantity"])
            price = float(it["product_price"])
            total_price = qty * price


            # insert things into sales
            cur.execute(
                """
                INSERT INTO sales (user_id, product_id, sale_quantity, total_price, order_status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, product_id, qty, total_price, "on-going"),
            )


            # reduce stock
            ok, msg = reduce_product_stock(product_id, qty, conn=conn)
            if not ok:
                raise Exception(msg)


            created += 1


        conn.commit()
        return True, f"Checkout complete. Created {created} order(s).", created


    except Exception as e:
        conn.rollback()
        return False, f"Checkout failed: {e}", 0
    finally:
        conn.close()
       
def get_orders_by_user(user_id: int) -> List[Dict]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                s.sale_id,
                s.user_id,
                s.product_id,
                s.sale_quantity,
                s.total_price,
                s.order_status,
                s.order_date,
                p.product_name,
                p.product_price,
                p.product_image,
                p.product_description
            FROM sales s
            JOIN products p ON p.product_id = s.product_id
            WHERE s.user_id = ?
            ORDER BY s.order_date DESC, s.sale_id DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()




def get_all_orders(status: str = "all", search_text: str = "") -> List[Dict]:
    conn = _get_conn()
    try:
        cur = conn.cursor()


        where_clauses = []
        params = []


        if status and status != "all":
            where_clauses.append("s.order_status = ?")
            params.append(status)


        q = (search_text or "").strip()
        if q:
            like = f"%{q}%"
            where_clauses.append(
                "(u.user_name LIKE ? OR p.product_name LIKE ? OR CAST(s.sale_id AS TEXT) LIKE ?)"
            )
            params.extend([like, like, like])


        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)


        cur.execute(
            f"""
            SELECT
                s.sale_id,
                s.user_id,
                s.product_id,
                s.sale_quantity,
                s.total_price,
                s.order_status,
                s.order_date,
                u.user_name,
                u.user_email,
                p.product_name,
                p.product_price,
                p.product_image,
                p.product_description
            FROM sales s
            JOIN users u ON u.user_id = s.user_id
            JOIN products p ON p.product_id = s.product_id
            {where_sql}
            ORDER BY s.order_date DESC, s.sale_id DESC
            """,
            tuple(params),
        )


        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()




def order_stats() -> Dict:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM sales")
        total = int(cur.fetchone()["total"])


        cur.execute(
            """
            SELECT order_status, COUNT(*) AS cnt
            FROM sales
            GROUP BY order_status
            """
        )
        by_status = {r["order_status"]: int(r["cnt"]) for r in cur.fetchall()}


        return {
            "total": total,
            "on-going": by_status.get("on-going", 0),
            "delivering": by_status.get("delivering", 0),
            "finished": by_status.get("finished", 0),
            "cancelled": by_status.get("cancelled", 0),
        }
    finally:
        conn.close()




def update_order_status(sale_id: int, new_status: str) -> Tuple[bool, str]:
    allowed = {"on-going", "delivering", "finished", "cancelled"}
    if new_status not in allowed:
        return False, f"Invalid status. Allowed: {', '.join(sorted(allowed))}"


    conn = _get_conn()
    try:
        cur = conn.cursor()


        cur.execute("SELECT order_status FROM sales WHERE sale_id = ?", (sale_id,))
        row = cur.fetchone()
        if not row:
            return False, "Order not found."


        current = row["order_status"]


        # if finished is terminal
        if current == "finished":
            return False, "Finished orders cannot be changed."


        #  transitions delivering or cancelled or finished 
        transitions = {
            "on-going": {"delivering", "cancelled"},
            "delivering": {"finished", "cancelled"},
            "cancelled": set(),     
            "finished": set(),      
        }


        if new_status == current:
            return True, "No change (status already set)."


        if new_status not in transitions.get(current, set()):
            return False, f"Invalid transition: {current} → {new_status}"


        cur.execute(
            "UPDATE sales SET order_status = ? WHERE sale_id = ?",
            (new_status, sale_id),
        )
        conn.commit()


        if cur.rowcount == 0:
            return False, "Update failed."


        return True, f"Order #{sale_id} updated: {current} → {new_status}"


    except Exception as e:
        conn.rollback()
        return False, f"Failed to update status: {e}"
    finally:
        conn.close()




def cancel_order(sale_id: int) -> Tuple[bool, str, Dict]:
    conn = _get_conn()
    try:
        cur = conn.cursor()


        cur.execute(
            "SELECT order_status, product_id, sale_quantity FROM sales WHERE sale_id = ?",
            (sale_id,),
        )
        row = cur.fetchone()
        if not row:
            return False, "Order not found.", {}


        current = row["order_status"]
        if current in ("finished", "cancelled"):
            return False, f"Cannot cancel an order that is '{current}'.", {}


        # make cancelled
        cur.execute(
            "UPDATE sales SET order_status = 'cancelled' WHERE sale_id = ?",
            (sale_id,),
        )
        conn.commit()


        return True, f"Order #{sale_id} cancelled.", {
            "product_id": int(row["product_id"]),
            "sale_quantity": int(row["sale_quantity"]),
        }


    except Exception as e:
        conn.rollback()
        return False, f"Cancel failed: {e}", {}
    finally:
        conn.close()





