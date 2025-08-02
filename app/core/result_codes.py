from enum import Enum


class ResultCode(Enum):
    SUCCESS = (0, "Success", 200)

    # Auth & User Errors (1000-1099)
    EMAIL_ALREADY_REGISTERED = (1000, "Email already registered", 400)
    LOGIN_FAILED = (1001, "Incorrect email or password", 401)
    TOO_MANY_LOGIN_ATTEMPTS = (1002, "Too many failed login attempts. Please try again later.", 429)
    INVALID_REFRESH_TOKEN = (1003, "Invalid or expired refresh token", 401)
    INACTIVE_USER = (1004, "Inactive user", 400)
    INVALID_CREDENTIALS = (1005, "Could not validate credentials", 401)

    # Appearance Errors (2000-2099)
    APPEARANCE_ALREADY_EXISTS = (2000, "Appearance with this name already exists", 400)
    APPEARANCE_TYPE_ALREADY_EXISTS = (2001, "Appearance type with this name already exists", 400)
    APPEARANCE_ALIAS_ALREADY_EXISTS = (2002, "Appearance alias with this name already exists", 400)

    # Planform Errors (3000-3099)
    PLATFORM_ALREADY_EXISTS = (2003, "Platform with this name already exists", 400)

    # User purchase transaction Errors (4000-4099)

    # User sale transaction Errors (4100-4199)

    # Watchlist Errors (5000-5099)
    WATCHLIST_ALREADY_EXISTS = (5000, "Watchlist with this name already exists", 400)
    WATCHLIST_NOT_EXISTS = (5001, "Watchlist not exists", 400)

    # Watchlist item Errors (5100-5199)
    WATCHLIST_ITEM_ALREADY_EXISTS = (5100, "Watchlist item already exists", 400)
    WATCHLIST_ITEM_NOT_EXISTS = (5101, "Watchlist item not exists", 400)

    # Common Errors (9000-9099)
    FORBIDDEN = (9000, "Permission denied", 403)
    NOT_FOUND = (9001, "Resource not found", 404)
    INTERNAL_SERVER_ERROR = (9999, "Internal server error", 500)

    def __init__(self, code, message, status_code):
        self.code = code
        self.message = message
        self.status_code = status_code
