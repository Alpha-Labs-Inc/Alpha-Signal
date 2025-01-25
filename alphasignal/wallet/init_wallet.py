from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solana.rpc.types import TxOpts
from solders.transaction import Transaction
import asyncio
import base58
import os
import json

# Constants
SOLANA_CLUSTER_URL = "https://api.mainnet-beta.solana.com"  # Mainnet cluster URL
WALLET_SAVE_FILE = "wallet_keypair.json"  # File to save the wallet keypair securely


async def create_wallet():
    """Generate a new Solana wallet or load an existing one."""
    # Check if the wallet keypair file exists
    if os.path.exists(WALLET_SAVE_FILE):
        print(
            f"Wallet file {WALLET_SAVE_FILE} already exists. Loading existing wallet..."
        )
        with open(WALLET_SAVE_FILE, "r") as f:
            wallet_data = json.load(f)  # Properly load JSON as a dictionary

        public_key = wallet_data["public_key"]
        secret_key = base58.b58decode(wallet_data["secret_key"])
        wallet = Keypair.from_seed(secret_key)

        print(f"Loaded wallet successfully! Public Key: {public_key}")
        return wallet

    # If the file does not exist, create a new wallet
    print("No existing wallet found. Creating a new wallet...")
    wallet = Keypair()
    public_key = str(wallet.pubkey())
    secret_key = base58.b58encode(wallet.secret()).decode()

    # Save the wallet's keypair to a file in human-readable JSON format
    wallet_data = {
        "public_key": str(public_key),  # Ensure the public key is a string
        "secret_key": str(secret_key),  # Ensure the secret key is a string
    }
    with open(WALLET_SAVE_FILE, "w") as f:
        json.dump(wallet_data, f, indent=4)  # Save JSON in a readable format

    print(f"Wallet created successfully! Public Key: {public_key}")
    print(f"Wallet keypair saved to {WALLET_SAVE_FILE}")
    return wallet


async def fund_wallet(
    sender_wallet: Keypair, recipient_public_key: Pubkey, amount: float
):
    """Send SOL to the new wallet."""
    async with AsyncClient(SOLANA_CLUSTER_URL) as client:
        # Convert amount to lamports (1 SOL = 1_000_000_000 lamports)
        lamports = int(amount * 1_000_000_000)

        # Create and send a transaction
        txn = Transaction().add(
            transfer(
                TransferParams(
                    from_pubkey=sender_wallet.pubkey(),  # Fix: Use pubkey() instead of public_key
                    to_pubkey=recipient_public_key,
                    lamports=lamports,
                )
            )
        )
        response = await client.send_transaction(
            txn, sender_wallet, opts=TxOpts(skip_preflight=True)
        )

        if response["result"]:
            print(f"Transaction successful! Signature: {response['result']}.")
        else:
            print(f"Transaction failed! Error: {response['error']}")


async def create_solana_wallet(fund: bool = False):
    """Main setup process."""
    # Step 1: Create a new wallet
    print("Creating a new wallet...")
    new_wallet = await create_wallet()

    # Step 3: Fund the new wallet

    if fund:
        sender_secret_key = os.getenv(
            "FUNDING_WALLET_SECRET_KEY"
        )  # Load sender private key from environment variable
        if not sender_secret_key:
            print("Error: Set the SENDER_SECRET_KEY environment variable.")
            return

        sender_keypair = Keypair.from_secret_key(base58.b58decode(sender_secret_key))
        print("Funding the new wallet with SOL...")
        await fund_wallet(
            sender_keypair, new_wallet.pubkey(), amount=0.001
        )  # Fix: Use pubkey() instead of public_key
