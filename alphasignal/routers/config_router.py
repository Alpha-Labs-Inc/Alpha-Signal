from fastapi import APIRouter

from alphasignal.models.configs import AutoBuyConfig, AutoSellConfig, BaseSellConfig
from alphasignal.models.constants import (
    AUTO_BUY_CONFIG_PATH,
    AUTO_SELL_CONFIG_PATH,
    BASE_SELL_CONFIG_PATH,
)
from alphasignal.models.enums import AmountType, BuyType, SellMode, SellType
from alphasignal.schemas.requests.auto_buy_config_request import AutoBuyConfigRequest
from alphasignal.schemas.requests.auto_sell_config_request import AutoSellConfigRequest
from alphasignal.schemas.requests.base_sell_config_request import BaseSellConfigRequest
from alphasignal.schemas.responses.auto_buy_config_response import AutoBuyConfigResponse
from alphasignal.schemas.responses.auto_sell_config_response import (
    AutoSellConfigResponse,
)
from alphasignal.schemas.responses.base_sell_config_response import (
    BaseSellConfigResponse,
)
from alphasignal.utils.utils import load_config, update_config

router = APIRouter()


@router.get("/config/auto-buy", response_model=AutoBuyConfigResponse)
async def get_auto_buy_config():
    buy_config = load_config(AUTO_BUY_CONFIG_PATH, AutoBuyConfig)

    response = AutoBuyConfigResponse(
        buy_type=buy_config.buy_type.value,
        amount_type=buy_config.amount_type.value,
        amount=buy_config.amount,
        slippage=buy_config.slippage,
    )

    return response


@router.get("/config/auto-sell", response_model=AutoSellConfigResponse)
async def get_auto_sell_config():
    sell_config = load_config(AUTO_SELL_CONFIG_PATH, AutoSellConfig)

    response = AutoSellConfigResponse(
        sell_mode=sell_config.sell_mode.value,
        sell_type=sell_config.sell_type.value,
        sell_value=sell_config.sell_value,
        slippage=sell_config.slippage,
    )
    return response


@router.get("/config/sell", response_model=BaseSellConfigResponse)
async def get_base_sell_config():
    sell_config = load_config(BASE_SELL_CONFIG_PATH, BaseSellConfig)

    response = BaseSellConfigResponse(
        sell_type=sell_config.sell_type.value,
        slippage=sell_config.slippage,
    )

    return response


@router.post("/config/auto-buy", response_model=bool)
async def update_auto_buy_config(request: AutoBuyConfigRequest):
    AutoBuyConfig(
        buy_type=BuyType(request.buy_type),
        amount_type=AmountType(request.amount_type),
        amount=request.amount,
        slippage=request.amount,
    )

    update_config(AUTO_BUY_CONFIG_PATH, request.model_dump())

    return True


@router.post("/config/auto-sell", response_model=bool)
async def update_auto_sell_config(request: AutoSellConfigRequest):
    AutoSellConfig(
        sell_mode=SellMode(request.sell_mode),
        sell_type=SellType(request.sell_type),
        sell_value=request.sell_value,
        slippage=request.slippage,
    )

    update_config(AUTO_SELL_CONFIG_PATH, request.model_dump())
    return True


@router.post("/config/sell", response_model=bool)
async def update_base_sell_config(request: BaseSellConfigRequest):
    BaseSellConfig(sell_type=SellType(request.sell_type), slippage=request.slippage)

    update_config(BASE_SELL_CONFIG_PATH, request.model_dump())

    return True
