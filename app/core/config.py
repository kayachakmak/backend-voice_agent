from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    auth0_domain: str
    auth0_audience: str
    auth0_algorithms: str = "RS256"
    elevenlabs_api_key: str = ""
    webhook_api_url: str
    webhook_api_key: str = ""
    debug: bool = False
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/voiceagent"

    @property
    def auth0_issuer(self) -> str:
        return f"https://{self.auth0_domain}/"

    @property
    def auth0_jwks_url(self) -> str:
        return f"https://{self.auth0_domain}/.well-known/jwks.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
