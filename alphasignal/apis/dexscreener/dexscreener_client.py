import requests

from alphasignal.database.db import SQLiteDB

response = requests.get(
    "https://api.dexscreener.com/token-pairs/v1/{chainId}/{tokenAddress}",
    headers={},
)
data = response.json()


class DexscreenerClient:
    BASE_URL = "https://api.dexscreener.com/tokens/v1"
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
            response = requests.get(url, headers={})
            response.raise_for_status()
            data = response.json()
            if len(data) == 1:
                pair = data[0]
                result = {
                    "image_url": pair.get("info", {}).get("imageUrl"),
                    "base_token_symbol": pair.get("baseToken", {}).get("symbol"),
                    "name": pair.get("baseToken", {}).get("name"),
                }
                # Store data in database
                self.sql_db.add_token_info(
                    token_address,
                    result["name"],
                    result["base_token_symbol"],
                    result["image_url"],
                )

                return self.sql_db.get_token_info(token_address)
            return None
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
