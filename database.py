import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("orders.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_order(order_id: str):
    with get_connection() as conn:
        order = conn.execute(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        ).fetchone()
    return dict(order) if order else None


def get_customer_orders(customer_name: str):
    with get_connection() as conn:
        orders = conn.execute(
            "SELECT * FROM orders WHERE customer_name = ? ORDER BY order_id",
            (customer_name,),
        ).fetchall()
    return [dict(order) for order in orders]


def update_status(order_id: str, status: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            (status, order_id),
        )
    return cursor.rowcount > 0


def add_note(order_id: str, note: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE orders SET note = ? WHERE order_id = ?",
            (note, order_id),
        )
    return cursor.rowcount > 0


def cancel_order(order_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE orders SET status = 'CANCELLED' WHERE order_id = ?",
            (order_id,),
        )
    return cursor.rowcount > 0
