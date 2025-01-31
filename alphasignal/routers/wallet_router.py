from alphasignal.schemas.responses.fund_response import FundResponse
from alphasignal.schemas.requests.fund_request import FundRequest
from alphasignal.schemas.responses.wallet_response import WalletResponse
from alphasignal.schemas.requests.swapquote_request import SwapQuoteRequest
from alphasignal.schemas.responses.quote_response import QuoteResponse
from alphasignal.schemas.responses.swap_confirmation_response import (
    SwapConfirmationResponse,
)
from alphasignal.services.service import (
    create_wallet,
    fund,
    get_swap_quote,
    load_wallet,
    retrieve_wallet_value,
    swap_tokens,
)
from fastapi import APIRouter, HTTPException


router = APIRouter()


@router.get("/wallet-value")
async def get_wallet_value():
    try:
        wallet = load_wallet()
        return await retrieve_wallet_value(wallet=wallet)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/create-wallet")
async def get_create_wallet():
    try:
        wallet = create_wallet()
        return WalletResponse(
            public_key=str(wallet.wallet.public_key),
        )
    except Exception as e:
        raise HTTPException(status_code=406, detail=str(e))


@router.get("/load-wallet")
def get_load_wallet():
    try:
        wallet = load_wallet()
        return WalletResponse(
            public_key=str(wallet.wallet.public_key),
        )
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))


@router.post("/swap-coins")
async def swap_coins(request: SwapQuoteRequest) -> SwapConfirmationResponse:
    try:
        wallet = load_wallet()
        result = await swap_tokens(
            request.from_token_mint_address,
            request.to_token_mint_address,
            request.amt,
            wallet,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/swap-quote")
async def swap_quote(request: SwapQuoteRequest) -> QuoteResponse:
    try:
        result = await get_swap_quote(
            request.from_token_mint_address, request.to_token_mint_address, request.amt
        )
        return result
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))


@router.post("/add-funds")
async def add_funds(fund_request: FundRequest) -> FundResponse:
    try:
        wallet = load_wallet()
        result = await fund(
            amt=fund_request.amt,
            wallet=wallet,
            funding_key=fund_request.funding_private_key,
        )
        return FundResponse(funded_wallet_public_key=result[0], amt=result[1])
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))
