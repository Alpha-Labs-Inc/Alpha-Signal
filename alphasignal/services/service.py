from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.services.token_manager import TokenManager
from alphasignal.services.wallet_manager import WalletManager


def create_wallet():
    wallet = WalletManager(True)
    return wallet


async def get_wallet_value(wallet):
    await wallet.get_wallet_value()


def load_wallet():
    return WalletManager()


async def get_token_value(token_mint_address):
    client = JupiterClient()
    price = await client.fetch_token_value(token_mint_address)
    print(f"Price for {token_mint_address}: ${price}")


async def get_swap_quote(from_token, to_token, amt):
    client = JupiterClient()
    await client.create_quote(from_token, to_token, amt)


async def swap_tokens(from_token, to_token, amt, wallet):
    client = JupiterClient()

    await client.swap_tokens(from_token, to_token, amt, wallet.wallet)
    return True
