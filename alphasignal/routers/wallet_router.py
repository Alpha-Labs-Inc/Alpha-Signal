from alphasignal.schemas.fund_payload import FundPayload
from alphasignal.schemas.fund_request import FundRequest
from alphasignal.schemas.payload_wallet import PayloadWallet
from alphasignal.schemas.payquote_request import PayQuoteRequest
from alphasignal.schemas.quote_output import QuoteOutput
from alphasignal.schemas.swap_confirmation import SwapConfirmation
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
        return PayloadWallet(
            public_key=str(wallet.wallet.public_key),
            wallet_keypair=str(wallet.wallet.wallet_keypair),
        )
    except Exception as e:
        raise HTTPException(status_code=406, detail=str(e))


@router.get("/load-wallet")
def get_load_wallet():
    try:
        wallet = load_wallet()
        return PayloadWallet(
            public_key=str(wallet.wallet.public_key),
            wallet_keypair=str(wallet.wallet.wallet_keypair),
        )
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))


@router.post("/swap-coins")
async def swap_coins(request: PayQuoteRequest) -> SwapConfirmation:
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
async def swap_quote(request: PayQuoteRequest) -> QuoteOutput:
    try:
        result = await get_swap_quote(
            request.from_token_mint_address, request.to_token_mint_address, request.amt
        )
        return result
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))


@router.post("/add-funds")
async def add_funds(fund_request: FundRequest) -> FundPayload:
    try:
        wallet = load_wallet()
        result = await fund(
            amt=fund_request.amt,
            wallet=wallet,
            funding_key=fund_request.funding_private_key,
        )
        return FundPayload(funded_wallet_public_key=result[0], amt=result[1])
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))
