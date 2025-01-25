import asyncio
import requests
import struct
import base58
import json
import os
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base64
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.transaction import Transaction

WALLET_SAVE_FILE = "wallet_keypair.json"  # Wallet JSON file containing keys


def load_wallet_secret_key():
    """
    Load the wallet's secret key from the JSON file and reconstruct the full keypair.

    Returns:
        Keypair: A Keypair object for signing transactions.
    """
    if not os.path.exists(WALLET_SAVE_FILE):
        raise FileNotFoundError(
            f"{WALLET_SAVE_FILE} does not exist. Create a wallet first."
        )

    with open(WALLET_SAVE_FILE, "r") as f:
        wallet_data = json.load(f)

    secret_key = base58.b58decode(wallet_data["secret_key"])
    print(Keypair.from_seed(secret_key))
    return Keypair.from_seed(secret_key)


if __name__ == "__main__":
    load_wallet_secret_key()
