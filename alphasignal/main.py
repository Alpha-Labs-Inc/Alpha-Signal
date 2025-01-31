# main.py
import argparse
import os
import shutil
from pathlib import Path

from alphasignal.models.enums import SellMode
from alphasignal.services.service import (
    create_wallet,
    fund,
    get_swap_quote,
    get_token_value,
    get_wallet_value,
    initialize_database,
    load_wallet,
    process_orders,
    swap_tokens,
    add_order_command,
    get_tracked_orders_command,
    remove_order_command,
)
import asyncio
from dotenv import load_dotenv

load_dotenv()


def execute_command(command, args, wallet):
    if command == "add_order":
        asyncio.run(add_order_command())
    elif command == "remove_order":
        remove_order_command()
    elif command == "get_orders":
        get_tracked_orders_command()
    elif command == "process":
        asyncio.run(process_orders())
    elif command == "make_wallet":
        create_wallet()
    elif command == "value":
        asyncio.run(get_token_value(args[0]))
    elif command == "wallet_value":
        asyncio.run(get_wallet_value(wallet))
    elif command == "quote":
        asyncio.run(get_swap_quote(args[0], args[1], args[2]))
    elif command == "swap":
        asyncio.run(swap_tokens(args[0], args[1], args[2], wallet))
    elif command == "fund":
        asyncio.run(fund(args[0], wallet))
    else:
        print("Unknown command. Type 'help' for a list of commands.")


def main():
    initialize_database()  # Move to start once only a single acc can be created
    print(
        "Welcome to the AlphaSignal Interactive CLI. Type 'start' to get started. Type 'help' to see all available commands, or 'exit'/'quit' to quit."
    )
    try:
        wallet = load_wallet()
        display_wallet_pubkey = wallet.wallet.public_key
    except Exception as e:
        print(e)
        no_wallet = True
        while no_wallet:
            user_input = input(
                "Type make_wallet to create a new wallet\nAlphaSignal>  "
            ).strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting AlphaSignal. Goodbye!")
                break
            elif user_input.lower() == "make_wallet":
                wallet = create_wallet()
                no_wallet = False
            else:
                print("No wallet found, please make a wallet before continuing.")

    while True:
        user_input = input("AlphaSignal> ").strip()
        load_dotenv()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting AlphaSignal. Goodbye!")
            break
        elif user_input.lower() == "help":
            print("Available commands:")
            print("  start - Initialize the application and create an account.")
            print("  create_account <account_name> - Create an account.")
            print("  follow <twitter_handle> - Follow a Twitter account.")
            print("  unfollow <twitter_handle> - Unfollow a Twitter account.")
            print("  tokens - Get current wallet details.")
            print(
                "  add_order <mint_address> - Add a order in your wallet to be tracked."
            )
            print("  sell <mint_address> - Sell a order.")
            print("  exit or quit - Exit the CLI.")
        else:
            parts = user_input.split()
            command = parts[0]
            args = parts[1:]

            # Validate arguments based on command
            try:
                if command == "create_account" and len(args) != 1:
                    print(
                        "Error: 'create_account' requires exactly 1 argument: <account_name>"
                    )
                elif command in ["follow", "unfollow"] and len(args) != 1:
                    print(
                        f"Error: '{command}' requires exactly 1 argument: <twitter_handle>"
                    )
                elif command == fund and len(args) != 1:
                    print(
                        f"Error: '{command}' requires exactly 1 argument: <fund amount>"
                    )
                elif command == "sell" and len(args) != 1:
                    print("Error: 'sell' requires exactly 1 argument: <mint_address>")
                elif command == "make_wallet":
                    if len(args) == 0:
                        # No arguments, valid
                        execute_command(command, args, wallet)
                    elif (
                        len(args) == 2
                        and args[0] == "--fund"
                        and args[1].lower() in ["true", "false"]
                    ):
                        # Valid --fund flag with boolean value
                        execute_command(command, args, wallet)
                    else:
                        print(
                            "Error: 'make_wallet' requires no arguments or --fund BOOLEAN as a flag."
                        )
                elif command == "swap":
                    print(
                        f"Arguments received for swap: {args}"
                    )  # Debugging: Print arguments received
                    if len(args) != 3:
                        print(
                            "Error: 'swap' requires exactly 3 arguments: <from_token_mint> <to_token_mint> <amount>"
                        )
                    else:
                        from_token_mint = args[0]
                        to_token_mint = args[1]
                        amount_str = args[2]

                        # Validate token mint addresses (44 characters for Solana mints)

                        try:
                            # Debugging: Print amount before parsing
                            print(f"Raw amount received: {amount_str}")

                            # Convert amount to float
                            amount_float = float(amount_str)
                            if amount_float <= 0:
                                print("Error: <amount> must be a positive number.")
                            else:
                                # Convert to smallest unit (e.g., lamports for SOL)

                                # Debugging: Print validated inputs
                                print(
                                    f"Validated inputs - from: {from_token_mint}, to: {to_token_mint}, amount (in smallest unit): {amount_float}"
                                )

                                # Execute the command if all validations pass
                                execute_command(
                                    command,
                                    [from_token_mint, to_token_mint, amount_float],
                                    wallet,
                                )
                        except ValueError as e:
                            print(f"Error: <amount> must be a valid number. {e}")
                            raise e
                else:
                    execute_command(command, args, wallet)
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
