from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.constants import (
    TYPE_TO_MINT,
)
from alphasignal.models.enums import AmountType, BuyType, Platform
from alphasignal.services.order_manager import OrderManager
from alphasignal.services.profile_manager import ProfileManager
from alphasignal.services.wallet_manager import WalletManager
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class AutoManager:
    def __init__(self):
        self.db = SQLiteDB()
        self.jupiter = JupiterClient()
        self.wallet_manager = WalletManager()
        self.orders = OrderManager()
        self.profiles = ProfileManager()
        self.solana_client = SolanaClient()

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

        tokens = await self.wallet_manager.get_tokens()

        # Determine the mint address for the selected buy type
        from_mint_address = TYPE_TO_MINT[profile.buy_type.value]
        if profile.buy_type == BuyType.SOL:
            token_balance = self.solana_client.get_sol_balance(
                self.wallet_manager.wallet
            )
        else:
            # Find balance of the required token
            token_balance = None
            for token in tokens:
                if token.mint_address == from_mint_address:
                    token_balance = token.balance
                    break
            if token_balance is None:
                raise Exception(
                    f"Token balance not found for mint address: {from_mint_address}"
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
            wallet_manager=self.wallet_manager,
            slippage_bps=profile.buy_slippage,
        )

        final_balance = float(f"{float(amount):.6f}")

        # Create an order using profile's sell configurations
        order_id = self.orders.add_order(
            mint_address=mint_address,
            sell_mode=profile.sell_mode,
            sell_value=profile.sell_value,
            sell_type=profile.sell_type,
            balance=final_balance,
            token_value=await self.jupiter.fetch_token_value(mint_address),
            slippage=profile.sell_slippage,
        )

        # Log order creation
        logger.info(
            f"Order created with ID: {order_id} and balance of: {final_balance}"
        )

        return order_id
