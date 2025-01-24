# main.py
import argparse
import os
import shutil
from pathlib import Path
from alphasignal.commands.account import create_account
from alphasignal.commands.twitter import follow, unfollow
from alphasignal.commands.coin_manager import track, sell


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
    else:
        print("Unknown command. Type 'help' for a list of commands.")


def start():
    cwd = Path(os.getcwd())

    # Clone .env.example to .env
    env_example_path = cwd / ".env.example"
    env_path = cwd / ".env"

    if not env_path.exists():
        shutil.copy(env_example_path, env_path)
        print(".env file created from .env.example")

    # Ask user to input required keys
    with env_path.open("r") as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        if "YOUR_" in line:
            key = line.split("=")[0]
            value = input(f"Please enter the value for {key}: ")
            new_lines.append(f"{key}={value}\n")
        else:
            new_lines.append(line)

    with env_path.open("w") as file:
        file.writelines(new_lines)

    # Create account
    account_name = input("Enter account name to create: ")
    create_account(account_name)


def main():
    print(
        "Welcome to the AlphaSignal Interactive CLI. Type 'start' to get started. Type 'help' to see all available commands, or 'exit'/'quit' to quit."
    )
    while True:
        user_input = input("AlphaSignal> ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting AlphaSignal. Goodbye!")
            break
        elif user_input.lower() == "help":
            print("Available commands:")
            print("  start - Initialize the application and create an account.")
            print("  create_account <account_name> - Create an account.")
            print("  follow <twitter_handle> - Follow a Twitter account.")
            print("  unfollow <twitter_handle> - Unfollow a Twitter account.")
            print("  track <mint_address> <track_type> - Track a coin.")
            print("  sell <mint_address> - Sell a coin.")
            print("  exit or quit - Exit the CLI.")
        elif user_input.lower() == "start":
            start()
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
                elif command == "track" and len(args) != 2:
                    print(
                        "Error: 'track' requires exactly 2 arguments: <mint_address> <track_type>"
                    )
                elif command == "sell" and len(args) != 1:
                    print("Error: 'sell' requires exactly 1 argument: <mint_address>")
                else:
                    execute_command(command, args)
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
