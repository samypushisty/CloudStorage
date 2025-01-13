import ssl

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "parol"
    REDIS_HOST: str = "0.0.0.0"


# Создание экземпляра настроек
settings = Settings()

# Формирование URL для подключения к Redis через SSL
redis_url = f"rediss://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

