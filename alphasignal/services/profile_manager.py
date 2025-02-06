from typing import List
import uuid
from alphasignal.database.db import SQLiteDB
from alphasignal.models.configs import AutoBuyConfig, AutoSellConfig
from alphasignal.models.constants import AUTO_BUY_CONFIG_PATH, AUTO_SELL_CONFIG_PATH
from alphasignal.models.enums import AmountType, BuyType, Platform, SellMode, SellType
from alphasignal.models.profile import Profile
from alphasignal.utils.utils import load_config


class ProfileManager:
    def __init__(self):
        self.db = SQLiteDB()
        # Load the configurations

    def add_profile(self, platform: Platform, signal: str) -> str:
        self.buy_config = load_config(AUTO_BUY_CONFIG_PATH, AutoBuyConfig)
        self.sell_config = load_config(AUTO_SELL_CONFIG_PATH, AutoSellConfig)

        # Default the rest of the arguments from the configs
        profile_id = self.db.add_profile(
            platform=platform,
            signal=signal,
            buy_type=self.buy_config.buy_type,
            buy_amount_type=self.buy_config.amount_type,
            buy_amount=self.buy_config.amount,
            buy_slippage=self.buy_config.slippage,
            sell_mode=self.sell_config.sell_mode,
            sell_type=self.sell_config.sell_type,
            sell_value=self.sell_config.sell_value,
            sell_slippage=self.sell_config.slippage,
        )
        return profile_id

    def activate_profile(self, profile_id: str) -> None:
        # Activate the profile
        self.db.activate_profile(profile_id)

    def deactivate_profile(self, profile_id: str) -> None:
        # Deactivate the profile
        self.db.deactivate_profile(profile_id)

    def update_profile(
        self,
        profile_id: str,
        buy_type: BuyType,
        buy_amount_type: AmountType,
        buy_amount: float,
        buy_slippage: float,
        sell_mode: SellMode,
        sell_type: SellType,
        sell_value: float,
        sell_slippage: float,
    ) -> None:
        # Update the profile with new configurations
        self.db.update_profile(
            profile_id=profile_id,
            buy_type=buy_type,
            buy_amount_type=buy_amount_type,
            buy_amount=buy_amount,
            buy_slippage=buy_slippage,
            sell_mode=sell_mode,
            sell_type=sell_type,
            sell_value=sell_value,
            sell_slippage=sell_slippage,
        )

    def get_profile(self, platform: str, signal: str) -> Profile:
        profile_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{platform}_{signal}"))
        return self.db.get_profile_data(profile_id)

    def get_profile_by_id(self, profile_id: str) -> Profile:
        return self.db.get_profile_data(profile_id)

    def delete_profile(self, profile_id: str) -> None:
        self.db.delete_profile(profile_id)

    def get_profiles(self) -> List[Profile]:
        return self.db.get_profiles()
