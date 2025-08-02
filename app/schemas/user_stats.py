from pydantic import BaseModel


class UserStats(BaseModel):
    total_appearances_held: int
    total_investment_cents: int
    current_market_value_cents: int
    estimated_pnl_cents: int
    estimated_pnl_percentage: float
    realized_pnl_cents: int

    class Config:
        from_attributes = True
