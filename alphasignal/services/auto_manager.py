from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.configs import AutoBuyConfig, AutoSellConfig
from alphasignal.models.constants import (
    AUTO_BUY_CONFIG_PATH,
    AUTO_SELL_CONFIG_PATH,
    TYPE_TO_MINT,
)
from alphasignal.models.enums import AmountType
from alphasignal.services.order_manager import OrderManager
from alphasignal.services.wallet_manager import WalletManager
from alphasignal.utils.utils import load_config


class AutoManager:
    def __init__(self):
        self.db = SQLiteDB()
        self.jupiter = JupiterClient()
        self.wallet = WalletManager()
        self.orders = OrderManager()

    async def auto_buy(
        self,
        mint_address: str,
    ) -> str:
        """
        Logic to auto buy a coin from a mint address

        Args:
            mint_address (str): The mint address of the token.
        """

        buy_config = load_config(AUTO_BUY_CONFIG_PATH, AutoBuyConfig)
        sell_config = load_config(AUTO_SELL_CONFIG_PATH, AutoSellConfig)

        tokens = await self.wallet.get_tokens()

        # Get the mint address for the selected buy type
        from_mint_address = TYPE_TO_MINT[buy_config.buy_type.value]

        # Find balance of the required token
        token_balance = next(
            (t.balance for t in tokens if t.mint_address == mint_address), 0
        )
        swap_balance = 0

        if buy_config.amount_type == AmountType.AMOUNT:
            # Ensure we have enough balance
            if token_balance < buy_config.amount:
                raise Exception(
                    f"Insufficient balance: {token_balance} available, {buy_config.amount} required."
                )
            else:
                swap_balance = buy_config.amount

        elif buy_config.amount_type == AmountType.PERCENT:
            # Calculate swap amount based on balance percentage
            swap_balance = token_balance * (buy_config.amount / 100)

        amount = await self.jupiter.swap_tokens(
            from_token_mint=from_mint_address,
            to_token_mint=mint_address,
            input_amount=swap_balance,
            wallet=self.wallet,
            slippage_bps=buy_config.slippage,
        )

        final_balance = 0 if amount is None else float(amount)

        # Need to get the balance of the swap we got back

        order_id = self.orders.add_order(
            mint_address=mint_address,
            sell_mode=sell_config.sell_mode,
            sell_value=sell_config.sell_value,
            sell_type=sell_config.sell_type,
            balance=final_balance,
            token_value=self.jupiter.fetch_token_value(mint_address),
            slippage=sell_config.slippage,
        )

        return order_id
