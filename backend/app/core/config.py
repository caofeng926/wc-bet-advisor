import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/wc_bet.db")
    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:5174,http://localhost:3000"
        ).split(",")
    ]
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    FOOTBALL_DATA_API_KEY: str = os.getenv("FOOTBALL_DATA_API_KEY", "")
    POLYMARKET_API_BASE: str = os.getenv("POLYMARKET_API_BASE", "https://gamma-api.polymarket.com")
    ODDS_API_KEY: str = os.getenv("ODDS_API_KEY", "")


settings = Settings()
