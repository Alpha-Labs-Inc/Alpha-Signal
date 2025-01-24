import json


def load_wallet_address() -> str:
    """
    Load the wallet public key from 'wallet_keypair.json'.

    Returns:
        str: The wallet public key.
    """
    try:
        with open("wallet_keypair.json", "r") as f:
            wallet_data = json.load(f)
            return wallet_data["public_key"]
    except (FileNotFoundError, KeyError):
        raise FileNotFoundError("Error: 'wallet_keypair.json' is missing or malformed. Ensure it contains a 'public_key' key.")