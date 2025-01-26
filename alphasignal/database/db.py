import sqlite3
from typing import List
import uuid
from datetime import datetime, timezone

from alphasignal.models.coin import Coin
from alphasignal.models.enums import SellMode

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
            time_added TEXT,
            time_sold TEXT,
            balance REAL,
            is_active BOOLEAN DEFAULT 1
        );
        """)
        conn.commit()


def create_coin(
    mint_address: str,
    sell_mode: SellMode,
    sell_value: float,
    buy_in_value: float,
    balance: float,
) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        time_added = datetime.now(timezone.utc).isoformat()
        coin_id = str(uuid.uuid4())
        try:
            cursor.execute(
                """
                INSERT INTO tracked_coins (
                    id, mint_address, last_price_max, sell_mode, sell_value, 
                    time_added, time_sold, balance, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, 1)
                """,
                (
                    coin_id,
                    mint_address,
                    buy_in_value,
                    sell_mode.value,
                    sell_value,
                    time_added,
                    balance,
                ),
            )
            conn.commit()
            print(f"Coin with mint_address '{mint_address}' added successfully.")
        except sqlite3.IntegrityError as e:
            print(f"Error adding coin: {e}")


def get_active_coins() -> List[Coin]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, mint_address, last_price_max, sell_mode, sell_value, time_added, balance
            FROM tracked_coins
            WHERE is_active = 1
            """
        )
        rows = cursor.fetchall()
        return [
            Coin(
                id=row[0],
                mint_address=row[1],
                last_price_max=row[2],
                sell_mode=SellMode(row[3]),
                sell_value=row[4],
                time_added=datetime.fromisoformat(row[5]),
                balance=row[6],
            )
            for row in rows
        ]


def get_active_coin_balance_by_mint_address(mint_address: str) -> float:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT SUM(balance) FROM tracked_coins
            WHERE mint_address = ? AND is_active = 1
            """,
            (mint_address,),
        )
        used_balance = cursor.fetchone()[0] or 0.0
        return used_balance


def update_coin_last_price(coin_id: str, new_price: float) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tracked_coins SET last_price_max = ? WHERE id = ?
            """,
            (new_price, coin_id),
        )
        conn.commit()


def deactivate_coin(coin_id: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tracked_coins SET is_active = 0 WHERE id = ?
            """,
            (coin_id,),
        )
        conn.commit()
        print(f"Coin with ID '{coin_id}' has been deactivated.")


def reactivate_coin(coin_id: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE tracked_coins SET is_active = 1 WHERE id = ?
            """,
            (coin_id,),
        )
        conn.commit()
        print(f"Coin with ID '{coin_id}' has been reactivated.")
