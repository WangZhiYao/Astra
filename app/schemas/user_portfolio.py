from typing import List

from pydantic import BaseModel, ConfigDict

from .appearance import Appearance
from .platform_price_history import PlatformPriceHistoryPoint


class UserPortfolioItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    appearance: Appearance
    quantity: int
    average_cost: float
    total_investment: float
    current_market_value: float
    profit_loss: float
    profit_loss_percentage: float
    price_histories: List[PlatformPriceHistoryPoint] = []
