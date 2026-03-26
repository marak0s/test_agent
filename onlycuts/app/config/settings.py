from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="dev", alias="APP_ENV")
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/onlycuts",
        alias="DATABASE_URL",
    )
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_approver_user_id: int = Field(default=0, alias="TELEGRAM_APPROVER_USER_ID")
    telegram_approver_chat_id: int = Field(default=0, alias="TELEGRAM_APPROVER_CHAT_ID")
    telegram_publish_chat_id: int = Field(default=0, alias="TELEGRAM_PUBLISH_CHAT_ID")
    default_channel_code: str = Field(default="OnlyAiOps", alias="DEFAULT_CHANNEL_CODE")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


settings = Settings()
