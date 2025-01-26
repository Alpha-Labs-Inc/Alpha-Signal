from typing import List
from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.coin import Coin
from alphasignal.models.enums import SellMode, SellType
from alphasignal.models.swap_confirmation import SwapConfirmation
from alphasignal.models.token_value import TokenValue
from alphasignal.services.coin_manager import CoinManager
from alphasignal.services.token_manager import TokenManager
from alphasignal.services.wallet_manager import WalletManager


def create_wallet():
    wallet = WalletManager(True)
    return wallet


async def get_wallet_value(wallet):
    await wallet.get_wallet_value()


async def fund(amt, wallet):
    try:
        in_amt = float(amt)
    except Exception as e:
        print("In amount must be float.")
        return
    solana_client = SolanaClient()
    await solana_client.fund_wallet(wallet.wallet.public_key, in_amt)
    print("Funded wallet.")


def load_wallet():
    return WalletManager()


async def get_token_value(token_mint_address):
    client = JupiterClient()
    price = await client.fetch_token_value(token_mint_address)
    print(f"Price for {token_mint_address}: ${price}")
    return TokenValue(token_mint_address=token_mint_address, price=price)


async def get_swap_quote(from_token, to_token, amt):
    client = JupiterClient()
    # Gets a quote output pydantic object
    quote = client.create_quote(from_token, to_token, amt)

    # Display the quote details
    print("Quote details:")
    print(
        f"- Input: {quote.from_token_amt:.6f} tokens (~${quote.from_token_amt_usd:.2f})"
    )
    print(f"- Output: {quote.to_token_amt:.6f} tokens (~${quote.to_token_amt_usd:.2f})")
    print(f"- Conversion Rate: {quote.conversion_rate:.6f} tokens per input token")
    print(
        f"- Price Impact: {quote.price_impact * 100:.4f}% (~${quote.price_impact_usd:.2f})"
    )
    print(f"- Slippage Tolerance: {quote.slippage_bps / 100:.2f}%")
    return quote


async def swap_tokens(from_token, to_token, amt, wallet):
    client = JupiterClient()

    transaction_signature = await client.swap_tokens(
        from_token, to_token, amt, wallet.wallet
    )
    return SwapConfirmation(
        from_token_mint_address=from_token,
        to_token_mint_address=to_token,
        transaction_simulator=transaction_signature,
    )


async def add_coin_command() -> None:
    coin_manager = CoinManager()
    wallet_manager = WalletManager()

    # Fetch available tokens
    tokens = await wallet_manager.get_tokens()
    if not tokens:
        print("No tokens found in the wallet.")
        return

    print("Available tokens:")
    for idx, token in enumerate(tokens, start=1):
        print(
            f"{idx}. {token.token_name} (Mint Address: {token.mint_address}, Balance: {token.balance})"
        )

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
    remaining_balance = coin_manager.get_remaining_trackable_balance(
        selected_token.mint_address, selected_token.balance
    )
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

    print("Select type mode:")
    print("1. USDC")
    print("2. SOL")

    try:
        sell_type_choice = int(input("Your choice (1 or 2): "))
        if sell_type_choice == 1:
            sell_type = SellType.USDC
        elif sell_type_choice == 2:
            sell_type = SellType.SOL
        else:
            print("Invalid choice. Please try again.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    # Create the coin in the database
    coin_manager.add_coin(
        mint_address=selected_token.mint_address,
        sell_mode=sell_mode,
        sell_value=sell_value,
        sell_type=sell_type,
        balance=tracking_balance,
        tokens=tokens,
    )


def remove_coin_command() -> None:
    coin_manager = CoinManager()
    db = SQLiteDB()
    active_coins = db.get_active_coins()
    if not active_coins:
        print("No active coins to remove.")
        return

    print("\nActive Coins:")
    for idx, coin in enumerate(active_coins, start=1):
        print(
            f"{idx}. Mint Address: {coin.mint_address}, Balance: {coin.balance}, Sell Mode: {coin.sell_mode.value}"
        )

    try:
        choice = int(input("\nEnter the number of the coin to remove: ")) - 1
        if choice < 0 or choice >= len(active_coins):
            print("Invalid choice. Aborting.")
            return

        selected_coin = active_coins[choice]
        coin_manager.remove_coin(selected_coin.id)
    except ValueError:
        print("Invalid input. Please enter a valid number.")


def get_tracked_coins_command() -> List[Coin]:
    coin_manager = CoinManager()
    active_coins = coin_manager.get_tracked_coins()

    print("\nActive Coins:")
    for idx, coin in enumerate(active_coins, start=1):
        print(
            f"{idx}. Mint Address: {coin.mint_address}, Balance: {coin.balance}, Sell Mode: {coin.sell_mode.value}, Sell Trigger Value: {coin.sell_value}, Sell Type: {coin.sell_type.value}, Last Max: {coin.last_price_max}"
        )


async def process_coins() -> None:
    coin_manager = CoinManager()

    await coin_manager.process_coins()


def initialize_database() -> None:
    db = SQLiteDB()

    db.initialize_database()
