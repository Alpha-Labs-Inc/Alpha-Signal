import requests

from alphasignal.database.db import SQLiteDB
from alphasignal.models.constants import USDC_MINT_ADDRESS

response = requests.get(
    "https://api.dexscreener.com/token-pairs/v1/{chainId}/{tokenAddress}",
    headers={},
)
data = response.json()


class DexscreenerClient:
    BASE_URL = "https://api.dexscreener.com/tokens/v1"
    TOKEN_PAIRS_BASE_URL = "https://api.dexscreener.com/token-pairs/v1"
    CHAIN_ID = "solana"

    def __init__(self):
        self.sql_db = SQLiteDB()

    async def get_token_pairs(self, token_address: str):
        """
        Fetches token pair data from the Dexscreener API.

        :param chain_id: The blockchain chain ID
        :param token_address: The token contract address
        :return: JSON response with token pair details or None if request fails
        """
        url = f"{self.BASE_URL}/{self.CHAIN_ID}/{token_address}"

        try:
            token_data = self.sql_db.get_token_info(mint_address=token_address)
            response = requests.get(url, headers={})
            data = response.json()
            token_info = data[0]
            if token_data is None:
                if token_address == USDC_MINT_ADDRESS:
                    self.sql_db.add_token_info(
                        token_address,
                        "USD Coin",
                        "USDC",
                        "https://cryptologos.cc/logos/usd-coin-usdc-logo.png?v=040",
                    )
                else:
                    result = {
                        "image_url": token_info.get("info", {}).get("imageUrl"),
                        "base_token_symbol": token_info.get("baseToken", {}).get(
                            "symbol"
                        ),
                        "name": token_info.get("baseToken", {}).get("name"),
                    }
                    # Store data in database
                    self.sql_db.add_token_info(
                        token_address,
                        result["name"],
                        result["base_token_symbol"],
                        result["image_url"],
                    )
                token_data = self.sql_db.get_token_info(mint_address=token_address)

            result = {
                "mint_address": token_address,
                "image": token_data.image,
                "token_ticker": token_data.ticker,
                "token_name": token_data.name,
                "priceUsd": float(token_info.get("priceUsd", None)),
                "h24": float(token_info.get("priceChange", {}).get("h24"))
                if token_info.get("priceChange", {}).get("h24") is not None
                else None,
                "h6": float(token_info.get("priceChange", {}).get("h6"))
                if token_info.get("priceChange", {}).get("h6") is not None
                else None,
                "h1": float(token_info.get("priceChange", {}).get("h1"))
                if token_info.get("priceChange", {}).get("h1") is not None
                else None,
                "m5": float(token_info.get("priceChange", {}).get("m5"))
                if token_info.get("priceChange", {}).get("m5") is not None
                else None,
            }
            return result
        except Exception as e:
            raise Exception(f"Error fetching data: {e}")
