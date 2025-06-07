import sys
import asyncio
from alphasignal.services.wallet_manager import WalletManager


def main():
    if len(sys.argv) != 3:
        print("Usage: python send_sol_home.py <destination_wallet_address> <amount>")
        sys.exit(1)
    destination = sys.argv[1]
    try:
        amount = float(sys.argv[2])
    except ValueError:
        print("Error: amount must be a number")
        sys.exit(1)

    wallet_manager = WalletManager()
    try:
        tx_sig = asyncio.run(wallet_manager.send_sol(destination, amount))
        print(f"Transaction sent! Signature: {tx_sig}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
        raise ve


if __name__ == "__main__":
    main()
