import argparse
import asyncio
from alphasignal.services.wallet_manager import WalletManager


def main():
    parser = argparse.ArgumentParser(description="Send SOL to a wallet")
    parser.add_argument(
        "-d", "--destination", required=True, help="Destination wallet address"
    )
    parser.add_argument(
        "-a", "--amount", required=True, type=float, help="Amount of SOL to send"
    )
    args = parser.parse_args()
    destination = args.destination
    amount = args.amount

    wallet_manager = WalletManager()
    try:
        tx_sig = asyncio.run(wallet_manager.send_sol(destination, amount))
        print(f"Transaction sent! Signature: {tx_sig}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
        raise ve


if __name__ == "__main__":
    main()
