from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import UserPurchaseTransaction, UserSaleTransaction, PlatformPriceHistory
from app.schemas import UserStats


def get_user_stats(db: Session, user_id: int) -> UserStats:
    # 1. Calculate average cost for each purchased appearance
    purchase_summary = db.query(
        UserPurchaseTransaction.appearance_id,
        func.sum(UserPurchaseTransaction.quantity).label("total_purchased"),
        func.sum(UserPurchaseTransaction.quantity * UserPurchaseTransaction.unit_price_cents).label("total_cost"),
        (func.sum(UserPurchaseTransaction.quantity * UserPurchaseTransaction.unit_price_cents) /
         func.sum(UserPurchaseTransaction.quantity)).label("average_cost_cents")
    ).filter(UserPurchaseTransaction.user_id == user_id).group_by(UserPurchaseTransaction.appearance_id).subquery()

    # 2. Summarize sales
    sale_summary = db.query(
        UserSaleTransaction.appearance_id,
        func.sum(UserSaleTransaction.quantity).label("total_sold"),
        func.sum(UserSaleTransaction.quantity * UserSaleTransaction.unit_price_cents -
                 UserSaleTransaction.platform_fee_cents).label("total_revenue")
    ).filter(UserSaleTransaction.user_id == user_id).group_by(UserSaleTransaction.appearance_id).subquery()

    # 3. Calculate Realized PnL
    realized_pnl_query = db.query(
        func.sum(sale_summary.c.total_revenue).label("total_revenue"),
        func.sum(sale_summary.c.total_sold * purchase_summary.c.average_cost_cents).label("total_cogs")
    ).join(purchase_summary, sale_summary.c.appearance_id == purchase_summary.c.appearance_id).first()

    realized_pnl_cents = 0
    if realized_pnl_query and realized_pnl_query.total_revenue is not None:
        total_revenue = realized_pnl_query.total_revenue or 0
        total_cogs = realized_pnl_query.total_cogs or 0
        realized_pnl_cents = total_revenue - total_cogs

    # 4. Calculate current holdings and their value
    holdings_query = db.query(
        purchase_summary.c.appearance_id,
        (purchase_summary.c.total_purchased - func.coalesce(sale_summary.c.total_sold, 0)).label("held_quantity"),
        purchase_summary.c.average_cost_cents
    ).outerjoin(sale_summary, purchase_summary.c.appearance_id == sale_summary.c.appearance_id).filter(
        (purchase_summary.c.total_purchased - func.coalesce(sale_summary.c.total_sold, 0)) > 0
    ).subquery()

    # 5. Get the latest price for each appearance
    latest_prices = db.query(
        PlatformPriceHistory.appearance_id,
        func.max(PlatformPriceHistory.crawled_at).label("max_crawled_at")
    ).group_by(PlatformPriceHistory.appearance_id).subquery()

    current_prices = db.query(
        PlatformPriceHistory.appearance_id,
        PlatformPriceHistory.lowest_price_cents
    ).join(latest_prices, (PlatformPriceHistory.appearance_id == latest_prices.c.appearance_id) &
           (PlatformPriceHistory.crawled_at == latest_prices.c.max_crawled_at)).subquery()

    # 6. Calculate total investment and market value for holdings
    stats = db.query(
        func.sum(holdings_query.c.held_quantity).label("total_appearances_held"),
        func.sum(holdings_query.c.held_quantity * holdings_query.c.average_cost_cents).label("total_investment_cents"),
        func.sum(holdings_query.c.held_quantity * func.coalesce(current_prices.c.lowest_price_cents, 0)).label(
            "current_market_value_cents")
    ).outerjoin(current_prices, holdings_query.c.appearance_id == current_prices.c.appearance_id).first()

    total_appearances_held = stats.total_appearances_held or 0
    total_investment_cents = stats.total_investment_cents or 0
    current_market_value_cents = stats.current_market_value_cents or 0

    # 7. Calculate Estimated PnL
    estimated_pnl_cents = current_market_value_cents - total_investment_cents
    estimated_pnl_percentage = (estimated_pnl_cents / total_investment_cents) * 100 if total_investment_cents > 0 else 0

    return UserStats(
        total_appearances_held=int(total_appearances_held),
        total_investment_cents=int(total_investment_cents),
        current_market_value_cents=int(current_market_value_cents),
        estimated_pnl_cents=int(estimated_pnl_cents),
        estimated_pnl_percentage=estimated_pnl_percentage,
        realized_pnl_cents=int(realized_pnl_cents)
    )
