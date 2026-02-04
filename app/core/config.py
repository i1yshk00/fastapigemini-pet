import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """
    Settings of FastAPI Gemini application
    """
    # ── App ───────────────────────────────────────────
    APP_NAME: str = 'FastAPI Gemini'
    ENVIRONMENT: str = 'development'
    DEBUG: bool = False

    # ── Database parts ────────────────────────────────
    DATABASE_URL: str | None = Field(
        default=None,
        examples=['postgresql+asyncpg://user:pass@host:5432/dbname'],
    )
    DB_USER: str | None = Field(default=None, examples=['postgres'])
    DB_PASSWORD: str | None = Field(default=None, examples=['secret'])
    DB_HOST: str | None = Field(default=None, examples=['localhost'])
    DB_PORT: int | None = Field(default=5432, examples=[5432])
    DB_NAME: str | None = Field(default=None, examples=['fastapi_gemini'])

    @field_validator("DATABASE_URL", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME", mode="before")
    @classmethod
    def strip_quotes(cls, value):
        if isinstance(value, str):
            return value.strip().strip('"').strip("'")
        return value

    @field_validator("DB_PORT", mode="before")
    @classmethod
    def parse_port(cls, value):
        if isinstance(value, str):
            value = value.strip().strip('"').strip("'")
        return value

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        missing = [
            name
            for name in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME")
            if not getattr(self, name)
        ]
        if missing:
            raise ValueError(
                "Missing database settings: " + ", ".join(missing)
            )

        return (
            f'postgresql+asyncpg://'
            f'{self.DB_USER}:{self.DB_PASSWORD}'
            f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )

    # ── Security ──────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        extra='ignore',
    )


class GeminiConfig:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


class LoguruConfig:
    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]
        self.LOG_DIR = project_root / 'logs'
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def setup_logging(self) -> None:
        """
        Setup loguru function.
        Used for run logging when app starting.
        """
        logger.remove()  # before new setup any other loggers must be removed

        # ── STDOUT (for docker / uvicorn) ────────────────────────────
        logger.add(
            sys.stdout,
            level='INFO',
            format=(
                '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                '<level>{level}</level> | '
                '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
                '{message} | {extra}'
            ),
            enqueue=True,  # safe logging for async and multiprocess functions
        )

        # ── INFO log ─────────────────────────────────────────────────
        logger.add(
            self.LOG_DIR / 'app.log',
            level='INFO',
            rotation='10 MB',
            retention='14 days',
            compression='zip',
            enqueue=True,
            format=(
                '{time:YYYY-MM-DD HH:mm:ss.SSS} | '
                '{level} | {name}:{function}:{line} | '
                '{message} | {extra}'
            ),
        )

        # ── ERROR log ────────────────────────────────────────────────
        logger.add(
            self.LOG_DIR / 'error.log',
            mode='a',
            level='ERROR',
            rotation='5 MB',
            retention='30 days',
            compression='zip',
            enqueue=True,
            backtrace=True,
            diagnose=False,
            format=(
                '{time:YYYY-MM-DD HH:mm:ss.SSS} | '
                '{level} | {name}:{function}:{line} | '
                '{message} | {extra}'
            ),
        )


settings = Settings()
gemini_config_obj = GeminiConfig()
loguru_config_obj = LoguruConfig()
