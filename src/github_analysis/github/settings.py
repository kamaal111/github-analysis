from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    github_token: str
    github_base_url: HttpUrl = "https://api.github.com"

    @property
    def github_base_url_string(self):
        return str(self.github_base_url)


settings = __Settings()
