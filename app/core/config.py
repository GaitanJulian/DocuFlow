# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuFlow"
    API_V1_STR: str = "/api/v1"

    # DB
    DATABASE_URL: str = "postgresql://docuflow:docuflow@localhost:5432/docuflow"

    # Auth
    JWT_SECRET_KEY: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 día

    class Config:
        env_file = ".env"


settings = Settings()
