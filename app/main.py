from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api import auth, user_stats, user_portfolio, appearance, appearance_type, appearance_alias, platform, user_purchase_transaction, user_sale_transaction, platform_price_history, watchlist, watchlist_item
from app.core.exceptions import BusinessException

app = FastAPI()


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.result_code.status_code,
        content={"code": exc.result_code.code, "message": exc.result_code.message},
    )


# 用户类
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user_stats.router, prefix="/me", tags=["users"])
app.include_router(user_portfolio.router, prefix="/me", tags=["users"])

# Appearance 类
app.include_router(appearance.router, prefix="/appearances", tags=["appearances"])
app.include_router(appearance_type.router, prefix="/appearance-types", tags=["appearance-types"])
app.include_router(appearance_alias.router, prefix="/appearance-aliases", tags=["appearance-aliases"])

# Platform 与交易类
app.include_router(platform.router, prefix="/platforms", tags=["platforms"])
app.include_router(user_purchase_transaction.router, prefix="/user-purchase-transactions", tags=["transactions"])
app.include_router(user_sale_transaction.router, prefix="/user-sale-transactions", tags=["transactions"])
app.include_router(platform_price_history.router, prefix="/platform-price-histories", tags=["platforms"])

# Watchlist 类
app.include_router(watchlist.router, prefix="/watchlists", tags=["watchlists"])
app.include_router(watchlist_item.router, prefix="/watchlist-items", tags=["watchlists"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Astra API"}
