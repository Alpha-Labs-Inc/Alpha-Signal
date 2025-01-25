from datetime import datetime, timedelta, timezone
from typing import List
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey

import asyncio
from alphasignal.commands.wallet import load_wallet_address
from alphasignal.database.db import calculate_remaining_balance, create_coin, deactivate_coin, get_active_coins, reactivate_coin, update_coin_last_price
from alphasignal.modles.coin import Coin
from alphasignal.modles.constants import USDC_MINT_ADDRESS
from alphasignal.modles.enums import SellMode
from alphasignal.modles.wallet_token import WalletToken

import requests

def get_tokens_command() -> None:
    wallet_address = load_wallet_address()
    tokens = get_wallet_tokens(wallet_address)
    total_value = 0.0
    if not tokens:
        print("No tokens found in the wallet.")
        return

    print("\nTokens in your wallet:")
    for token in tokens:
        wallet_value = token.balance * token.value
        total_value += wallet_value
        print(f"- Name: {token.token_name}, Mint Address: {token.mint_address}, Value (USD): ${token.value:.2f}, Balance: {token.balance}, Total Value: {wallet_value:.2f}")
    print(f"Total Value: ${total_value:.2f}")


def add_coin_command() -> None:
    wallet_address = load_wallet_address()

    # Fetch available tokens
    tokens = get_wallet_tokens(wallet_address)
    if not tokens:
        print("No tokens found in the wallet.")
        return

    print("Available tokens:")
    for idx, token in enumerate(tokens, start=1):
        print(f"{idx}. {token.token_name} (Mint Address: {token.mint_address}, Balance: {token.balance})")

    # Let user select a token
    try:
        token_choice = int(input("Select a token by number: ")) - 1
        if token_choice < 0 or token_choice >= len(tokens):
            print("Invalid choice. Please try again.")
            return
        selected_token = tokens[token_choice]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    # Calculate remaining balance for the selected token
    remaining_balance = calculate_remaining_balance(selected_token.mint_address, selected_token.balance)
    print(f"Remaining balance available for tracking: {remaining_balance}")

    if remaining_balance <= 0:
        print("No balance available for tracking this token.")
        return

    # Ask user for the tracking amount
    print("Enter the tracking amount:")
    print("1. Percentage of the remaining balance")
    print("2. Custom balance amount")

    try:
        tracking_choice = int(input("Your choice (1 or 2): "))
        if tracking_choice == 1:
            tracking_percentage = float(input("Enter percentage (e.g., 50 for 50%): "))
            tracking_balance = (tracking_percentage / 100) * remaining_balance
        elif tracking_choice == 2:
            tracking_balance = float(input("Enter custom balance amount: "))
        else:
            print("Invalid choice. Please try again.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    if tracking_balance > remaining_balance:
        print("Tracking amount exceeds available balance. Please try again.")
        return

    # Ask user for the sell mode
    print("Select sell mode:")
    print("1. Time-based (Interval in minutes)")
    print("2. Stop-loss (Percentage drop)")

    try:
        sell_mode_choice = int(input("Your choice (1 or 2): "))
        if sell_mode_choice == 1:
            sell_mode = SellMode.TIME_BASED
            sell_value = float(input("Enter interval in minutes: "))
        elif sell_mode_choice == 2:
            sell_mode = SellMode.STOP_LOSS
            sell_value = float(input("Enter percentage drop (e.g., 10 for 10%): "))
        else:
            print("Invalid choice. Please try again.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    # Create the coin in the database
    create_coin(
        mint_address=selected_token.mint_address,
        sell_mode=sell_mode,
        sell_value=sell_value,
        buy_in_value=selected_token.value,
        balance=tracking_balance
    )

def remove_coin_command() -> None:
    active_coins = get_active_coins()
    if not active_coins:
        print("No active coins to remove.")
        return

    print("\nActive Coins:")
    for idx, coin in enumerate(active_coins, start=1):
        print(f"{idx}. Mint Address: {coin.mint_address}, Balance: {coin.balance}, Sell Mode: {coin.sell_mode.value}")

    try:
        choice = int(input("\nEnter the number of the coin to remove: ")) - 1
        if choice < 0 or choice >= len(active_coins):
            print("Invalid choice. Aborting.")
            return

        selected_coin = active_coins[choice]
        deactivate_coin(selected_coin.id)
    except ValueError:
        print("Invalid input. Please enter a valid number.")

def get_tracked_coins_command() -> None:
    active_coins = get_active_coins()
    if not active_coins:
        print("No active coins to remove.")
        return

    print("\nActive Coins:")
    for idx, coin in enumerate(active_coins, start=1):
        print(f"{idx}. Mint Address: {coin.mint_address}, Balance: {coin.balance}, Sell Mode: {coin.sell_mode.value}, Sell Trigger Value: {coin.sell_value}, Last Max: {coin.last_price_max}")

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
    if(mint_address == USDC_MINT_ADDRESS):
        return 1
    
    url = f"https://quote-api.jup.ag/v6/quote?inputMint={mint_address}&outputMint={USDC_MINT_ADDRESS}&amount=10000" # Need to integrate with the decimal of the coin
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
    sell_value: float,
    balance: float
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
        buy_in_value=token.value,
        balance=balance
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


async def process_coins() -> None:
    active_coins = get_active_coins()
    tasks = []

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
                    print(f"Sell condition detected for {coin.mint_address}: Starting monitoring...")
                    deactivate_coin(coin.id)
                    tasks.append(asyncio.create_task(determine_sell(coin)))
    
    # Wait for all stop-loss tasks to finish
    await asyncio.gather(*tasks)

async def determine_sell(coin: Coin, interval: int = 10) -> None:
    """
    Monitor the coin's value for the given interval (in seconds) to confirm or cancel a sell decision.
    If the decrease percentage meets or exceeds the coin's sell_value consistently, finalize the sell.
    """
    decrease_threshold_met = True
    for _ in range(interval):
        current_value = fetch_coin_value(coin.mint_address)
        decrease_percentage = ((coin.last_price_max - current_value) / coin.last_price_max) * 100

        if decrease_percentage < coin.sell_value:
            print(f"Sell condition not met for {coin.mint_address}: Decrease {decrease_percentage:.2f}%")
            decrease_threshold_met = False
            break

        await asyncio.sleep(1)

    if decrease_threshold_met:
        print(f"Final sell decision for {coin.mint_address}: Sell confirmed.")
    else:
        print(f"Sell condition revoked for {coin.mint_address}. Reactivating tracking.")
        reactivate_coin(coin.id)  # Reactivate the coin

def sell(mint_address):
    print(f"Coin with mint address '{mint_address}' sold.")

