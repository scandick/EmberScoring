from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./burnout.db"

    class Config:
        env_file = ".env"


settings = Settings()