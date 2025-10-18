import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def get_int_env(key: str, default: int = 0) -> int:
    """Безопасно преобразует переменную окружения в int"""
    try:
        return int(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return default

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    TG_API_ID: int = get_int_env("TG_API_ID", 0)
    TG_API_HASH: str = os.getenv("TG_API_HASH", "")
    DB_PATH: str = os.getenv("DB_PATH", "news.db")
    DEFAULT_CHANNELS: str = os.getenv("DEFAULT_CHANNELS", "")
    PAGE_SIZE: int = get_int_env("PAGE_SIZE", 5)

    def __post_init__(self):
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN обязателен")
        if not self.TG_API_ID:
            raise ValueError("TG_API_ID обязателен")
        if not self.TG_API_HASH:
            raise ValueError("TG_API_HASH обязателен")

config = Config()