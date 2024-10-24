from pydantic import BaseSettings

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_HOST: str

    class Config:
        env_file = ".env"

settings = Settings()
