import os

import requests
import json
import os
import base64
from solana.rpc.commitment import Processed
from solana.rpc.types import TxOpts
from solders.transaction import VersionedTransaction
from solders import message
from tenacity import retry, stop_after_attempt, wait_exponential

from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.models.constants import USDC_MINT_ADDRESS
from alphasignal.models.mint_token import MintToken
from alphasignal.schemas.responses.quote_response import QuoteResponse
from alphasignal.models.wallet import Wallet
from alphasignal.services.token_manager import TokenManager


class JupiterClient:
    def __init__(self):
        self.jupiter_api_url = os.getenv("JUPITER_API_URL")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fetch_swap_quote(
        self,
        from_token_mint,
        to_token_mint,
        amount,
        slippage_bps=50,
        swap_mode="ExactIn",
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
        from_token = TokenManager(from_token_mint)
        to_token = TokenManager(to_token_mint)
        from_token_decimals = await from_token.get_token_decimals()

        input_amount_smallest_units = int(amount * (10**from_token_decimals))

        url = f"{self.jupiter_api_url}/quote"
        params = {
            "inputMint": from_token.token.token_mint_address,
            "outputMint": to_token.token.token_mint_address,
            "amount": input_amount_smallest_units,
            "slippageBps": slippage_bps,
            "swapMode": swap_mode,
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"Error fetching quotes: {response.text}")

        quote = response.json()
        if not quote.get("routePlan"):
            raise Exception("No swap routes available.")

        return quote

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fetch_token_value(self, token_mint_address) -> float:
        """
        Fetch the current value of a coin in USD from the Jupiter API.

        Args:
            mint_address (str): The mint address of the token.

        Returns:
            float: The current value of the token in USD.
        """
        if token_mint_address == USDC_MINT_ADDRESS:
            return float(1.0000)
        token_manager = TokenManager(token_mint_address=token_mint_address)
        decimals = await token_manager.get_token_decimals()
        input_amount_smallest_units = int(1 * (10**decimals))
        url = f"{self.jupiter_api_url}/quote?inputMint={token_mint_address}&outputMint={USDC_MINT_ADDRESS}&amount={input_amount_smallest_units}"  # Need to integrate with the decimal of the coin
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            price = float(data["swapUsdValue"])
            return price
        raise Exception(f"Unable to fetch price for mint address: {token_mint_address}")

    async def create_quote(
        self,
        from_token_mint,
        to_token_mint,
        input_amount,
        slippage_bps=50,
    ):
        try:
            input_amount = float(input_amount)
        except:
            raise Exception("amount must be float or int")

        quote = await self.fetch_swap_quote(
            from_token_mint,
            to_token_mint,
            input_amount,
            slippage_bps,
        )
        out_token = TokenManager(to_token_mint)
        to_token_decimals = await out_token.get_token_decimals()
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

        return QuoteResponse(
            slippage_bps=slippage_bps,
            from_token_amt=input_amount,
            to_token_amt=output_token_amount,
            from_token_amt_usd=input_usd,
            to_token_amt_usd=output_usd,
            conversion_rate=conversion_rate,
            price_impact=price_impact_pct,
            price_impact_usd=price_impact_usd,
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def swap_tokens(
        self,
        from_token_mint,
        to_token_mint,
        input_amount,
        wallet,
        slippage_bps=50,
    ):
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
            quote = await self.fetch_swap_quote(
                from_token_mint, to_token_mint, input_amount, slippage_bps
            )
            transaction_signature = await self.execute_swap(quote, wallet)
            return transaction_signature
        except ValueError as e:
            raise Exception(f"Error: {e}")

    async def execute_swap(
        self,
        quote,
        wallet: Wallet,
    ):
        """
        Execute a swap transaction using the Jupiter Aggregator.

        Args:
            quote (dict): The best swap quote from Jupiter API.
            wallet (Keypair): Wallet Keypair object for signing the transaction.

        Returns:
            str: The transaction signature.
        """
        swap_url = f"{self.jupiter_api_url}/swap"
        payload = {
            "quoteResponse": quote,
            "userPublicKey": str(wallet.public_key),  # Ensure pubkey is a string
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
                raise RuntimeError("No swapTransaction provided by the /swap endpoint.")

            client = SolanaClient().client

            raw_transaction = VersionedTransaction.from_bytes(
                base64.b64decode(swap_transaction)
            )
            signature = wallet.wallet_keypair.sign_message(
                message.to_bytes_versioned(raw_transaction.message)
            )
            signed_txn = VersionedTransaction.populate(
                raw_transaction.message, [signature]
            )

            opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
            result = client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)

            transaction_id = json.loads(result.to_json())["result"]
            return transaction_id
        except Exception as e:
            raise Exception(f"Error swapping tokens: {e}")
