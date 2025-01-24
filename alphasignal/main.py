# main.py
import argparse
from alphasignal.commands.account import create_account
from alphasignal.commands.twitter import follow, unfollow
from alphasignal.commands.coin_manager import track, sell
from alphasignal.wallet.solana_wallet import create_solana_wallet
import asyncio
def execute_command(command, args):
    if command == "create_account":
        create_account(args[0])
    elif command == "follow":
        follow(args[0])
    elif command == "unfollow":
        unfollow(args[0])
    elif command == "track":
        track(args[0], args[1])
    elif command == "sell":
        sell(args[0])
    elif command == "make_wallet":
        if len(args) == 0:
            asyncio.run(create_solana_wallet())
        else:
            asyncio.run(create_solana_wallet(args[1]))
    else:
        print("Unknown command. Type 'help' for a list of commands.")

def main():
    print("Welcome to the AlphaSignal Interactive CLI. Type 'help' to see available commands, or 'exit'/'quit' to quit.")
    while True:
        user_input = input("AlphaSignal> ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting AlphaSignal. Goodbye!")
            break
        elif user_input.lower() == "help":
            print("Available commands:")
            print("  create_account <account_name> - Create an account.")
            print("  follow <twitter_handle> - Follow a Twitter account.")
            print("  unfollow <twitter_handle> - Unfollow a Twitter account.")
            print("  track <mint_address> <track_type> - Track a coin.")
            print("  sell <mint_address> - Sell a coin.")
            print("  exit or quit - Exit the CLI.")
        else:
            parts = user_input.split()
            command = parts[0]
            args = parts[1:]

            # Validate arguments based on command
            try:
                if command == "create_account" and len(args) != 1:
                    print("Error: 'create_account' requires exactly 1 argument: <account_name>")
                elif command in ["follow", "unfollow"] and len(args) != 1:
                    print(f"Error: '{command}' requires exactly 1 argument: <twitter_handle>")
                elif command == "track" and len(args) != 2:
                    print("Error: 'track' requires exactly 2 arguments: <mint_address> <track_type>")
                elif command == "sell" and len(args) != 1:
                    print("Error: 'sell' requires exactly 1 argument: <mint_address>")
                elif command == "make_wallet":
                    if len(args) == 0:
                        # No arguments, valid
                        execute_command(command, args)
                    elif len(args) == 2 and args[0] == "--fund" and args[1].lower() in ["true", "false"]:
                        # Valid --fund flag with boolean value
                        execute_command(command, args)
                    else:
                        print("Error: 'make_wallet' requires no arguments or --fund BOOLEAN as a flag.")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()