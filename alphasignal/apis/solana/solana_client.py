import os
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from alphasignal.models.wallet import Wallet
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey

from alphasignal.models.mint_token import MintToken


class SolanaClient:
    def __init__(self):
        self.solana_cluster_url = os.getenv("SOLANA_CLUSTER_URL")
        self.client = Client(self.solana_cluster_url)

    async def get_acc_info(self, token: MintToken):
        async with AsyncClient(self.solana_cluster_url) as async_client:
            try:
                response = await async_client.get_account_info(token.token_mint_pubkey)
                account_info = response.value

                if account_info is None:
                    raise Exception(
                        f"Invalid or non-existent mint address: {token.token_mint_address}"
                    )
                return account_info

            except Exception as e:
                raise Exception(
                    f"Error fetching decimals for mint address {token.token_mint_address}: {e}"
                )

    def get_owner_token_accounts(self, wallet: Wallet):
        opts = TokenAccountOpts(
            program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        )
        return self.client.get_token_accounts_by_owner_json_parsed(
            wallet.public_key, opts
        )

    def get_sol_balance(self, wallet: Wallet):
        try:
            response = self.client.get_balance(wallet.public_key)
            # Access the 'value' field properly based on the response structure
            sol_balance = response.value / 10**9  # Convert lamports to SOL
            return sol_balance
        except Exception as e:
            raise Exception(
                f"Error fetching SOL balance for wallet {wallet.public_key}: {e}"
            )
