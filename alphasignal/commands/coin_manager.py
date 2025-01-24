from datetime import datetime, timedelta, timezone
from typing import List
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey

from alphasignal.database.db import create_coin, get_active_coins, update_coin_last_price
from alphasignal.modles.enums import SellMode
from alphasignal.modles.wallet_token import WalletToken

import requests

class CoinNotFoundError(Exception):
    """Custom exception for when a token is not found in the wallet."""
    pass

def fetch_coin_value(mint_address: str) -> float:
    """
    Fetch the current value of a coin in USD from the Jupiter API.

    Args:
        mint_address (str): The mint address of the token.

    Returns:
        float: The current value of the token in USD.
    """
    if(mint_address == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"):
        return 1
    
    url = f"https://quote-api.jup.ag/v6/quote?inputMint={mint_address}&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=10000"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = int(data["outAmount"])/10000.0
        return price
    raise ValueError(f"Unable to fetch price for mint address: {mint_address}")

def add_coin(
    wallet_address: str,
    mint_address: str,
    sell_mode: SellMode,
    sell_value: float
) -> None:
    """
    Add a coin to the tracked_coins table after verifying the wallet and fetching current price.

    Args:
        wallet_address (str): The Solana wallet address.
        mint_address (str): The mint address of the token.
        sell_mode (SellMode): The sell mode for the coin (e.g., time-based or stop-loss).
        sell_value (float): The sell value threshold.

    Raises:
        CoinNotFoundError: If the token is not found in the user's wallet.
    """
    # Step 1: Check if the wallet contains the token
    tokens = get_wallet_tokens(wallet_address)
    token = next((t for t in tokens if t.mint_address == mint_address), None)

    if not token:
        raise CoinNotFoundError(f"Token with mint address '{mint_address}' not found in wallet '{wallet_address}'.")

    # Step 3: Add the coin to the database
    create_coin(
        mint_address=mint_address,
        sell_mode=sell_mode,
        sell_value=sell_value,
        buy_in_value=token.value
    )

def get_wallet_tokens(wallet_address: str) -> List[WalletToken]:
    """
    Fetch the tokens in a Solana wallet and return them as Pydantic models, including token names if available.

    Args:
        wallet_address (str): The Solana wallet address.

    Returns:
        List[WalletToken]: A list of tokens with their mint addresses, balances, and names.
    """
    client = Client("https://api.mainnet-beta.solana.com")  # Solana RPC endpoint
    opts = TokenAccountOpts(program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
    key = Pubkey.from_string(wallet_address)
    response = client.get_token_accounts_by_owner_json_parsed(key, opts)
    if not response.value:
        return []

    tokens = []
    for token_info in response.value:
        mint_address = token_info.account.data.parsed["info"]["mint"]
        balance = token_info.account.data.parsed["info"]["tokenAmount"]["uiAmount"]
        value = fetch_coin_value(mint_address)
        tokens.append(WalletToken(mint_address=mint_address, balance=balance, token_name="", value=value))
    
    return tokens


def process_coins() -> None:
    active_coins = get_active_coins()
    for coin in active_coins:
        current_value = fetch_coin_value(coin.mint_address)

        if coin.sell_mode == SellMode.TIME_BASED:
            elapsed_time = datetime.now(timezone.utc) - coin.time_purchased
            if elapsed_time >= timedelta(minutes=coin.sell_value):
                print(f"Sell {coin.mint_address}: Time-based trigger reached.")
            elif current_value > coin.last_price_max:
                update_coin_last_price(coin.id, current_value)

        elif coin.sell_mode == SellMode.STOP_LOSS:
            if current_value > coin.last_price_max:
                update_coin_last_price(coin.id, current_value)
            else:
                decrease_percentage = ((coin.last_price_max - current_value) / coin.last_price_max) * 100
                if decrease_percentage >= coin.sell_value:
                    print(f"Sell {coin.mint_address}: Stop-loss trigger reached.")

def sell(mint_address):
    print(f"Coin with mint address '{mint_address}' sold.")