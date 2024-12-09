from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRATION_MINUTES: int = 120
    BASE_URL: str
    USER_DB_URL: str
    REDIS_HOST: str

    class Config:
        env_file = ".env"

settings = Settings()
