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
from solana.rpc.commitment import Confirmed, Processed
from solders.transaction import Transaction
from solana.rpc.types import TxOpts
from solders.rpc.config import RpcSendTransactionConfig
from solders.hash import Hash
from solana.rpc.api import Client
from solders.transaction import VersionedTransaction
from solders import message


# Constants
SOLANA_CLUSTER_URL = "https://api.mainnet-beta.solana.com"  # Solana mainnet
JUPITER_API_URL = "https://quote-api.jup.ag/v6"  # Jupiter Aggregator API base URL
WALLET_SAVE_FILE = "wallet_keypair.json"  # Wallet JSON file containing keys


async def get_token_decimals(mint_address):
    """
    Fetch the decimals for a given token mint address using Solana RPC and `solders.pubkey.Pubkey`.

    Args:
        mint_address (str): The token mint address (Base58 encoded).

    Returns:
        int: The number of decimals for the token.
    """
    async with AsyncClient(SOLANA_CLUSTER_URL) as client:
        try:
            mint_pubkey = Pubkey.from_string(mint_address)
            response = await client.get_account_info(mint_pubkey)
            account_info = response.value
            if account_info is None:
                raise ValueError(
                    f"Invalid or non-existent mint address: {mint_address}"
                )
            raw_data = account_info.data
            decimals = struct.unpack_from("B", raw_data, offset=44)[0]
            return decimals
        except Exception as e:
            raise ValueError(
                f"Error fetching decimals for mint address {mint_address}: {e}"
            )


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
    return Keypair.from_seed(secret_key)


async def fetch_swap_quote(
    from_token_mint, to_token_mint, amount, slippage_bps=50, swap_mode="ExactIn"
):
    """
    Fetch the best swap quote from Jupiter Aggregator.

    Args:
        from_token_mint (str): Mint address of the token to swap from.
        to_token_mint (str): Mint address of the token to swap to.
        amount (int): Amount to swap (in smallest units).
        slippage_bps (int): Slippage tolerance in basis points (default: 50 bps = 0.5%).
        swap_mode (str): Swap mode, either "ExactIn" (default) or "ExactOut".

    Returns:
        dict: The full swap quote from Jupiter API.
    """
    url = f"{JUPITER_API_URL}/quote"
    params = {
        "inputMint": from_token_mint,
        "outputMint": to_token_mint,
        "amount": amount,
        "slippageBps": slippage_bps,
        "swapMode": swap_mode,
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Error fetching quotes: {response.text}")

    quote = response.json()
    if not quote.get("routePlan"):
        raise RuntimeError("No swap routes available.")

    return quote


async def swap_tokens(from_token_mint, to_token_mint, input_amount, slippage_bps=50):
    """
    Perform a token swap using Jupiter Aggregator API, dynamically handling decimals.

    Args:
        from_token_mint (str): Mint address of the token to swap from.
        to_token_mint (str): Mint address of the token to swap to.
        input_amount (float): The input amount in token units (e.g., 1.0 USDC).
        slippage_bps (int): Slippage tolerance in basis points (default: 50 bps = 0.5%).

    Returns:
        str: The transaction signature of the completed swap.
    """
    try:
        wallet = load_wallet_secret_key()
        from_token_decimals = await get_token_decimals(from_token_mint)
        to_token_decimals = await get_token_decimals(to_token_mint)

        input_amount_smallest_units = int(input_amount * (10**from_token_decimals))

        print(
            f"Fetching swap quote for {input_amount} tokens ({input_amount_smallest_units} smallest units)..."
        )
        quote = await fetch_swap_quote(
            from_token_mint, to_token_mint, input_amount_smallest_units, slippage_bps
        )
        out_amount_smallest_units = int(quote["outAmount"])
        swap_usd_value = float(quote["swapUsdValue"])
        price_impact_pct = float(quote.get("priceImpactPct", 0))
        output_token_amount = out_amount_smallest_units / (10**to_token_decimals)

        # Conversion rate
        input_usd = float(swap_usd_value) / float(1 - price_impact_pct)
        output_usd = swap_usd_value  # Total USD value of the output token

        # Conversion rate (token-to-token)
        conversion_rate = (
            output_token_amount / input_amount
        )  # Tokens of output per 1 token of input

        # Price impact in USD
        price_impact_usd = (
            input_usd * price_impact_pct
        )  # Price impact as a dollar value

        # Display the quote details
        print(f"Quote details:")
        print(f"- Input: {input_amount:.6f} tokens (~${input_usd:.2f})")
        print(f"- Output: {output_token_amount:.6f} tokens (~${output_usd:.2f})")
        print(f"- Conversion Rate: {conversion_rate:.6f} tokens per input token")
        print(
            f"- Price Impact: {price_impact_pct * 100:.4f}% (~${price_impact_usd:.2f})"
        )
        print(f"- Slippage Tolerance: {slippage_bps / 100:.2f}%")

        # confirm = (
        #     input("Do you want to proceed with the swap? (yes/no): ").strip().lower()
        # )
        # if confirm != "yes":
        #     print("Swap cancelled.")
        #     return

        print("Executing swap...")
        transaction_signature = await execute_swap(quote, wallet)
        print(f"Swap completed! Transaction signature: {transaction_signature}")
        return transaction_signature

    except ValueError as e:
        print(f"Error: {e}")


async def execute_swap(quote, wallet):
    """
    Execute a swap transaction using the Jupiter Aggregator.

    Args:
        quote (dict): The best swap quote from Jupiter API.
        wallet (Keypair): Wallet Keypair object for signing the transaction.

    Returns:
        str: The transaction signature.
    """
    swap_url = f"{JUPITER_API_URL}/swap"
    payload = {
        "quoteResponse": quote,
        "userPublicKey": str(wallet.pubkey()),  # Ensure pubkey is a string
        "wrapAndUnwrapSol": True,
    }

    try:
        response = requests.post(
            swap_url, json=payload, headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            raise RuntimeError(f"Error fetching swap transaction: {response.text}")
        swap_data = response.json()
        swap_transaction = swap_data.get("swapTransaction")

        if not swap_transaction:
            print(
                f"Swap transaction is missing. Full response: {json.dumps(swap_data, indent=4)}"
            )
            raise RuntimeError("No swapTransaction provided by the /swap endpoint.")
        client = Client(endpoint=SOLANA_CLUSTER_URL)
        # Decode and deserialize the transaction
        raw_transaction = VersionedTransaction.from_bytes(
            base64.b64decode(swap_transaction)
        )
        signature = wallet.sign_message(
            message.to_bytes_versioned(raw_transaction.message)
        )
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])

        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
        result = client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)

        transaction_id = json.loads(result.to_json())["result"]
        print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")
        return transaction_id
    except Exception as e:
        raise Exception(f"poop fart {e}")
