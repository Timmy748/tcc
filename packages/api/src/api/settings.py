from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=['../../.env', '.env'], env_file_encoding='utf-8'
    )

    PEPPER: str = Field(init=False)
    DATABASE_URL: str = Field(init=False)
