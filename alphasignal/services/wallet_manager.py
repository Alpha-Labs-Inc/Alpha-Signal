import asyncio
from typing import List
import base58
import os
import json
from solders.keypair import Keypair

from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.models.wallet import Wallet
from alphasignal.models.wallet_token import WalletToken
from alphasignal.schemas.responses.wallet_value_response import WalletValueResponse

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
            jupiter_client = JupiterClient()
            sol_bal = solana_client.get_sol_balance(self.wallet)
            response = solana_client.get_owner_token_accounts(self.wallet)
            if not response.value and sol_bal == 0:
                return []
            solana_mint = "So11111111111111111111111111111111111111112"
            tokens = []
            for token_info in response.value:
                mint_address = token_info.account.data.parsed["info"]["mint"]
                tokens.append(
                    WalletToken(
                        mint_address=mint_address,
                        balance=token_info.account.data.parsed["info"]["tokenAmount"][
                            "uiAmount"
                        ],
                        token_name="",
                        value=await jupiter_client.fetch_token_value(mint_address),
                    )
                )
        except Exception as e:
            raise e

        tokens.append(
            WalletToken(
                mint_address=solana_mint,
                balance=sol_bal,
                token_name="Solana",
                value=await jupiter_client.fetch_token_value(solana_mint),
            )
        )

        return tokens

    async def get_wallet_value(self):
        tokens = await self.get_tokens()
        total_value = 0.0
        if not tokens:
            return

        for token in tokens:
            wallet_value = token.balance * token.value
            total_value += wallet_value
        return WalletValueResponse(wallet_tokens=tokens, total_value=total_value)
