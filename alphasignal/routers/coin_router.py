from fastapi import APIRouter

from alphasignal.models.enums import SellMode, SellType
from alphasignal.schemas.requests.add_coin_request import AddCoinRequest
from alphasignal.schemas.responses.coins_response import CoinsResponse, CoinResponse
from alphasignal.services.coin_manager import (
    CoinManager,
    TokenBalanceNotAvalible,
    TokenNotFoundError,
)

router = APIRouter()

coin_manager = CoinManager()


@router.get("/coin/tracked", response_model=CoinsResponse)
async def get_tracked_coins():
    coins_return = []
    tracked_coins = coin_manager.get_tracked_coins()

    for coin in tracked_coins:
        current_coin = CoinResponse(
            id=coin.id,
            mint_address=coin.mint_address,
            last_price_max=coin.last_price_max,
            sell_mode=coin.sell_mode.value,
            sell_value=coin.sell_value,
            sell_type=coin.sell_type.value,
            time_added=coin.time_added,
            balance=coin.balance,
        )
        coins_return.append(current_coin)

    return CoinsResponse(coins=coins_return)


@router.post("/coin/add", response_model=str)
async def add_coin(request: AddCoinRequest):
    tokens = coin_manager.wallet.get_tokens()
    token = next((t for t in tokens if t.mint_address == request.mint_address), None)

    if not token:
        raise TokenNotFoundError(
            f"Token with mint address '{request.mint_address}' not found in wallet'."
        )

    remaining_balance = coin_manager.get_remaining_trackable_balance(
        request.mint_address, token.balance
    )

    if request.balance < remaining_balance:
        raise TokenBalanceNotAvalible(
            f"Token with mint address '{request.mint_address}' only has an avalible balance of {remaining_balance}'."
        )

    id = coin_manager.add_coin(
        request.mint_address,
        SellMode(request.sell_mode),
        request.sell_value,
        SellType(request.sell_type),
        request.balance,
        token.value,
    )

    return id


@router.get("/coin/balance/{mint_address}", response_model=float)
async def get_avalible_balance(mint_address: str):
    tokens = coin_manager.wallet.get_tokens()
    token = next((t for t in tokens if t.mint_address == mint_address), None)

    if not token:
        raise TokenNotFoundError(
            f"Token with mint address '{mint_address}' not found in wallet'."
        )

    remaining_balance = coin_manager.get_remaining_trackable_balance(
        mint_address, token.balance
    )

    return remaining_balance


@router.delete("/coin/remove/{coin_id}", response_model=bool)
async def remove_coin(coin_id: str):
    coin_manager.remove_coin(coin_id)

    return True


@router.post("/coin/process", response_model=bool)
async def process_coins():
    coin_manager.process_coins()
    return True
