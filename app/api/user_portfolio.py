from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.response import Response
from app.crud import crud_user_portfolio
from app.db.database import get_db
from app.models import User
from app.schemas import UserPortfolio

router = APIRouter()


@router.get("/portfolio", response_model=Response[UserPortfolio])
def read_user_portfolio(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        page: int = 1,
        page_size: int = 10,
        sort_by: str | None = Query(
            None, enum=["quantity", "total_investment", "profit_loss", "current_market_value"]),
        sort_order: str = Query('desc', enum=["asc", "desc"]),
):
    user_portfolio = crud_user_portfolio.get_user_portfolio(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return Response(data=user_portfolio)
