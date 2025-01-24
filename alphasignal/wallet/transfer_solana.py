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
    rpc_url = "https://api.mainnet-beta.solana.com"  # Solana mainnet endpoint
    async with AsyncClient(rpc_url) as client:
        try:
            # Convert the Base58 mint address to a valid Pubkey
            mint_pubkey = Pubkey.from_string(mint_address)

            # Fetch account info for the mint
            response = await client.get_account_info(mint_pubkey)

            # Access the account information properly
            account_info = response.value  # .value holds the account info object
            if account_info is None:
                raise ValueError(
                    f"Invalid or non-existent mint address: {mint_address}"
                )

            # Debugging: Print account_info.data to verify its structure
            print(f"account_info.data: {account_info.data}")

            # The account data is already raw binary; no need for Base64 decoding
            raw_data = account_info.data

            # The decimals are stored at byte offset 44, size 1 (1 byte)
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

    # Decode the 32-byte private key (seed)
    secret_key = base58.b58decode(wallet_data["secret_key"])

    # Generate the full keypair using the seed
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
    headers = {"User-Agent": "AlphaSignalClient/1.0"}

    # Make the API request
    response = requests.get(url, params=params, headers=headers)

    # Debugging: Print the full response
    print(f"API Response Status Code: {response.status_code}")
    print(f"API Response Text: {response.text}")

    if response.status_code != 200:
        raise RuntimeError(f"Error fetching quotes: {response.text}")

    # Process the response JSON
    quote = response.json()
    print(quote)
    # Ensure required fields are in the response
    if not quote.get("routePlan"):
        raise RuntimeError("No swap routes available.")

    return quote


async def execute_swap(quote, wallet):
    """
    Execute a swap transaction using the Jupiter Aggregator.

    Args:
        quote (dict): The best swap quote from Jupiter API.
        wallet (Keypair): Wallet Keypair object for signing the transaction.

    Returns:
        str: The transaction signature.
    """
    # Extract the serialized transaction
    swap_transaction = quote.get("swapTransaction")
    if not swap_transaction:
        raise RuntimeError("No swapTransaction provided in the quote response.")

    # Deserialize the transaction
    transaction = Transaction.deserialize(base58.b58decode(swap_transaction))

    # Sign the transaction with the wallet
    transaction.sign(wallet)

    async with AsyncClient(SOLANA_CLUSTER_URL) as client:
        # Send the signed transaction
        response = await client.send_transaction(
            transaction, opts={"skip_preflight": True}
        )
        if "result" not in response or not response["result"]:
            raise RuntimeError(f"Swap failed! Error: {response['error']}")

        # Return the transaction signature
        return response["result"]


async def swap_tokens(from_token_mint, to_token_mint, input_amount, slippage_bps=50):
    """
    Perform a token swap using Jupiter Aggregator API, dynamically handling decimals.

    Args:
        from_token_mint (str): Mint address of the token to swap from.
        to_token_mint (str): Mint address of the token to swap to.
        input_amount (float): The input amount in token units (e.g., 1.0 USDC).
        slippage_bps (int): Slippage tolerance in basis points (default: 50 bps = 0.5%).

    Returns:
        None: Prints the swap details and confirms the transaction.
    """
    try:
        wallet = load_wallet_secret_key()  # Load the wallet from JSON

        # Validate and convert the mint addresses to PublicKey
        from_token_decimals = await get_token_decimals(from_token_mint)
        to_token_decimals = await get_token_decimals(to_token_mint)

        # Convert the input amount to the smallest unit of the "from token"
        input_amount_smallest_units = int(input_amount * (10**from_token_decimals))

        print(
            f"Fetching swap quote for {input_amount} tokens ({input_amount_smallest_units} smallest units)..."
        )
        # Fetch the actual swap quote from Jupiter API
        quote = await fetch_swap_quote(
            from_token_mint, to_token_mint, input_amount_smallest_units, slippage_bps
        )

        # Extract the best route from the quote
        out_amount_smallest_units = int(quote["outAmount"])
        swap_usd_value = float(quote["swapUsdValue"])  # Total USD value of the output
        price_impact_pct = float(quote.get("priceImpactPct", 0))

        # Convert output amount to human-readable format
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

        confirm = (
            input("Do you want to proceed with the swap? (yes/no): ").strip().lower()
        )
        if confirm != "yes":
            print("Swap cancelled.")
            return

        print("Executing swap...")
        transaction_signature = await execute_swap(quote, wallet)
        print(f"Swap completed! Transaction signature: {transaction_signature}")
        return transaction_signature

    except ValueError as e:
        print(f"Error: {e}")
