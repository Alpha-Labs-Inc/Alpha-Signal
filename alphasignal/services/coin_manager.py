import asyncio
from datetime import datetime, timedelta, timezone
from typing import List
from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.coin import Coin
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


class CoinManager:
    def __init__(self):
        self.db = SQLiteDB()
        self.jupiter = JupiterClient()
        self.wallet = WalletManager()

    def get_tracked_coins(self) -> List[Coin]:
        active_coins = self.db.get_active_coins()

        return active_coins

    def add_coin(
        self,
        mint_address: str,
        sell_mode: SellMode,
        sell_value: float,
        sell_type: SellType,
        balance: float,
        token_value: float,
    ) -> str:
        """
        Add a coin to the tracked_coins table after verifying the wallet and fetching current price.

        Args:
            wallet_address (str): The Solana wallet address.
            mint_address (str): The mint address of the token.
            sell_mode (SellMode): The sell mode for the coin (e.g., time-based or stop-loss).
            sell_value (float): The sell value threshold.
            balance (float): Amount of the coin to be added.
            token_value: value of the token
        """

        id = self.db.create_coin(
            mint_address=mint_address,
            sell_mode=sell_mode,
            sell_value=sell_value,
            sell_type=sell_type,
            buy_in_value=token_value,
            balance=balance,
        )

        return id

    def remove_coin(self, id: str) -> None:
        """
        Removes the coin from being tracked

        Args:
            id: id of the coin
        """
        active_coins = self.db.get_active_coins()

        coin = next((c for c in active_coins if c.id == id), None)

        if not coin:
            raise TokenNotFoundError(f"No active coin found with Id '{id}'.")

        self.db.deactivate_coin(id)

    def get_remaining_trackable_balance(self, mint_address: str, total_balance: float):
        """
        Given the mint address and total balance of a token in a wallet returns how much is avalible to be left for tracking

        Args:
            mint_address: mint address of the token
            total_balance: total balance of the token in the wallet
        """
        used_balance = self.db.get_active_coin_balance_by_mint_address(mint_address)

        remaining_balance = total_balance - used_balance

        return remaining_balance

    async def process_coins(self) -> None:
        active_coins = self.db.get_active_coins()
        tasks = []

        for coin in active_coins:
            current_value = await self.jupiter.fetch_token_value(coin.mint_address)

            if coin.sell_mode == SellMode.TIME_BASED:
                elapsed_time = datetime.now(timezone.utc) - coin.time_purchased
                if elapsed_time >= timedelta(minutes=coin.sell_value):
                    self.db.deactivate_coin(coin.id)
                    print(f"Sell {coin.mint_address}: Time-based trigger reached.")
                    await self.sell_coin(coin)
                elif current_value > coin.last_price_max:
                    self.db.update_coin_last_price(coin.id, current_value)

            elif coin.sell_mode == SellMode.STOP_LOSS:
                if current_value > coin.last_price_max:
                    self.db.update_coin_last_price(coin.id, current_value)
                else:
                    decrease_percentage = (
                        (coin.last_price_max - current_value) / coin.last_price_max
                    ) * 100
                    print(decrease_percentage)
                    if decrease_percentage >= coin.sell_value:
                        print(
                            f"Sell condition detected for {coin.mint_address}: Starting monitoring..."
                        )
                        self.db.deactivate_coin(coin.id)
                        tasks.append(asyncio.create_task(self.determine_sell(coin)))

        # Wait for all stop-loss tasks to finish
        await asyncio.gather(*tasks)

    async def determine_sell(self, coin: Coin, interval: int = 10) -> None:
        """
        Monitor the coin's value for the given interval (in seconds) to confirm or cancel a sell decision.
        If the decrease percentage meets or exceeds the coin's sell_value consistently, finalize the sell.
        """
        decrease_threshold_met = True

        for _ in range(interval):
            current_value = await self.jupiter.fetch_token_value(coin.mint_address)
            decrease_percentage = (
                (coin.last_price_max - current_value) / coin.last_price_max
            ) * 100

            if decrease_percentage < coin.sell_value:
                print(
                    f"Sell condition not met for {coin.mint_address}: Decrease {decrease_percentage:.2f}%"
                )
                decrease_threshold_met = False
                break

            await asyncio.sleep(1)

        if decrease_threshold_met:
            await self.sell_coin(coin)
        else:
            print(
                f"Sell condition revoked for {coin.mint_address}. Reactivating tracking."
            )
            self.db.reactivate_coin(coin.id)  # Reactivate the coin

    async def sell_coin(self, coin: Coin):
        sell_address = None

        if coin.sell_type == SellType.SOL:
            sell_address = SOL_MINT_ADDRESS
        elif coin.sell_type == SellType.USDC:
            sell_address = USDC_MINT_ADDRESS

        # Try to sell the coin
        try:
            await self.jupiter.swap_tokens(
                coin.mint_address, sell_address, coin.balance, self.wallet.wallet
            )
        except Exception as e:
            print(f"There was an error selling {coin.id} reactivating tracking.")
            self.db.reactivate_coin(coin.id)
            raise e

        self.db.update_sell_time_sold(coin.id)
