import requests
from celery import Celery
from config import  settings,redis_url
from datetime import timedelta

celery_app = Celery(
    "celery_worker",  # Имя приложения Celery
    broker_connection_retry_on_startup = True,
    broker=redis_url,  # URL брокера задач (Redis)
)

@celery_app.task(
    name='delete_file_scheduled',
    bind=True,
    max_retries=1,
    default_retry_delay=5
)
def delete_file_scheduled(self, file_id, dell_id):
    try:
        response = requests.delete(f"{settings.BASE_URL}/file/{file_id}/{dell_id}")
        response.raise_for_status()
        return response.status_code
    except requests.RequestException as exc:
        self.retry(exc=exc)
    except Exception as e:
        return None

@celery_app.task(
    name='get_count_files',
)
def get_count_files():
    try:
        response = requests.get(f"{settings.BASE_URL}/file/all")
        response.raise_for_status()
        return response.status_code
    except Exception as e:
        return e

celery_app.conf.beat_schedule = {
    "get_count_files": {
        "task": 'get_count_files',
        "schedule": timedelta(seconds=30)
    },
}