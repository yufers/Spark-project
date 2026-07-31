import os
import requests
from pathlib import Path
from tqdm import tqdm
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# --- Настройки ---
DOWNLOAD_URL = "https://datasets-documentation.s3.eu-west-3.amazonaws.com/noaa/noaa_enriched.parquet"
TEMP_LOCAL_FILE = "weather_temp.parquet"

# Настройки MinIO из .env
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://127.0.0.1:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")

BUCKET_NAME = "course-bucket"
OBJECT_NAME = "weather.parquet"


def get_s3_client():
    """Создает клиент boto3 для работы с MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1"
    )


def ensure_bucket_exists(s3_client, bucket_name):
    """Создает бакет, если он не существует."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Бакет '{bucket_name}' уже существует.")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ["404", "NoSuchBucket"]:
            print(f"Бакет '{bucket_name}' не найден. Создаем...")
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"Бакет '{bucket_name}' успешно создан.")
        else:
            # Если ошибка 403 или другая — выбрасываем с подробностями
            print(f"Ошибка проверки бакета: {e}")
            raise e


def download_file(url, local_path):
    """Скачивает файл с прогресс-баром."""
    print(f"Скачивание данных с {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))

    with open(local_path, "wb") as f, tqdm(
        total=total_size, unit="B", unit_scale=True, desc="Скачивание"
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))


def upload_to_minio(s3_client, local_path, bucket, object_name):
    """Загружает файл в MinIO."""
    filesize = os.path.getsize(local_path)
    print(f"Загрузка в MinIO (s3://{bucket}/{object_name})...")

    class ProgressCallback:
        def __init__(self, total):
            self.pbar = tqdm(total=total, unit="B", unit_scale=True, desc="Загрузка")

        def __call__(self, bytes_amount):
            self.pbar.update(bytes_amount)

    s3_client.upload_file(
        local_path,
        bucket,
        object_name,
        Callback=ProgressCallback(filesize)
    )
    print("Загрузка завершена!")


def main():
    print(f"Подключение к MinIO: {MINIO_ENDPOINT}")
    print(f"Используем Access Key: {ACCESS_KEY}")

    s3 = get_s3_client()
    
    # 1. Проверяем / создаем бакет
    ensure_bucket_exists(s3, BUCKET_NAME)
    
    # 2. Скачиваем временный файл
    download_file(DOWNLOAD_URL, TEMP_LOCAL_FILE)
    
    # 3. Загружаем в MinIO
    upload_to_minio(s3, TEMP_LOCAL_FILE, BUCKET_NAME, OBJECT_NAME)
    
    # 4. Удаляем временный локальный файл
    if os.path.exists(TEMP_LOCAL_FILE):
        os.remove(TEMP_LOCAL_FILE)
        print("Временный локальный файл удален.")


if __name__ == "__main__":
    main()