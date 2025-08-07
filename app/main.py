import logging
import time

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api import auth, user_stats, user_portfolio, appearance, appearance_type, appearance_alias, platform, \
    user_purchase_transaction, user_sale_transaction, platform_price_history, watchlist, watchlist_item
from app.core.exceptions import BusinessException
from app.core.logging_config import setup_logging
from app.core.result_codes import ResultCode

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request details
    logger.info(f"Request: {request.method} {request.url.path} - From: {request.client.host}")

    response = await call_next(request)

    # Log response details
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Response: {response.status_code} - Process Time: {process_time:.2f}ms"
    )

    return response


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.warning(f"Business exception occurred: {exc.result_code.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.result_code.status_code,
        content={"code": exc.result_code.code, "message": exc.result_code.message},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the validation errors for debugging
    logger.warning(f"Validation error on request {request.method} {request.url}: {exc.errors()}")

    # Format the error messages
    error_messages = []
    for error in exc.errors():
        # field = ".".join(str(p) for p in error['loc']) # e.g., "body.email"
        field = str(error['loc'][-1])
        message = f"Field '{field}': {error['msg']}"
        error_messages.append(message)
    detailed_message = "; ".join(error_messages)

    return JSONResponse(
        status_code=ResultCode.VALIDATION_ERROR.status_code,
        content={"code": ResultCode.VALIDATION_ERROR.code, "message": detailed_message},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("An unexpected error occurred", exc_info=True)
    return JSONResponse(
        status_code=ResultCode.INTERNAL_SERVER_ERROR.status_code,
        content={"code": ResultCode.INTERNAL_SERVER_ERROR.code,
                   "message": ResultCode.INTERNAL_SERVER_ERROR.message},
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
app.include_router(watchlist_item.router, prefix="/watchlists/{watchlist_id}/items", tags=["watchlists"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Astra API"}
