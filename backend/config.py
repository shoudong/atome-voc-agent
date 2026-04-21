from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://atome:atome_secret@localhost:5432/atome_voc"
    database_url_sync: str = "postgresql://atome:atome_secret@localhost:5432/atome_voc"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # LLM
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-20250514"

    # Crawlers
    apify_api_token: str = ""
    brave_api_key: str = ""
    reddit_user_agent: str = "AtomeVoC/1.0"

    # Alerting
    slack_webhook_url: str = ""
    lark_webhook_url: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_email_from: str = ""
    alert_email_to: str = ""

    # Schedule
    crawl_schedule_hours: str = "8,20"
    digest_hour: int = 9
    tz: str = "Asia/Manila"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
