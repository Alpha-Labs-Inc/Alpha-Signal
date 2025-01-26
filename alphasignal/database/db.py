import sqlite3
from typing import List
import uuid
from datetime import datetime, timezone

from alphasignal.models.coin import Coin
from alphasignal.models.constants import DB_PATH
from alphasignal.models.enums import SellMode, SellType


class SQLiteDB:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)

    def initialize_database(self) -> None:
        cursor = self.connection.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS tracked_coins (
            id TEXT PRIMARY KEY,
            mint_address TEXT NOT NULL,
            last_price_max REAL,
            sell_mode TEXT,
            sell_value REAL,
            sell_type TEXT,
            time_added TEXT,
            time_sold TEXT,
            balance REAL, 
            is_active BOOLEAN DEFAULT 1
        );
        """)
        self.connection.commit()

    def create_coin(
        self,
        mint_address: str,
        sell_mode: SellMode,
        sell_value: float,
        sell_type: SellType,
        buy_in_value: float,
        balance: float,
    ) -> None:
        cursor = self.connection.cursor()
        time_added = datetime.now(timezone.utc).isoformat()
        coin_id = str(uuid.uuid4())
        try:
            cursor.execute(
                """
                INSERT INTO tracked_coins (
                    id, mint_address, last_price_max, sell_mode, sell_value, 
                    sell_type, time_added, time_sold, balance, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, 1)
                """,
                (
                    coin_id,
                    mint_address,
                    buy_in_value,
                    sell_mode.value,
                    sell_value,
                    sell_type.value,
                    time_added,
                    balance,
                ),
            )
            self.connection.commit()
            print(f"Coin with mint_address '{mint_address}' added successfully.")
        except sqlite3.IntegrityError as e:
            print(f"Error adding coin: {e}")

    def get_active_coins(self) -> List[Coin]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, mint_address, last_price_max, sell_mode, sell_value, sell_type, time_added, balance
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
                sell_type=SellType(row[5]),
                time_added=datetime.fromisoformat(row[6]),
                balance=row[7],
            )
            for row in rows
        ]

    def get_active_coin_balance_by_mint_address(self, mint_address: str) -> float:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT SUM(balance) FROM tracked_coins
            WHERE mint_address = ? AND is_active = 1
            """,
            (mint_address,),
        )
        used_balance = cursor.fetchone()[0] or 0.0
        return used_balance

    def update_coin_last_price(self, coin_id: str, new_price: float) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tracked_coins SET last_price_max = ? WHERE id = ?
            """,
            (new_price, coin_id),
        )
        self.connection.commit()

    def deactivate_coin(self, coin_id: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tracked_coins SET is_active = 0 WHERE id = ?
            """,
            (coin_id,),
        )
        self.connection.commit()
        print(f"Coin with ID '{coin_id}' has been deactivated.")

    def reactivate_coin(self, coin_id: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tracked_coins SET is_active = 1 WHERE id = ?
            """,
            (coin_id,),
        )
        self.connection.commit()
        print(f"Coin with ID '{coin_id}' has been reactivated.")

    def update_sell_time_sold(self, coin_id: str):
        time_sold = datetime.now(timezone.utc).isoformat()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tracked_coins SET time_sold = ? WHERE id = ?
            """,
            (
                time_sold,
                coin_id,
            ),
        )
        self.connection.commit()
        print(f"Time sold updated for Coin with ID '{coin_id}'.")
