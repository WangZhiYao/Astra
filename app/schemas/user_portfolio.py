from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas import Appearance


class PriceHistoryPoint(BaseModel):
    price: float
    quantity_on_sale: Optional[int] = None
    crawled_at: datetime

    class Config:
        from_attributes = True


class UserPortfolioItem(BaseModel):
    appearance: Appearance
    quantity: int
    average_cost: float
    total_investment: float
    current_market_value: float
    profit_loss: float
    profit_loss_percentage: float
    price_histories: List[PriceHistoryPoint] = []

    class Config:
        from_attributes = True


class UserPortfolio(BaseModel):
    total: int
    items: List[UserPortfolioItem]
