from collections import defaultdict
from typing import List

from sqlalchemy import func, desc, asc, cast, Float
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models import UserPurchaseTransaction, UserSaleTransaction, Appearance, PlatformPriceHistory
from app.schemas import UserPortfolio, UserPortfolioItem, PriceHistoryPoint, PortfolioAppearance


def get_user_portfolio(db: Session, user_id: int, page: int, page_size: int,
                       sort_by: str | None = None, sort_order: str = 'desc'):
    # 1. 购买数据子查询
    purchase_subquery = (
        db.query(
            UserPurchaseTransaction.appearance_id,
            func.sum(UserPurchaseTransaction.quantity).label("total_purchased"),
            func.sum(UserPurchaseTransaction.quantity * UserPurchaseTransaction.unit_price_cents).label("total_spent"),
        )
        .filter(UserPurchaseTransaction.user_id == user_id)
        .group_by(UserPurchaseTransaction.appearance_id)
        .subquery('purchase_subquery')
    )

    # 2. 销售数据子查询
    sale_subquery = (
        db.query(
            UserSaleTransaction.appearance_id,
            func.sum(UserSaleTransaction.quantity).label("total_sold"),
        )
        .filter(UserSaleTransaction.user_id == user_id)
        .group_by(UserSaleTransaction.appearance_id)
        .subquery('sale_subquery')
    )

    # 3. 最新价格查询
    latest_price_subquery = (
        db.query(
            PlatformPriceHistory.appearance_id,
            PlatformPriceHistory.lowest_price_cents.label("price"),
            PlatformPriceHistory.quantity_on_sale,
        )
        .distinct(PlatformPriceHistory.appearance_id)
        .order_by(
            PlatformPriceHistory.appearance_id,
            PlatformPriceHistory.crawled_at.desc()
        )
        .subquery('latest_price_subquery')
    )

    # 4. 计算字段
    quantity = (purchase_subquery.c.total_purchased - func.coalesce(sale_subquery.c.total_sold, 0)).label("quantity")
    average_cost = (
            cast(purchase_subquery.c.total_spent, Float) /
            func.nullif(cast(purchase_subquery.c.total_purchased, Float), 0)
    ).label("average_cost")
    total_investment = (quantity * average_cost).label("total_investment")
    current_market_value = (quantity * func.coalesce(latest_price_subquery.c.price, 0)).label("current_market_value")
    profit_loss = (current_market_value - total_investment).label("profit_loss")

    # 5. 基础查询（用于计算总数）
    base_query = (
        db.query(Appearance.id)
        .join(purchase_subquery, Appearance.id == purchase_subquery.c.appearance_id)
        .outerjoin(sale_subquery, Appearance.id == sale_subquery.c.appearance_id)
        .filter(quantity > 0)
    )

    # 6. 获取总数
    total = base_query.count()

    if total == 0:
        return UserPortfolio(total=0, items=[])

    # 7. 主查询
    query = (
        db.query(
            Appearance,
            quantity,
            average_cost,
            total_investment,
            current_market_value,
            profit_loss
        )
        .join(purchase_subquery, Appearance.id == purchase_subquery.c.appearance_id)
        .outerjoin(sale_subquery, Appearance.id == sale_subquery.c.appearance_id)
        .outerjoin(latest_price_subquery, Appearance.id == latest_price_subquery.c.appearance_id)
        .filter(quantity > 0)
        .options(
            joinedload(Appearance.appearance_types),
            joinedload(Appearance.appearance_aliases)
        )
    )

    # 8. 排序
    sort_column_map = {
        "quantity": quantity,
        "total_investment": total_investment,
        "profit_loss": profit_loss,
        "current_market_value": current_market_value,
        # "name": Appearance.name,
    }

    if sort_by and sort_by in sort_column_map:
        sort_column = sort_column_map[sort_by]
        order_func = asc if sort_order == 'asc' else desc
        query = query.order_by(order_func(sort_column))
    else:
        # 默认排序
        query = query.order_by(desc(total_investment))

    # 9. 分页
    portfolio_items_data = query.offset((page - 1) * page_size).limit(page_size).all()

    # 10. 批量获取价格历史（优化为单次查询）
    appearance_ids = [item[0].id for item in portfolio_items_data]
    price_histories_map = _get_price_histories_batch(db, appearance_ids, settings.PRICE_HISTORY_FETCH_COUNT)

    # 11. 构建结果
    items = []
    for appearance, qty, avg_cost, total_inv, current_mv, pl in portfolio_items_data:
        # 安全的百分比计算
        profit_loss_percentage = (pl / total_inv * 100) if total_inv and total_inv > 0 else 0

        portfolio_appearance = PortfolioAppearance.model_validate(appearance)

        items.append(
            UserPortfolioItem(
                appearance=portfolio_appearance,
                quantity=qty or 0,
                average_cost=avg_cost or 0,
                total_investment=total_inv or 0,
                current_market_value=current_mv or 0,
                profit_loss=pl or 0,
                profit_loss_percentage=profit_loss_percentage,
                price_history=price_histories_map.get(appearance.id, []),
            )
        )

    return UserPortfolio(total=total, items=items)


def _get_price_histories_batch(db: Session, appearance_ids: List[int],
                               limit: int = settings.PRICE_HISTORY_FETCH_COUNT) -> dict:
    """批量获取价格历史"""
    if not appearance_ids:
        return {}

    price_history_subquery = (
        db.query(
            PlatformPriceHistory,
            func.row_number().over(
                partition_by=PlatformPriceHistory.appearance_id,
                order_by=PlatformPriceHistory.crawled_at.desc()
            ).label('rn')
        )
        .filter(PlatformPriceHistory.appearance_id.in_(appearance_ids))
        .subquery()
    )

    price_history_data = (
        db.query(price_history_subquery)
        .filter(price_history_subquery.c.rn <= limit)
        .order_by(
            price_history_subquery.c.appearance_id,
            price_history_subquery.c.crawled_at.desc()
        )
        .all()
    )

    price_histories_map = defaultdict(list)
    for row in price_history_data:
        price_histories_map[row.appearance_id].append(
            PriceHistoryPoint(
                price=row.lowest_price_cents,
                quantity_on_sale=row.quantity_on_sale,
                crawled_at=row.crawled_at,
            )
        )

    return price_histories_map
