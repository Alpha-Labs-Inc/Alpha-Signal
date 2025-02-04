import asyncio
from typing import List
import base58
import os
import json
from solders.keypair import Keypair

from alphasignal.apis.dexscreener.dexscreener_client import DexscreenerClient
from alphasignal.apis.jupiter.jupiter_client import JupiterClient
from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.database.db import SQLiteDB
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
        sql_db = SQLiteDB()
        try:
            solana_client = SolanaClient()
            jupiter_client = JupiterClient()
            dexscreener_client = DexscreenerClient()

            sol_bal = solana_client.get_sol_balance(self.wallet)
            response = solana_client.get_owner_token_accounts(self.wallet)
            if not response.value and sol_bal == 0:
                return []
            solana_mint = "So11111111111111111111111111111111111111112"
            tokens = []
            for token_info in response.value:
                mint_address = token_info.account.data.parsed["info"]["mint"]
                token_data = sql_db.get_token_info(mint_address)
                if token_data is None:
                    token_data = dexscreener_client.get_token_pairs(mint_address)
                val = await jupiter_client.fetch_token_value(mint_address)
                bal = float(
                    token_info.account.data.parsed["info"]["tokenAmount"]["uiAmount"]
                )
                usd_bal = float(val) * float(bal)
                if token_data is None:
                    tokens.append(
                        WalletToken(
                            mint_address=mint_address,
                            balance=bal,
                            token_name="",
                            value=val,
                            usd_balance=usd_bal,
                        )
                    )
                else:
                    tokens.append(
                        WalletToken(
                            token_name=token_data.name,
                            token_ticker=token_data.ticker,
                            image=token_data.image,
                            mint_address=mint_address,
                            balance=bal,
                            value=val,
                            usd_balance=usd_bal,
                        )
                    )
            sol_info = sql_db.get_token_info(solana_mint)
            if sol_info is None:
                sol_info = dexscreener_client.get_token_pairs(solana_mint)
            if sol_info is None:
                val = await jupiter_client.fetch_token_value(solana_mint)
                usd_bal = float(val) * float(sol_bal)
                tokens.append(
                    WalletToken(
                        mint_address=solana_mint,
                        balance=sol_bal,
                        token_name="Solana",
                        value=float(val),
                        usd_balance=usd_bal,
                    )
                )
            else:
                val = await jupiter_client.fetch_token_value(solana_mint)
                usd_bal = float(val) * float(sol_bal)
                tokens.append(
                    WalletToken(
                        token_ticker=sol_info.ticker,
                        image=sol_info.image,
                        mint_address=solana_mint,
                        balance=sol_bal,
                        token_name="Solana",
                        value=val,
                        usd_balance=usd_bal,
                    )
                )
        except Exception as e:
            raise e

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
