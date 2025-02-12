from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.constants import (
    TYPE_TO_MINT,
)
from alphasignal.models.enums import AmountType, Platform
from alphasignal.services.order_manager import OrderManager
from alphasignal.services.profile_manager import ProfileManager
from alphasignal.services.wallet_manager import WalletManager


class AutoManager:
    def __init__(self):
        self.db = SQLiteDB()
        self.jupiter = JupiterClient()
        self.wallet = WalletManager()
        self.orders = OrderManager()
        self.profiles = ProfileManager()

    async def auto_buy(
        self,
        mint_address: str,
        platform: Platform,
        username: str,
    ) -> str | None:
        """
        Auto buy a token using the profile settings.

        Args:
            mint_address (str): The mint address of the token.
            platform (str): The platform associated with the username.
            username (str): The trading username.
        """

        # Retrieve profile based on platform and username
        profile = self.profiles.get_profile(platform.value, username)

        if profile is None:
            raise Exception(
                f"No profile found for platform '{platform.value}' and username '{username}'."
            )

        if not profile.is_active:
            return None

        tokens = await self.wallet.get_tokens()

        # Determine the mint address for the selected buy type
        from_mint_address = TYPE_TO_MINT[profile.buy_type.value]

        # Find balance of the required token
        token_balance = next(
            (t.balance for t in tokens if t.mint_address == from_mint_address), 0
        )

        swap_balance = 0

        if profile.buy_amount_type == AmountType.AMOUNT:
            # Ensure sufficient balance
            if token_balance < profile.buy_amount:
                raise Exception(
                    f"Insufficient balance: {token_balance} available, {profile.buy_amount} required."
                )
            else:
                swap_balance = profile.buy_amount

        elif profile.buy_amount_type == AmountType.PERCENT:
            # Calculate swap amount based on balance percentage
            swap_balance = token_balance * (profile.buy_amount / 100)

        amount = await self.jupiter.swap_tokens(
            from_token_mint=from_mint_address,
            to_token_mint=mint_address,
            input_amount=swap_balance,
            wallet=self.wallet,
            slippage_bps=profile.buy_slippage,
        )

        final_balance = 0 if amount is None else float(amount)

        # Create an order using profile's sell configurations
        order_id = self.orders.add_order(
            mint_address=mint_address,
            sell_mode=profile.sell_mode,
            sell_value=profile.sell_value,
            sell_type=profile.sell_type,
            balance=final_balance,
            token_value=self.jupiter.fetch_token_value(mint_address),
            slippage=profile.sell_slippage,
        )

        return order_id
