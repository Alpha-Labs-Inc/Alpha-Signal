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
def get_wallet_value():
    try:
        return retrieve_wallet_value()
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@router.get("/create-wallet")
async def get_create_wallet():
    try:
        wallet = await create_wallet()
        return PayloadWallet(
            public_key=wallet.public_key,
            wallet_keypair=wallet.wallet_keypair,
        )
    except Exception as e:
        raise HTTPException(status_code=406, detail=e)


@router.get("/load-wallet")
def get_load_wallet():
    try:
        wallet = load_wallet()
        return PayloadWallet(
            public_key=wallet.public_key,
            wallet_keypair=wallet.wallet_keypair,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@router.post("/swap_coins")
def swap_coins(request: PayQuoteRequest) -> SwapConfirmation:
    try:
        wallet = load_wallet()
        result = swap_tokens(
            request.from_token_mint_address,
            request.to_token_mint_address,
            request.amt,
            wallet,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@router.post("/swap-quote")
def swap_quote(request: PayQuoteRequest) -> QuoteOutput:
    try:
        result = get_swap_quote(
            request.from_token_mint_address, request.to_token_mint_address, request.amt
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)


@router.post("/add-funds")
def add_funds(fund_request: FundRequest) -> FundPayload:
    try:
        wallet = load_wallet()
        result = fund(
            amt=fund_request.amt,
            wallet=wallet,
            funding_key=fund_request.funding_private_key,
        )
        return FundPayload(funded_wallet_public_key=result[0], amt=result[1])
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)
