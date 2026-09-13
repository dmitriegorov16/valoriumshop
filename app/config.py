from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    CHANNEL_NAME: str
    CHANNEL_USERNAME: str
    CHANNEL_ID: int
    STARS_EXCHANGE_RATE: float
    CRYPTO_PAY_TOKEN: str
    DB_PATH: str = "data.sqlite"
    MAXIMUM_LENGTH_CATEGORY: int = 20
    MINIMUM_LENGTH_CATEGORY: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
