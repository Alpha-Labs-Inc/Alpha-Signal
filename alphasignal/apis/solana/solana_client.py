import os
import base58
from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from tenacity import retry, stop_after_attempt
from alphasignal.models.wallet import Wallet
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams
from solders.keypair import Keypair
from solders.message import Message

from alphasignal.models.mint_token import MintToken


class SolanaClient:
    def __init__(self):
        self.solana_cluster_url = os.getenv("SOLANA_CLUSTER_URL")
        self.client = Client(self.solana_cluster_url)

    @retry(stop=stop_after_attempt(3))
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

    @retry(stop=stop_after_attempt(3))
    async def fund_wallet(
        self, recipient_pubkey: Pubkey, amount: float, from_private_key: str
    ):
        """
        Fund a Solana wallet using `solders`.

        Args:
            to_public_key (str): The public key of the recipient wallet in base58-encoded string.
            amount (float): Amount of SOL to transfer.

        Returns:
            str: Transaction signature.
        """
        try:
            # Create client and sender's keypair
            client = AsyncClient(self.solana_cluster_url)
            secret_key = base58.b58decode(from_private_key)
            sender_keypair = Keypair.from_seed(secret_key)
            sender_pubkey = sender_keypair.pubkey()

            min_balance_result = await client.get_minimum_balance_for_rent_exemption(
                0
            )  # 0 bytes for default account
            if min_balance_result.value is None:
                raise Exception("Failed to fetch minimum balance for rent exemption")
            min_balance_for_rent = min_balance_result.value

            # Ensure transfer amount covers rent exemption
            lamports = int(amount * 1e9)
            if lamports < min_balance_for_rent:
                raise ValueError(
                    f"The transfer amount must be at least {min_balance_for_rent / 1e9} SOL to cover rent exemption"
                )

            # Get recent blockhash
            recent_blockhash_result = await client.get_latest_blockhash()
            if not recent_blockhash_result.value:
                raise Exception("Failed to fetch the latest blockhash")
            recent_blockhash = recent_blockhash_result.value.blockhash

            # Create a transfer instruction
            transfer_instruction = transfer(
                TransferParams(
                    from_pubkey=sender_pubkey,
                    to_pubkey=recipient_pubkey,
                    lamports=lamports,
                )
            )

            # Create the message for the transaction
            message = Message.new_with_blockhash(
                [transfer_instruction], sender_pubkey, recent_blockhash
            )

            # Create the transaction
            transaction = Transaction(
                from_keypairs=[sender_keypair],
                message=message,
                recent_blockhash=recent_blockhash,
            )

            # Send the transaction
            response = await client.send_transaction(transaction)
            await client.close()

            # Return transaction signature
            return str(recipient_pubkey), amount
        except Exception as e:
            return f"An error occurred: {str(e)}"
