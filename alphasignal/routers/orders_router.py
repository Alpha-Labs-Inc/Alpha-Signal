from fastapi import APIRouter

from alphasignal.models.enums import OrderStatus, SellMode, SellType
from alphasignal.schemas.requests.add_order_request import AddOrderRequest
from alphasignal.schemas.responses.orders_response import OrdersResponse, OrderResponse
from alphasignal.services.order_manager import (
    OrderManager,
    TokenBalanceNotAvalible,
    TokenNotFoundError,
)

router = APIRouter()


@router.get("/orders/{status}", response_model=OrdersResponse)
async def get_tracked_orders(status: int):
    order_manager = OrderManager()
    orders_return = []
    tracked_orders = order_manager.get_orders(OrderStatus(status))

    for order in tracked_orders:
        current_order = OrderResponse(
            id=order.id,
            mint_address=order.mint_address,
            last_price_max=order.last_price_max,
            sell_mode=order.sell_mode.value,
            sell_value=order.sell_value,
            sell_type=order.sell_type.value,
            time_added=order.time_added,
            balance=order.balance,
            status=order.status.value,
            profit=order.profit,
            slippage=order.slippage,
        )
        orders_return.append(current_order)

    return OrdersResponse(orders=orders_return)


@router.post("/orders/add", response_model=str)
async def add_order(request: AddOrderRequest):
    order_manager = OrderManager()
    tokens = await order_manager.wallet.get_tokens()
    token = next((t for t in tokens if t.mint_address == request.mint_address), None)

    if not token:
        raise TokenNotFoundError(
            f"Token with mint address '{request.mint_address}' not found in wallet'."
        )

    remaining_balance = order_manager.get_remaining_trackable_balance(
        request.mint_address, token.balance
    )

    if request.balance > remaining_balance:
        raise TokenBalanceNotAvalible(
            f"Token with mint address '{request.mint_address}' only has an avalible balance of {remaining_balance}'."
        )

    id = order_manager.add_order(
        request.mint_address,
        SellMode(request.sell_mode),
        request.sell_value,
        SellType(request.sell_type),
        request.balance,
        token.value,
        request.slippage,
    )

    return id


@router.get("/orders/balance/{mint_address}", response_model=float)
async def get_avalible_balance(mint_address: str):
    order_manager = OrderManager()
    tokens = await order_manager.wallet.get_tokens()
    token = next((t for t in tokens if t.mint_address == mint_address), None)

    if not token:
        raise TokenNotFoundError(
            f"Token with mint address '{mint_address}' not found in wallet'."
        )

    remaining_balance = order_manager.get_remaining_trackable_balance(
        mint_address, token.balance
    )

    return remaining_balance


@router.delete("/orders/cancel/{order_id}", response_model=bool)
async def cancel_order(order_id: str):
    order_manager = OrderManager()
    order_manager.cancel_order(order_id)

    return True


@router.post("/orders/process", response_model=bool)
async def process_orders():
    order_manager = OrderManager()
    await order_manager.process_orders()
    return True
