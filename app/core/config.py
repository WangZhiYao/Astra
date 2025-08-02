from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_URL: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MAX_LOGIN_ATTEMPTS: int = 3
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = 30

    PRICE_HISTORY_FETCH_COUNT = 30

    class Config:
        env_file = ".env"


settings = Settings()
