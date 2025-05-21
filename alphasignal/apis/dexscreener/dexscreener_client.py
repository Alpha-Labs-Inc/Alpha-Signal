import logging
import requests

from alphasignal.database.db import SQLiteDB
from alphasignal.models.constants import USDC_MINT_ADDRESS

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

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
                        "https://s2.coinmarketcap.com/static/img/coins/64x64/3408.png",
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
            logging.error(f"Error fetching token data: {e}")
            raise Exception(f"Error fetching data: {e}")

    async def get_top_volume_mint_address(self, ticker: str) -> str:
        """
        Searches DexScreener for all pairs matching `ticker` and returns
        the mint/contract address of the token (base or quote) with the
        highest 24-hour volume.
        """
        if "$" in ticker:
            raise ValueError("Ticker symbol should not contain '$'")

        # 1) Call the DexScreener search endpoint
        url = f"https://api.dexscreener.com/latest/dex/search?q={ticker}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error if request failed

        # Parse the JSON response
        data = response.json()
        pairs = data.get("pairs", [])

        # 2) Filter out pairs that actually match the ticker
        #    in baseToken or quoteToken
        matching_pairs = []
        for pair in pairs:
            base_symbol = pair.get("baseToken", {}).get("symbol")
            quote_symbol = pair.get("quoteToken", {}).get("symbol")

            if base_symbol == ticker or quote_symbol == ticker:
                matching_pairs.append(pair)

        if not matching_pairs:
            raise ValueError(f"No pairs found for ticker: {ticker}")

        # 3) Find the pair with the highest 24-hour volume
        top_pair = None
        max_volume = 0.0

        for pair in matching_pairs:
            # volume.h24 is in USD
            vol_24h = pair.get("volume", {}).get("h24", 0.0)
            if vol_24h > max_volume:
                max_volume = vol_24h
                top_pair = pair

        if not top_pair:
            raise ValueError(f"No valid pair with volume found for ticker: {ticker}")

        # 4) Retrieve the mint address from whichever side matches the ticker
        base_token_info = top_pair.get("baseToken", {})
        quote_token_info = top_pair.get("quoteToken", {})

        if base_token_info.get("symbol") == ticker:
            return base_token_info.get("address")
        else:
            return quote_token_info.get("address")
