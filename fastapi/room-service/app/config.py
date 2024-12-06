from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    BASE_URL: str
    API_GATEWAY_URL: str
    ROOM_DB_URL: str
    REDIS_HOST: str

    class Config:
        env_file = ".env"


settings = Settings()
