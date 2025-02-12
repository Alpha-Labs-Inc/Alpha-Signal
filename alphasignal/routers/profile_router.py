from typing import List
from fastapi import APIRouter, HTTPException
from alphasignal.database.db import ProfileNotFoundError
from alphasignal.models.enums import BuyType, AmountType, Platform, SellMode, SellType
from alphasignal.schemas.requests.create_profile import ProfileCreateRequest
from alphasignal.schemas.requests.update_profile_request import ProfileUpdateRequest
from alphasignal.schemas.responses.profile_respones import ProfileResponse
from alphasignal.services.profile_manager import ProfileManager

router = APIRouter()
profile_manager = ProfileManager()


@router.post("/profile", response_model=str)
async def add_profile(request: ProfileCreateRequest):
    """
    Create a new profile with default buy/sell settings.
    """
    profile_id = profile_manager.add_profile(
        Platform(request.platform), request.username
    )
    return profile_id


@router.patch("/profile/{profile_id}/activate", response_model=bool)
async def activate_profile(profile_id: str):
    """
    Activate a profile by its ID.
    """
    profile_manager.activate_profile(profile_id)
    return True


@router.patch("/profile/{profile_id}/deactivate", response_model=bool)
async def deactivate_profile(profile_id: str):
    """
    Deactivate a profile by its ID.
    """
    profile_manager.deactivate_profile(profile_id)
    return True


@router.put("/profile/{profile_id}", response_model=bool)
async def update_profile(profile_id: str, request: ProfileUpdateRequest):
    """
    Update an existing profile with new buy/sell settings.
    """
    profile_manager.update_profile(
        profile_id=profile_id,
        buy_type=BuyType(request.buy_type),
        buy_amount_type=AmountType(request.buy_amount_type),
        buy_amount=request.buy_amount,
        buy_slippage=request.buy_slippage,
        sell_mode=SellMode(request.sell_mode),
        sell_type=SellType(request.sell_type),
        sell_value=request.sell_value,
        sell_slippage=request.sell_slippage,
    )
    return True


@router.get("/profile/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str):
    """
    Retrieve a profile based on platform and username.
    """
    try:
        profile = profile_manager.get_profile_by_id(profile_id)
        return ProfileResponse(
            id=profile.id,
            platform=profile.platform.value,
            username=profile.username,
            is_active=profile.is_active,
            buy_type=profile.buy_type.value,
            buy_amount_type=profile.buy_amount_type.value,
            buy_amount=profile.buy_amount,
            buy_slippage=profile.buy_slippage,
            sell_mode=profile.sell_mode.value,
            sell_type=profile.sell_type.value,
            sell_value=profile.sell_value,
            sell_slippage=profile.sell_slippage,
        )
    except ProfileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Profile not found")


@router.delete("/profile/{profile_id}", response_model=bool)
async def delete_profile(profile_id: str):
    """
    Delete a profile by its ID.
    """
    try:
        profile_manager.delete_profile(profile_id)
    except ProfileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Profile not found")
    return True


@router.get("/profiles", response_model=List[ProfileResponse])
async def get_profiles():
    """
    Retrieve all available profiles.
    """
    profiles = profile_manager.get_profiles()
    return [
        ProfileResponse(
            id=p.id,
            platform=p.platform.value,
            username=p.username,
            is_active=p.is_active,
            buy_type=p.buy_type.value,
            buy_amount_type=p.buy_amount_type.value,
            buy_amount=p.buy_amount,
            buy_slippage=p.buy_slippage,
            sell_mode=p.sell_mode.value,
            sell_type=p.sell_type.value,
            sell_value=p.sell_value,
            sell_slippage=p.sell_slippage,
        )
        for p in profiles
    ]
