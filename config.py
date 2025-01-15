from celery import Celery
import os
from pydantic_settings import BaseSettings
from pydantic import BaseModel
import redis

class RunConfig(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000

class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "parol"
    REDIS_HOST: str = "0.0.0.0"
    BASE_URL: str = "http://0.0.0.0:8000"
    BASE_DIR: str = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, 'app/uploads')


# Создание экземпляра настроек
settings = Settings()

# Формирование URL для подключения к Redis
redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"



redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    password=settings.REDIS_PASSWORD,
)