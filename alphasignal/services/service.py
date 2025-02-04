from typing import List
from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.order import Order
from alphasignal.models.enums import OrderStatus, SellMode, SellType
from alphasignal.schemas.responses.swap_confirmation_response import (
    SwapConfirmationResponse,
)
from alphasignal.models.token_value import TokenValue
from alphasignal.schemas.responses.wallet_value_response import WalletValueResponse
from alphasignal.services.order_manager import OrderManager
from alphasignal.services.token_manager import TokenManager
from alphasignal.services.wallet_manager import WalletManager


def create_wallet():
    wallet = WalletManager(True)
    return wallet


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


async def add_order_command() -> None:
    order_manager = OrderManager()
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
    remaining_balance = order_manager.get_remaining_trackable_balance(
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

    # Create the order in the database
    order_manager.add_order(
        mint_address=selected_token.mint_address,
        sell_mode=sell_mode,
        sell_value=sell_value,
        sell_type=sell_type,
        balance=tracking_balance,
        token_value=selected_token.value,
    )


def remove_order_command() -> None:
    order_manager = OrderManager()
    db = SQLiteDB()
    active_orders = db.get_orders(OrderStatus.ACTIVE)
    if not active_orders:
        print("No active orders to remove.")
        return

    print("\nActive Orders:")
    for idx, order in enumerate(active_orders, start=1):
        print(
            f"{idx}. Mint Address: {order.mint_address}, Balance: {order.balance}, Sell Mode: {order.sell_mode.value}"
        )

    try:
        choice = int(input("\nEnter the number of the order to remove: ")) - 1
        if choice < 0 or choice >= len(active_orders):
            print("Invalid choice. Aborting.")
            return

        selected_order = active_orders[choice]
        order_manager.cancel_order(selected_order.id)
    except ValueError:
        print("Invalid input. Please enter a valid number.")


def get_tracked_orders_command() -> List[Order]:
    order_manager = OrderManager()
    active_orders = order_manager.get_orders(OrderStatus.ACTIVE)

    print("\nActive Orders:")
    for idx, order in enumerate(active_orders, start=1):
        print(
            f"{idx}. Mint Address: {order.mint_address}, Balance: {order.balance}, Sell Mode: {order.sell_mode.value}, Sell Trigger Value: {order.sell_value}, Sell Type: {order.sell_type.value}, Last Max: {order.last_price_max}"
        )

    return active_orders


async def process_orders() -> None:
    order_manager = OrderManager()

    await order_manager.process_orders()


def initialize_database() -> None:
    db = SQLiteDB()

    db.initialize_database()
