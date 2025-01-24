import sqlite3
import uuid
from datetime import datetime

DB_PATH = "alphasignal.db"

def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

def initialize_database() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS tracked_coins (
            id TEXT PRIMARY KEY,
            mint_address TEXT NOT NULL,
            last_price_max REAL,
            sell_mode TEXT,
            sell_value REAL,
            time_purchased TEXT,
            time_sold TEXT,
            buy_in_value REAL,
            profit REAL,
            is_active BOOLEAN DEFAULT 1
        );
        """)
        conn.commit()

def create_coin(
    mint_address: str,
    last_price_max: float,
    sell_mode: str,
    sell_value: float,
    buy_in_value: float
) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        time_purchased = datetime.utcnow().isoformat()
        coin_id = str(uuid.uuid4())
        try:
            cursor.execute(
                """
                INSERT INTO tracked_coins (
                    id, mint_address, last_price_max, sell_mode, sell_value, 
                    time_purchased, time_sold, buy_in_value, profit, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, NULL, 1)
                """,
                (coin_id, mint_address, last_price_max, sell_mode, sell_value, time_purchased, buy_in_value)
            )
            conn.commit()
            print(f"Coin with mint_address '{mint_address}' added successfully.")
        except sqlite3.IntegrityError as e:
            print(f"Error adding coin: {e}")
