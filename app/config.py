from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    session_secret: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
