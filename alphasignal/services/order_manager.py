import asyncio
from datetime import datetime, timedelta, timezone
from typing import List
from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.order import Order
from alphasignal.models.constants import SOL_MINT_ADDRESS, USDC_MINT_ADDRESS
from alphasignal.models.enums import SellMode, SellType
from alphasignal.models.wallet_token import WalletToken
from alphasignal.services.wallet_manager import WalletManager


class TokenNotFoundError(Exception):
    """Custom exception for when a token is not found in the wallet."""

    pass


class TokenBalanceNotAvalible(Exception):
    """Custom exception for when a token does not have enough balance to be tracked."""

    pass


class OrderManager:
    def __init__(self):
        self.db = SQLiteDB()
        self.jupiter = JupiterClient()
        self.wallet = WalletManager()

    def get_tracked_orders(self) -> List[Order]:
        active_orders = self.db.get_active_orders()

        return active_orders

    def add_order(
        self,
        mint_address: str,
        sell_mode: SellMode,
        sell_value: float,
        sell_type: SellType,
        balance: float,
        token_value: float,
    ) -> str:
        """
        Add a order to the tracked_orders table after verifying the wallet and fetching current price.

        Args:
            wallet_address (str): The Solana wallet address.
            mint_address (str): The mint address of the token.
            sell_mode (SellMode): The sell mode for the order (e.g., time-based or stop-loss).
            sell_value (float): The sell value threshold.
            balance (float): Amount of the order to be added.
            token_value: value of the token
        """

        id = self.db.create_order(
            mint_address=mint_address,
            sell_mode=sell_mode,
            sell_value=sell_value,
            sell_type=sell_type,
            buy_in_value=token_value,
            balance=balance,
        )

        return id

    def remove_order(self, id: str) -> None:
        """
        Removes the order from being tracked

        Args:
            id: id of the order
        """
        active_orders = self.db.get_active_orders()

        order = next((c for c in active_orders if c.id == id), None)

        if not order:
            raise TokenNotFoundError(f"No active order found with Id '{id}'.")

        self.db.deactivate_order(id)

    def get_remaining_trackable_balance(self, mint_address: str, total_balance: float):
        """
        Given the mint address and total balance of a token in a wallet returns how much is avalible to be left for tracking

        Args:
            mint_address: mint address of the token
            total_balance: total balance of the token in the wallet
        """
        used_balance = self.db.get_active_order_balance_by_mint_address(mint_address)

        remaining_balance = total_balance - used_balance

        return remaining_balance

    async def process_orders(self) -> None:
        active_orders = self.db.get_active_orders()
        tasks = []

        for order in active_orders:
            current_value = await self.jupiter.fetch_token_value(order.mint_address)

            if order.sell_mode == SellMode.TIME_BASED:
                elapsed_time = datetime.now(timezone.utc) - order.time_purchased
                if elapsed_time >= timedelta(minutes=order.sell_value):
                    self.db.deactivate_order(order.id)
                    print(f"Sell {order.mint_address}: Time-based trigger reached.")
                    await self.sell_order(order)
                elif current_value > order.last_price_max:
                    self.db.update_order_last_price(order.id, current_value)

            elif order.sell_mode == SellMode.STOP_LOSS:
                if current_value > order.last_price_max:
                    self.db.update_order_last_price(order.id, current_value)
                else:
                    decrease_percentage = (
                        (order.last_price_max - current_value) / order.last_price_max
                    ) * 100
                    print(decrease_percentage)
                    if decrease_percentage >= order.sell_value:
                        print(
                            f"Sell condition detected for {order.mint_address}: Starting monitoring..."
                        )
                        self.db.deactivate_order(order.id)
                        tasks.append(asyncio.create_task(self.determine_sell(order)))

        # Wait for all stop-loss tasks to finish
        await asyncio.gather(*tasks)

    async def determine_sell(self, order: Order, interval: int = 10) -> None:
        """
        Monitor the order's value for the given interval (in seconds) to confirm or cancel a sell decision.
        If the decrease percentage meets or exceeds the order's sell_value consistently, finalize the sell.
        """
        decrease_threshold_met = True

        for _ in range(interval):
            current_value = await self.jupiter.fetch_token_value(order.mint_address)
            decrease_percentage = (
                (order.last_price_max - current_value) / order.last_price_max
            ) * 100

            if decrease_percentage < order.sell_value:
                print(
                    f"Sell condition not met for {order.mint_address}: Decrease {decrease_percentage:.2f}%"
                )
                decrease_threshold_met = False
                break

            await asyncio.sleep(1)

        if decrease_threshold_met:
            await self.sell_order(order)
        else:
            print(
                f"Sell condition revoked for {order.mint_address}. Reactivating tracking."
            )
            self.db.reactivate_order(order.id)  # Reactivate the order

    async def sell_order(self, order: Order):
        sell_address = None

        if order.sell_type == SellType.SOL:
            sell_address = SOL_MINT_ADDRESS
        elif order.sell_type == SellType.USDC:
            sell_address = USDC_MINT_ADDRESS

        # Try to sell the order
        try:
            await self.jupiter.swap_tokens(
                order.mint_address, sell_address, order.balance, self.wallet.wallet
            )
        except Exception as e:
            print(f"There was an error selling {order.id} reactivating tracking.")
            self.db.reactivate_order(order.id)
            raise e

        self.db.update_sell_time_sold(order.id)
