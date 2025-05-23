import sys
import asyncio
from alphasignal.services.wallet_manager import WalletManager


dest = "7RH4SDoNA4cfJWikCht7pX4zheX7hedX2N5oMbrPSZPG"


def main():
    if len(sys.argv) != 2:
        print("Usage: python send_sol_home.py <destination_wallet_address>")
        sys.exit(1)
    destination = sys.argv[1]
    wallet_manager = WalletManager()
    try:
        tx_sig = asyncio.run(wallet_manager.send_all_sol(destination))
        print(f"Transaction sent! Signature: {tx_sig}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
        raise ve


if __name__ == "__main__":
    main()
