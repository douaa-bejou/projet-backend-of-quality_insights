from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Quality Insights API"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./quality_insights.db"
    bootstrap_admin_name: str = "Responsable"
    bootstrap_admin_email: str = "admin@gmail.com"
    bootstrap_admin_password: str = "ChangeMe123!"
    cors_origins: str = (
        "http://localhost:8080,http://127.0.0.1:8080,"
        "http://localhost:5173,http://127.0.0.1:5173"
    )
    cors_origin_regex: str = (
        r"https?://("
        r"(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])(:\d+)?"
        r"|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?"
        r"|(172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?"
        r"|(192\.168\.\d{1,3}\.\d{1,3})(:\d+)?"
        r"|([a-z0-9-]+\.local)(:\d+)?"
        r"|([a-z0-9-]+\.)*vercel\.app"
        r")$"
    )

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
