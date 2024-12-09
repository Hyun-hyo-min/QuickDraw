from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_URL: str
    DRAW_SERVICE_URL: str
    TIME_OUT: float = 10.0

    class Config:
        env_file = ".env"


settings = Settings()
