import sqlite3
from typing import List
import uuid
from datetime import datetime, timezone

from alphasignal.models.order import Order
from alphasignal.models.constants import DB_PATH
from alphasignal.models.enums import (
    AmountType,
    BuyType,
    OrderStatus,
    Platform,
    SellMode,
    SellType,
)
from alphasignal.models.profile import Profile
from alphasignal.models.token_info import TokenInfo


class ProfileNotFoundError(Exception):
    def __init__(self, profile_id: str):
        super().__init__(f"Profile with ID '{profile_id}' not found.")
        self.profile_id = profile_id


class SQLiteDB:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)

    def initialize_database(self) -> None:
        cursor = self.connection.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS tracked_orders (
            id TEXT PRIMARY KEY,
            mint_address TEXT NOT NULL,
            last_price_max REAL,
            sell_mode TEXT,
            sell_value REAL,
            sell_type TEXT,
            time_added TEXT,
            time_sold TEXT,
            balance REAL, 
            order_status INTEGER DEFAULT 0,
            profit TEXT,
            slippage REAL
        );
        """)
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS token_info (
            mint_address TEXT PRIMARY KEY,
            name TEXT,
            ticker TEXT,
            image TEXT
        );
        """)
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS profile (
            id TEXT PRIMARY KEY,
            platform TEXT,
            signal TEXT,
            is_active BOOLEAN,
            buy_type TEXT,
            buy_amount_type TEXT,
            buy_amount REAL,
            buy_slippage REAL,
            sell_mode TEXT,
            sell_type TEXT,
            sell_value REAL,
            sell_slippage REAL
        );
        """)
        self.connection.commit()

    def add_token_info(
        self,
        mint_address,
        name,
        ticker,
        image,
    ):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO token_info (mint_address, name, ticker, image)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(mint_address) DO UPDATE SET
                    name=excluded.name,
                    ticker=excluded.ticker,
                    image=excluded.image;
            """,
                (
                    mint_address,
                    name,
                    ticker,
                    image,
                ),
            )

            self.connection.commit()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    def get_token_info(self, mint_address):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT mint_address, name, ticker, image
                FROM token_info
                WHERE mint_address = ?;
            """,
                (mint_address,),
            )

            row = cursor.fetchone()

            if row:
                return TokenInfo(
                    mint_address=row[0],
                    name=row[1],
                    ticker=row[2],
                    image=row[3] if row[3] else None,
                )
            return None

        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        return None

    def create_order(
        self,
        mint_address: str,
        sell_mode: SellMode,
        sell_value: float,
        sell_type: SellType,
        buy_in_value: float,
        balance: float,
        slippage: float,
    ) -> str:
        cursor = self.connection.cursor()
        time_added = datetime.now(timezone.utc).isoformat()
        order_id = str(uuid.uuid4())
        try:
            cursor.execute(
                """
                INSERT INTO tracked_orders (
                    id, mint_address, last_price_max, sell_mode, sell_value, 
                    sell_type, time_added, time_sold, balance, order_status, profit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, 0, NULL, ?)
                """,
                (
                    order_id,
                    mint_address,
                    buy_in_value,
                    sell_mode.value,
                    sell_value,
                    sell_type.value,
                    time_added,
                    balance,
                    slippage,
                ),
            )
            self.connection.commit()
            print(f"Order with mint_address '{mint_address}' added successfully.")
            return order_id
        except sqlite3.IntegrityError as e:
            print(f"Error adding order: {e}")

    def get_orders(self, status: OrderStatus) -> List[Order]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, mint_address, last_price_max, sell_mode, sell_value, sell_type, time_added, balance, order_status, profit, slippage
            FROM tracked_orders
            WHERE order_status = ?
            """,
            (status.value,),
        )
        rows = cursor.fetchall()
        return [
            Order(
                id=row[0],
                mint_address=row[1],
                last_price_max=row[2],
                sell_mode=SellMode(row[3]),
                sell_value=row[4],
                sell_type=SellType(row[5]),
                time_added=datetime.fromisoformat(row[6]),
                balance=row[7],
                status=OrderStatus(row[8]),
                profit=row[9],
                slippage=row[10],
            )
            for row in rows
        ]

    def get_active_order_balance_by_mint_address(self, mint_address: str) -> float:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT SUM(balance) FROM tracked_orders
            WHERE mint_address = ? AND order_status = ?
            """,
            (mint_address, OrderStatus.ACTIVE.value),
        )
        used_balance = cursor.fetchone()[0] or 0.0
        return used_balance

    def update_order_last_price(self, order_id: str, new_price: float) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tracked_orders SET last_price_max = ? WHERE id = ?
            """,
            (new_price, order_id),
        )
        self.connection.commit()

    def set_order_status(self, order_id: str, status: OrderStatus) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tracked_orders SET order_status = ? WHERE id = ?
            """,
            (
                status.value,
                order_id,
            ),
        )
        self.connection.commit()
        print(f"Order with ID '{order_id}' has been canceled.")

    def complete_order(self, order_id: str, profit: str = None):
        time_sold = datetime.now(timezone.utc).isoformat()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tracked_orders SET order_status = ?, time_sold = ?, profit = ? WHERE id = ?
            """,
            (
                OrderStatus.COMPLETE.value,
                time_sold,
                profit,
                order_id,
            ),
        )
        self.connection.commit()
        print(f"Completed Order with ID '{order_id}'.")

    def add_profile(
        self,
        platform: Platform,
        signal: str,
        buy_type: BuyType,
        buy_amount_type: AmountType,
        buy_amount: float,
        buy_slippage: float,
        sell_mode: SellMode,
        sell_type: SellType,
        sell_value: float,
        sell_slippage: float,
    ) -> str:
        # Generate a unique ID based on platform and signal using hashlib
        profile_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{platform}_{signal}"))
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO profile (
                    id, platform, signal, is_active, buy_type, buy_amount_type, 
                    buy_amount, buy_slippage, sell_mode, sell_type, 
                    sell_value, sell_slippage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile_id,
                    platform.value,
                    signal,
                    True,  # Default to active
                    buy_type.value,
                    buy_amount_type.value,
                    buy_amount,
                    buy_slippage,
                    sell_mode.value,
                    sell_type.value,
                    sell_value,
                    sell_slippage,
                ),
            )
            self.connection.commit()
            print(
                f"Profile with platform '{platform}' and signal '{signal}' added successfully."
            )
            return profile_id
        except sqlite3.Error as e:
            print(f"Error adding profile: {e}")
            return None

    def deactivate_profile(self, profile_id: str) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                UPDATE profile SET is_active = ? WHERE id = ?
                """,
                (False, profile_id),
            )
            self.connection.commit()
            print(f"Profile with ID '{profile_id}' has been deactivated.")
        except sqlite3.Error as e:
            print(f"Error deactivating profile: {e}")

    def activate_profile(self, profile_id: str) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                UPDATE profile SET is_active = ? WHERE id = ?
                """,
                (True, profile_id),
            )
            self.connection.commit()
            print(f"Profile with ID '{profile_id}' has been activated.")
        except sqlite3.Error as e:
            print(f"Error activating profile: {e}")

    def update_profile(
        self,
        profile_id: str,
        buy_type: BuyType,
        buy_amount_type: AmountType,
        buy_amount: float,
        buy_slippage: float,
        sell_mode: SellMode,
        sell_type: SellType,
        sell_value: float,
        sell_slippage: float,
    ) -> None:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                UPDATE profile SET 
                    buy_type = ?, 
                    buy_amount_type = ?, 
                    buy_amount = ?, 
                    buy_slippage = ?, 
                    sell_mode = ?, 
                    sell_type = ?, 
                    sell_value = ?, 
                    sell_slippage = ?
                WHERE id = ?
                """,
                (
                    buy_type.value,
                    buy_amount_type.value,
                    buy_amount,
                    buy_slippage,
                    sell_mode.value,
                    sell_type.value,
                    sell_value,
                    sell_slippage,
                    profile_id,
                ),
            )
            self.connection.commit()
            print(f"Profile with ID '{profile_id}' has been updated.")
        except sqlite3.Error as e:
            print(f"Error updating profile: {e}")

    def get_profile_data(self, profile_id: str) -> Profile:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, platform, signal, is_active, buy_type, buy_amount_type, 
                   buy_amount, buy_slippage, sell_mode, sell_type, 
                   sell_value, sell_slippage
            FROM profile
            WHERE id = ?;
            """,
            (profile_id,),
        )
        row = cursor.fetchone()
        if row:
            # Return the profile as a Pydantic model
            return Profile(
                id=row[0],
                platform=Platform(row[1]),
                signal=row[2],
                is_active=bool(row[3]),
                buy_type=BuyType(row[4]),
                buy_amount_type=AmountType(row[5]),
                buy_amount=row[6],
                buy_slippage=row[7],
                sell_mode=SellMode(row[8]),
                sell_type=SellType(row[9]),
                sell_value=row[10],
                sell_slippage=row[11],
            )
        # Raise an exception if the profile is not found
        raise ProfileNotFoundError(profile_id)

    def delete_profile(self, profile_id: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            DELETE FROM profile WHERE id = ?;
            """,
            (profile_id,),
        )
        self.connection.commit()

        if cursor.rowcount == 0:
            raise ProfileNotFoundError(profile_id)

        print(f"Profile with ID '{profile_id}' has been deleted.")

    def get_profiles(self) -> List[Profile]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, platform, signal, is_active, buy_type, buy_amount_type, 
                buy_amount, buy_slippage, sell_mode, sell_type, 
                sell_value, sell_slippage
            FROM profile;
            """
        )
        rows = cursor.fetchall()
        return [
            Profile(
                id=row[0],
                platform=Platform(row[1]),
                signal=row[2],
                is_active=bool(row[3]),
                buy_type=BuyType(row[4]),
                buy_amount_type=AmountType(row[5]),
                buy_amount=row[6],
                buy_slippage=row[7],
                sell_mode=SellMode(row[8]),
                sell_type=SellType(row[9]),
                sell_value=row[10],
                sell_slippage=row[11],
            )
            for row in rows
        ]
