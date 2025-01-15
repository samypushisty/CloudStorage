import requests
from celery import Celery
from config import  settings,redis_url

celery_app = Celery(
    "celery_worker",  # Имя приложения Celery
    broker=redis_url,  # URL брокера задач (Redis)
)

@celery_app.task(
    name='delete_file_scheduled',
    bind=True,
    max_retries=3,
    default_retry_delay=5
)
def delete_file_scheduled(self, file_id, dell_id):
    try:
        print("vlad")
        response = requests.delete(f"{settings.BASE_URL}/delete/{file_id}/{dell_id}")
        response.raise_for_status()
        return response.status_code
    except requests.RequestException as exc:
        self.retry(exc=exc)
    except Exception as e:
        return None