import struct

from alphasignal.apis.solana.solana_client import SolanaClient
from alphasignal.models.mint_token import MintToken
from solders.pubkey import Pubkey
from alphasignal.models.constants import USDC_MINT_ADDRESS


class TokenManager:
    def __init__(self, token_mint_address: str):
        self.token = MintToken(
            token_mint_address=token_mint_address,
            token_mint_pubkey=Pubkey.from_string(token_mint_address),
        )

    async def get_token_decimals(self):
        try:
            solana_client = SolanaClient()
            account_info = await solana_client.get_acc_info(self.token)

            return struct.unpack_from("B", account_info.data, offset=44)[0]
        except Exception as e:
            raise Exception(f"Could not gather token decimals: {e}")
