from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.wallet_token import WalletToken
from alphasignal.schemas.responses.swap_confirmation_response import (
    SwapConfirmationResponse,
)
from alphasignal.models.token_value import TokenValue
from alphasignal.schemas.responses.wallet_value_response import WalletValueResponse
from alphasignal.services.wallet_manager import WalletManager

import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def create_wallet():
    wallet = WalletManager(True)
    return wallet


async def retrieve_sol_value(wallet: WalletManager) -> WalletToken:
    sol_value = await wallet.get_sol_value()
    return sol_value


async def retrieve_wallet_value(wallet: WalletManager) -> WalletValueResponse:
    wallet_value = await wallet.get_wallet_value()
    return wallet_value


async def fund(amt, wallet, funding_key):
    try:
        in_amt = float(amt)
    except Exception as e:
        raise Exception("In amount must be float.")
    solana_client = SolanaClient()
    return await solana_client.fund_wallet(
        wallet.wallet.public_key, in_amt, funding_key
    )


def load_wallet():
    return WalletManager()


async def get_token_value(token_mint_address):
    client = JupiterClient()
    price = await client.fetch_token_value(token_mint_address)
    return TokenValue(token_mint_address=token_mint_address, price=price)


async def get_swap_quote(from_token, to_token, amt):
    client = JupiterClient()
    # Gets a quote output pydantic object
    quote = await client.create_quote(from_token, to_token, amt)
    return quote


async def swap_tokens(from_token, to_token, amt, wallet):
    client = JupiterClient()

    amount = await client.swap_tokens(from_token, to_token, amt, wallet.wallet)
    return SwapConfirmationResponse(
        from_token_mint_address=from_token,
        to_token_mint_address=to_token,
        amount=amount,
    )


def initialize_database() -> None:
    db = SQLiteDB()

    db.initialize_database()
