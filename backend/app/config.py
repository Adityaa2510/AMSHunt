import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Attack Surface Management Platform"
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
