import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
from alphasignal.commands.account import create_account
from alphasignal.commands.twitter import follow, unfollow
from alphasignal.commands.coin_manager import (
    add_coin_command,
    remove_coin_command,
    get_tracked_coins_command,
    process_coins,
)
from alphasignal.wallet.solana_wallet import create_solana_wallet
from alphasignal.wallet.transfer_solana import swap_tokens
from alphasignal.database.db import (
    calculate_remaining_balance,
    create_coin,
    deactivate_coin,
    get_active_coins,
    update_coin_last_price,
)
from alphasignal.modles.enums import SellMode


def run_in_async(func, *args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func(*args))


def print_status(message):
    print(message)


def create_account_gui(account_name):
    if not account_name.strip():
        print_status("Error: Account name cannot be empty.")
        return
    try:
        create_account(account_name)
        print_status(f"Account '{account_name}' created successfully.")
    except Exception as e:
        print_status(f"Error: Failed to create account: {e}")


def follow_user_gui(handle):
    if not handle.strip():
        print_status("Error: Twitter handle cannot be empty.")
        return
    try:
        follow(handle)
        print_status(f"Now following {handle}.")
    except Exception as e:
        print_status(f"Error: Failed to follow {handle}: {e}")


def unfollow_user_gui(handle):
    if not handle.strip():
        print_status("Error: Twitter handle cannot be empty.")
        return
    try:
        unfollow(handle)
        print_status(f"Unfollowed {handle} successfully.")
    except Exception as e:
        print_status(f"Error: Failed to unfollow {handle}: {e}")


def add_coin_gui():
    def on_confirm():
        selected_token = token_choice_var.get()
        tracking_option = tracking_choice_var.get()
        sell_mode_option = sell_mode_choice_var.get()

        try:
            tracking_balance = float(tracking_amount_entry.get())
            sell_value = float(sell_value_entry.get())

            # Validate inputs
            if not selected_token:
                print_status("Error: No token selected.")
                return
            if tracking_balance <= 0:
                print_status("Error: Tracking balance must be greater than 0.")
                return
            if sell_value <= 0:
                print_status("Error: Sell value must be greater than 0.")
                return

            # Add coin logic (dummy implementation for now)
            print_status(
                f"Token: {selected_token}, Tracking: {tracking_balance}, Sell Mode: {sell_mode_option}, Sell Value: {sell_value}"
            )
            messagebox.showinfo(
                "Success", f"Coin '{selected_token}' added successfully."
            )
        except ValueError:
            print_status(
                "Error: Invalid numeric values for tracking balance or sell value."
            )

    # Dummy tokens for selection (replace with actual wallet tokens)
    tokens = ["Token A", "Token B", "Token C"]

    # Create a popup window
    add_coin_window = tk.Toplevel()
    add_coin_window.title("Add Coin")

    ttk.Label(add_coin_window, text="Select a token:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    token_choice_var = tk.StringVar()
    token_dropdown = ttk.Combobox(
        add_coin_window, textvariable=token_choice_var, values=tokens, state="readonly"
    )
    token_dropdown.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(add_coin_window, text="Tracking Amount:").grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )
    tracking_amount_entry = ttk.Entry(add_coin_window)
    tracking_amount_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(add_coin_window, text="Tracking Option:").grid(
        row=2, column=0, padx=5, pady=5, sticky="w"
    )
    tracking_choice_var = tk.StringVar(value="Percentage")
    ttk.Radiobutton(
        add_coin_window,
        text="Percentage",
        variable=tracking_choice_var,
        value="Percentage",
    ).grid(row=2, column=1, sticky="w")
    ttk.Radiobutton(
        add_coin_window,
        text="Custom Amount",
        variable=tracking_choice_var,
        value="Custom Amount",
    ).grid(row=2, column=2, sticky="w")

    ttk.Label(add_coin_window, text="Sell Mode:").grid(
        row=3, column=0, padx=5, pady=5, sticky="w"
    )
    sell_mode_choice_var = tk.StringVar(value="Time-based")
    ttk.Radiobutton(
        add_coin_window,
        text="Time-based",
        variable=sell_mode_choice_var,
        value="Time-based",
    ).grid(row=3, column=1, sticky="w")
    ttk.Radiobutton(
        add_coin_window,
        text="Stop-loss",
        variable=sell_mode_choice_var,
        value="Stop-loss",
    ).grid(row=3, column=2, sticky="w")

    ttk.Label(add_coin_window, text="Sell Value:").grid(
        row=4, column=0, padx=5, pady=5, sticky="w"
    )
    sell_value_entry = ttk.Entry(add_coin_window)
    sell_value_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Button(add_coin_window, text="Add Coin", command=on_confirm).grid(
        row=5, column=0, columnspan=3, pady=10
    )


def remove_coin_gui():
    try:
        remove_coin_command()
        print_status("Coin removed successfully.")
    except Exception as e:
        print_status(f"Error: Failed to remove coin: {e}")


def process_coins_gui():
    try:
        run_in_async(process_coins)
        print_status("Coins processed successfully.")
    except Exception as e:
        print_status(f"Error: Failed to process coins: {e}")


def create_wallet_gui():
    try:
        run_in_async(create_solana_wallet)
        print_status("Wallet created successfully.")
    except Exception as e:
        print_status(f"Error: Failed to create wallet: {e}")


def swap_tokens_gui(from_token, to_token, amount):
    try:
        run_in_async(swap_tokens, from_token, to_token, float(amount))
        print_status(f"Swapped {amount} of {from_token} to {to_token}.")
    except Exception as e:
        print_status(f"Error: Failed to swap tokens: {e}")


def main_gui():
    root = tk.Tk()
    root.title("AlphaSignal Settings")

    # Settings Menu Layout
    ttk.Label(root, text="AlphaSignal Settings", font=("Arial", 16)).pack(pady=10)

    # Account Section
    account_frame = ttk.LabelFrame(root, text="Account Settings", padding=(10, 10))
    account_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(account_frame, text="Account Name:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    account_name_entry = ttk.Entry(account_frame)
    account_name_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(
        account_frame,
        text="Create Account",
        command=lambda: create_account_gui(account_name_entry.get()),
    ).grid(row=0, column=2, padx=5, pady=5)

    # Twitter Section
    twitter_frame = ttk.LabelFrame(root, text="Twitter Settings", padding=(10, 10))
    twitter_frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(twitter_frame, text="Twitter Handle:").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    twitter_handle_entry = ttk.Entry(twitter_frame)
    twitter_handle_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(
        twitter_frame,
        text="Follow",
        command=lambda: follow_user_gui(twitter_handle_entry.get()),
    ).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(
        twitter_frame,
        text="Unfollow",
        command=lambda: unfollow_user_gui(twitter_handle_entry.get()),
    ).grid(row=0, column=3, padx=5, pady=5)

    # Wallet Section
    wallet_frame = ttk.LabelFrame(root, text="Wallet Settings", padding=(10, 10))
    wallet_frame.pack(fill="x", padx=10, pady=5)

    ttk.Button(wallet_frame, text="Create Wallet", command=create_wallet_gui).grid(
        row=0, column=0, padx=5, pady=5
    )

    ttk.Label(wallet_frame, text="Swap Tokens:").grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )
    ttk.Label(wallet_frame, text="From Token:").grid(
        row=2, column=0, padx=5, pady=5, sticky="w"
    )
    from_token_entry = ttk.Entry(wallet_frame)
    from_token_entry.grid(row=2, column=1, padx=5, pady=5)
    ttk.Label(wallet_frame, text="To Token:").grid(
        row=3, column=0, padx=5, pady=5, sticky="w"
    )
    to_token_entry = ttk.Entry(wallet_frame)
    to_token_entry.grid(row=3, column=1, padx=5, pady=5)
    ttk.Label(wallet_frame, text="Amount:").grid(
        row=4, column=0, padx=5, pady=5, sticky="w"
    )
    amount_entry = ttk.Entry(wallet_frame)
    amount_entry.grid(row=4, column=1, padx=5, pady=5)
    ttk.Button(
        wallet_frame,
        text="Swap",
        command=lambda: swap_tokens_gui(
            from_token_entry.get(), to_token_entry.get(), amount_entry.get()
        ),
    ).grid(row=5, column=0, columnspan=2, pady=5)

    # Coins Section
    coins_frame = ttk.LabelFrame(root, text="Coins Settings", padding=(10, 10))
    coins_frame.pack(fill="x", padx=10, pady=5)

    ttk.Button(coins_frame, text="Add Coin", command=add_coin_gui).grid(
        row=0, column=0, padx=5, pady=5
    )
    ttk.Button(coins_frame, text="Remove Coin", command=remove_coin_gui).grid(
        row=0, column=1, padx=5, pady=5
    )
    ttk.Button(coins_frame, text="Process Coins", command=process_coins_gui).grid(
        row=0, column=2, padx=5, pady=5
    )

    root.mainloop()


if __name__ == "__main__":
    main_gui()
