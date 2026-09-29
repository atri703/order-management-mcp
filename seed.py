import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("orders.db")

ORDERS = [
    ("ORD-1001", "Atri Gulati", "MacBook Pro", 189999, "PROCESSING", ""),
    ("ORD-1002", "Rahul Sharma", "iPhone 17", 89999, "SHIPPED", ""),
    ("ORD-1003", "Priya Singh", "AirPods Pro", 24999, "DELIVERED", ""),
    ("ORD-1004", "Atri Gulati", "Magic Mouse", 8999, "PENDING", ""),
    ("ORD-1005", "Neha Verma", "iPad Air", 69999, "PROCESSING", ""),
]


def seed():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DROP TABLE IF EXISTS orders")
        conn.execute(
            """
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                product TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                note TEXT DEFAULT ''
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO orders (
                order_id,
                customer_name,
                product,
                amount,
                status,
                note
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ORDERS,
        )

    print(f"Seeded {len(ORDERS)} orders into {DB_PATH}")


if __name__ == "__main__":
    seed()
