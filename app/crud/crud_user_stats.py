from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models import UserPurchaseTransaction, UserSaleTransaction, PlatformPriceHistory
from app.schemas import UserStats


def get_user_stats(db: Session, user_id: int) -> UserStats:
    # Calculate total investment and quantity of purchased appearances
    purchases = db.query(
        UserPurchaseTransaction.appearance_id,
        func.sum(UserPurchaseTransaction.quantity).label("total_quantity"),
        func.sum(UserPurchaseTransaction.quantity *
                 UserPurchaseTransaction.unit_price_cents).label("total_cost")
    ).filter(UserPurchaseTransaction.user_id == user_id).group_by(UserPurchaseTransaction.appearance_id).subquery()

    # Calculate quantity of sold appearances
    sales = db.query(
        UserSaleTransaction.appearance_id,
        func.sum(UserSaleTransaction.quantity).label("total_quantity")
    ).filter(UserSaleTransaction.user_id == user_id).group_by(UserSaleTransaction.appearance_id).subquery()

    # Calculate current holdings
    holdings = db.query(
        purchases.c.appearance_id,
        (purchases.c.total_quantity -
         func.coalesce(sales.c.total_quantity, 0)).label("held_quantity"),
        (purchases.c.total_cost).label("investment_cents")
    ).outerjoin(sales, purchases.c.appearance_id == sales.c.appearance_id).filter(
        (purchases.c.total_quantity - func.coalesce(sales.c.total_quantity, 0)) > 0
    ).subquery()

    # Get the latest price for each appearance
    latest_prices = db.query(
        PlatformPriceHistory.appearance_id,
        func.max(PlatformPriceHistory.crawled_at).label("max_crawled_at")
    ).group_by(PlatformPriceHistory.appearance_id).subquery()

    current_prices = db.query(
        PlatformPriceHistory.appearance_id,
        PlatformPriceHistory.lowest_price_cents
    ).join(latest_prices, PlatformPriceHistory.appearance_id == latest_prices.c.appearance_id and
           PlatformPriceHistory.crawled_at == latest_prices.c.max_crawled_at).subquery()

    # Calculate total investment and market value
    stats = db.query(
        func.sum(holdings.c.held_quantity).label("total_appearances_held"),
        func.sum(holdings.c.investment_cents).label("total_investment_cents"),
        func.sum(holdings.c.held_quantity * func.coalesce(current_prices.c.lowest_price_cents, 0)).label(
            "current_market_value_cents")
    ).outerjoin(current_prices, holdings.c.appearance_id == current_prices.c.appearance_id).first()

    total_appearances_held = stats.total_appearances_held or 0
    total_investment_cents = stats.total_investment_cents or 0
    current_market_value_cents = stats.current_market_value_cents or 0

    # Calculate realized PnL
    realized_pnl = db.query(func.sum(
        UserSaleTransaction.quantity * UserSaleTransaction.unit_price_cents -
        UserSaleTransaction.platform_fee_cents
    )).filter(UserSaleTransaction.user_id == user_id).scalar() or 0

    # Calculate cost of goods sold
    cogs = db.query(func.sum(
        UserSaleTransaction.quantity * UserPurchaseTransaction.unit_price_cents
    )).join(UserPurchaseTransaction, UserSaleTransaction.appearance_id == UserPurchaseTransaction.appearance_id) \
        .filter(UserSaleTransaction.user_id == user_id).scalar() or 0

    realized_pnl_cents = realized_pnl - cogs

    estimated_pnl_cents = current_market_value_cents - total_investment_cents
    estimated_pnl_percentage = (
        estimated_pnl_cents / total_investment_cents) * 100 if total_investment_cents > 0 else 0

    return UserStats(
        total_appearances_held=total_appearances_held,
        total_investment_cents=total_investment_cents,
        current_market_value_cents=current_market_value_cents,
        estimated_pnl_cents=estimated_pnl_cents,
        estimated_pnl_percentage=estimated_pnl_percentage,
        realized_pnl_cents=realized_pnl_cents
    )
