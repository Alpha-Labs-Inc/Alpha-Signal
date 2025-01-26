from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.services.token_manager import TokenManager
from alphasignal.services.wallet_manager import WalletManager


def create_wallet():
    wallet = WalletManager(True)
    return True


async def get_wallet_value():
    wallet = WalletManager()
    await wallet.get_wallet_value()


async def get_token_value(token_mint_address):
    client = JupiterClient()
    price = await client.fetch_token_value(token_mint_address)
    print(f"Price for {token_mint_address}: ${price}")


async def get_swap_quote(from_token, to_token, amt):
    client = JupiterClient()
    await client.create_quote(from_token, to_token, amt)


async def swap_tokens(from_token, to_token, amt):
    client = JupiterClient()
    wallet_client = WalletManager()

    await client.swap_tokens(from_token, to_token, amt, wallet_client.wallet)
    return True
