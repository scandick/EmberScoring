import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./burnout.db")


settings = Settings()
