from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    github_token: str
    github_base_url: str = "https://api.github.com"


settings = __Settings()
