from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
from typing import List
import base58
import os
import json
from solders.keypair import Keypair
from alphasignal.apis.dexscreener.dexscreener_client import DexscreenerClient
from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.database.db import SQLiteDB
from alphasignal.models.wallet import Wallet
from alphasignal.models.wallet_token import WalletToken
from alphasignal.schemas.responses.wallet_value_response import WalletValueResponse

import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# Constants
SOLANA_CLUSTER_URL = "https://api.mainnet-beta.solana.com"  # Mainnet cluster URL


class WalletManager:
    def __init__(self, make_wallet: bool = False):
        self.make_wallet = make_wallet
        self.wallet_save_file = os.getenv("WALLET_SAVE_FILE", "wallet_keypair.json")
        if not os.path.exists(self.wallet_save_file) and not self.make_wallet:
            raise Exception("No wallet found.")
        elif make_wallet and not os.path.exists(self.wallet_save_file):
            self.wallet = asyncio.run(self.create_wallet())
        elif os.path.exists(self.wallet_save_file) and make_wallet:
            raise Exception("Wallet already found.")
        self.wallet = self.load_wallet()

    def load_wallet(self):
        """Load the wallet's public and secret keys."""
        try:
            with open(self.wallet_save_file, "r") as file:
                wallet_data = json.load(file)

            secret_key = base58.b58decode(wallet_data["secret_key"])
            keypair = Keypair.from_seed(secret_key)
            public_key = keypair.pubkey()

            return Wallet(public_key=public_key, wallet_keypair=keypair)
        except Exception as e:
            raise Exception(f"Error loading wallet keys: {e}")

    async def create_wallet(self):
        wallet = Keypair()
        public_key = str(wallet.pubkey())
        secret_key = base58.b58encode(wallet.secret()).decode()
        wallet_data = {
            "public_key": str(public_key),  # Ensure the public key is a string
            "secret_key": str(secret_key),  # Ensure the secret key is a string
        }

        with open(self.wallet_save_file, "w") as f:
            json.dump(wallet_data, f, indent=4)  # Save JSON in a readable format

    async def get_tokens(self) -> List[WalletToken]:
        """
        Fetch the tokens in a Solana wallet and return them as Pydantic models, including token names if available.

        Returns:
            List[WalletToken]: A list of tokens with their mint addresses, balances, and names.
        """
        # Solana RPC endpoint
        try:
            solana_client = SolanaClient()
            dexscreener_client = DexscreenerClient()

            response = solana_client.get_owner_token_accounts(self.wallet)
            if not response.value:
                return []
            tokens = []
            for token_info in response.value:
                mint_address = token_info.account.data.parsed["info"]["mint"]
                bal = float(
                    token_info.account.data.parsed["info"]["tokenAmount"]["uiAmount"]
                )
                try:
                    token_data = await dexscreener_client.get_token_pairs(mint_address)

                    tokens.append(
                        WalletToken(
                            mint_address=token_data["mint_address"],
                            token_name=token_data["token_name"],
                            token_ticker=token_data["token_ticker"],
                            image=token_data["image"],
                            value=float(token_data["priceUsd"]),
                            balance=bal,
                            usd_balance=float(token_data["priceUsd"] * bal),
                            percent_change_24hr=token_data["h24"],
                            percent_change_6hr=token_data["h6"],
                            percent_change_1hr=token_data["h1"],
                            percent_change_5min=token_data["m5"],
                            change_24hr=(
                                float(
                                    token_data["priceUsd"] * (token_data["h24"] / 100)
                                )
                                if token_data.get("priceUsd") is not None
                                and token_data.get("h24") is not None
                                else None
                            ),
                            change_6hr=(
                                float((token_data["priceUsd"] * token_data["h6"]) / 100)
                                if token_data.get("priceUsd") is not None
                                and token_data.get("h6") is not None
                                else None
                            ),
                            change_1hr=(
                                float((token_data["priceUsd"] * token_data["h1"]) / 100)
                                if token_data.get("priceUsd") is not None
                                and token_data.get("h1") is not None
                                else None
                            ),
                            change_5min=(
                                float((token_data["priceUsd"] * token_data["m5"]) / 100)
                                if token_data.get("priceUsd") is not None
                                and token_data.get("m5") is not None
                                else None
                            ),
                        )
                    )
                except Exception as e:
                    logging.error(f"Error getting token data: {e}")
                    raise Exception(f"Error getting data: {e}")
            tokens = sorted(tokens, key=lambda t: t.usd_balance, reverse=True)
            return tokens
        except Exception as e:
            raise Exception(
                f"error here:{repr(e)}, {type(e).__name__}, message: {e}"
            ) from e

        # return tokens

    async def get_wallet_value(self):
        tokens = await self.get_tokens()
        total_value = 0.0
        total_change_24 = 0.0
        if not tokens:
            return
        for token in tokens:
            if token.value is None or token.balance is None:
                continue
            wallet_value = token.balance * token.value
            total_value += wallet_value
        for token in tokens:
            if token.change_24hr is not None:
                total_change_24 += token.change_24hr * token.balance
        percent_change = (((total_value + total_change_24) / total_value) * 100) - 100
        return WalletValueResponse(
            wallet_tokens=tokens,
            total_value=total_value,
            percent_change_value_24h=percent_change,
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_token_acct_value(self, mint_address: str):
        """
        Return the balance for a specific token account in the wallet.

        Args:
            mint_address (str): The mint address of the token.

        Returns:
            float: The balance of the specified token.
        """
        try:
            solana_client = SolanaClient()
            response = solana_client.get_owner_token_accounts(self.wallet)
            if not response.value:
                raise Exception("Failed to get token accounts")

            for token_info in response.value:
                token_mint_address = token_info.account.data.parsed["info"]["mint"]
                if token_mint_address == mint_address:
                    balance = float(
                        token_info.account.data.parsed["info"]["tokenAmount"][
                            "uiAmount"
                        ]
                    )
                    return balance

            # If the mint address is not found in the wallet
            return 0
        except Exception as e:
            logger.error(f"Error getting wallet value: {e}")
            raise Exception(f"Error getting wallet value: {e}")

    async def get_sol_value(self):
        try:
            solana_client = SolanaClient()
            dexscreener_client = DexscreenerClient()
            solana_mint = "So11111111111111111111111111111111111111112"
            sol_bal = solana_client.get_sol_balance(self.wallet)
            token_data = await dexscreener_client.get_token_pairs(solana_mint)
            if sol_bal is None or token_data["priceUsd"] is None:
                raise ValueError("Retrieved SOL balance or price is None")
            return WalletToken(
                mint_address=token_data["mint_address"],
                token_name=token_data["token_name"],
                token_ticker=token_data["token_ticker"],
                image=token_data["image"],
                value=float(token_data["priceUsd"]),
                balance=sol_bal,
                usd_balance=float(token_data["priceUsd"] * sol_bal),
                percent_change_24hr=token_data["h24"],
                percent_change_6hr=token_data["h6"],
                percent_change_1hr=token_data["h1"],
                percent_change_5min=token_data["m5"],
                change_24hr=(
                    float(token_data["priceUsd"] * (token_data["h24"] / 100))
                    if token_data.get("priceUsd") is not None
                    and token_data.get("h24") is not None
                    else None
                ),
                change_6hr=(
                    float(
                        token_data["priceUsd"]
                        - (token_data["priceUsd"] * token_data["h6"])
                    )
                    if token_data.get("priceUsd") is not None
                    and token_data.get("h6") is not None
                    else None
                ),
                change_1hr=(
                    float(
                        token_data["priceUsd"]
                        - (token_data["priceUsd"] * token_data["h1"])
                    )
                    if token_data.get("priceUsd") is not None
                    and token_data.get("h1") is not None
                    else None
                ),
                change_5min=(
                    float(
                        token_data["priceUsd"]
                        - (token_data["priceUsd"] * token_data["m5"])
                    )
                    if token_data.get("priceUsd") is not None
                    and token_data.get("m5") is not None
                    else None
                ),
            )
        except Exception as e:
            raise e
