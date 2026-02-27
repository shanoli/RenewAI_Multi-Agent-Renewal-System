import os
from pydantic_settings import BaseSettings

from functools import lru_cache


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    jwt_secret_key: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    sqlite_db_path: str = os.path.abspath("./data/renewai.db")

    chroma_db_path: str = "./data/chroma_db"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    embedding_model: str = "models/text-embedding-004"
    chroma_telemetry_gather: bool = False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
