import os
from datetime import datetime, timezone, timedelta

import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, Form
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from celery_app.app import delete_file_scheduled
from config import settings, redis_client
from utils.random_string import generate_random_string

main_app = FastAPI(
    title="Trading App"
)


# Функция upload_file, которая асинхронно загружает файл
@main_app.post("/api/upload/")
async def upload_file(file: UploadFile, expiration_minutes: int = Form(...)):
    try:

        # Чтение содержимого загруженного файла
        file_content = await file.read()

        # Установка максимального размера файла в байтах(5 МБ)
        max_file_size = 5 * 1024 * 1024
        if len(file_content) > max_file_size:
            raise HTTPException(status_code=413, detail="Превышен максимальный размер файла (5 МБ).")

        # Получение пути к директории для загрузки файлов
        upload_dir = settings.UPLOAD_DIR

        # Вычисление общего размера файлов в директории загрузки в байтах
        total_size = sum(os.path.getsize(os.path.join(upload_dir, f)) for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f)))
        max_total_size = 100 * 1024 * 1024  # 100 МБ в байтах
        if total_size + len(file_content) > max_total_size:
            raise HTTPException(status_code=507, detail="Превышен общий лимит размера файлов (100 МБ). Освободите место и повторите попытку.")

        # Имя начального файла
        start_file_name = file.filename

        # Сгенерировать уникальное имя файла и ID для удаления
        file_extension = os.path.splitext(file.filename)[1]
        file_id = generate_random_string(12)
        dell_id = generate_random_string(12)

        # Сохранить файл на диск
        file_path = os.path.join(settings.UPLOAD_DIR, file_id + file_extension)
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Рассчитать время истечения в секундах
        expiration_seconds = expiration_minutes * 60
        expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expiration_seconds)

        # Запланировать задачу для удаления файла после истечения времени
        delete_file_scheduled.apply_async((file_id, dell_id), countdown=expiration_seconds)

        # URL-адреса для метаданных
        download_url = f"{settings.BASE_URL}/files/{file_id + file_extension}"

        # Сохранить метаданные в Redis
        redis_key = f"file:{file_id}"  # Уникальный ключ для файла
        redis_client.hmset(redis_key, {"file_path": file_path,
                                       "dell_id": dell_id,
                                       "download_url": download_url,
                                       "expiration_time": int(expiration_time.timestamp()),
                                       "start_file_name": start_file_name})

        return {
            "message": "Файл успешно загружен",
            "file_id": file_id,
            "dell_id": dell_id,
            "download_url": download_url,
            "expiration_time": expiration_time.isoformat(),
            "expiration_seconds": expiration_seconds
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")

@main_app.delete("/delete/{file_id}/{dell_id}")
async def delete_file(file_id: str, dell_id: str):

    # Полчение информации из redis
    redis_key = f"file:{file_id}"
    file_info = redis_client.hgetall(redis_key)

    if not file_info:
        raise HTTPException(status_code=404, detail="Файл не найден")
    # Проверка ид удаления
    dell_id_redis = file_info.get(b"dell_id").decode()
    if dell_id_redis != dell_id:
        raise HTTPException(status_code=403, detail="Не совпадает айди удаления с айди удаления файла")

    file_path = file_info.get(b"file_path").decode()

    # Удаление файла и очистка записи в Redis
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл {file_path} успешно удален!")
        else:
            print(f"Файл {file_path} не найден.")

        redis_client.delete(redis_key)
        return {"message": "Файл успешно удален и запись в Redis очищена!"}

    except OSError as e:
        print(f"Error deleting file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления файла: {str(e)}")

@main_app.get("/download/")
async def download_file(file_id: str):
    # Путь к файлу на сервере
    redis_key = f"file:{file_id}"
    file_info = redis_client.hgetall(redis_key)

    if not file_info:
        raise HTTPException(status_code=404, detail="Файл не найден")

    file_path = file_info.get(b"file_path").decode()

    return FileResponse(file_path, media_type='application/octet-stream')

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        reload=True,
        host=settings.run.host,
        port=settings.run.port
    )
