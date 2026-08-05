import os
import logging
from pyspark.sql import functions as F, SparkSession

# Имя вашего бакета в MinIO (убедитесь, что бакет создан)
BUCKET_NAME = "course-bucket"
PATH = f"s3a://{BUCKET_NAME}/weather.parquet"
WAREHOUSE_PATH = f"s3a://{BUCKET_NAME}/iceberg-warehouse/"

EXTREME_TEMP_LIMIT = -820

# 2. Логирование с префиксом OUR_APP
logging.basicConfig(format="OUR_APP: %(message)s", level=logging.INFO)


# 3. Создание SparkSession
# Пакеты JAR подтягиваются автоматически из /opt/spark/jars/ вашего Docker-образа
spark = (
    SparkSession.builder.appName("PySpark Iceberg Local MinIO")
    # Подключение расширений Iceberg SQL
    .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    # Настройка каталога Iceberg (Hadoop catalog)
    .config(
        "spark.sql.catalog.my_catalog",
        "org.apache.iceberg.spark.SparkCatalog",
    )
    .config("spark.sql.catalog.my_catalog.type", "hadoop")
    .config("spark.sql.catalog.my_catalog.warehouse", WAREHOUSE_PATH)
    # Конфигурация S3A для работы с MinIO
    .config("spark.hadoop.fs.s3a.endpoint", os.environ["MINIO_ENDPOINT"])
    .config("spark.hadoop.fs.s3a.access.key", os.environ["MINIO_ROOT_USER"])
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["MINIO_ROOT_PASSWORD"])
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config(
        "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
    )
    .config(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    )
    .getOrCreate()
)

hconf = spark.sparkContext._jsc.hadoopConfiguration()

logging.info(
    f"spark.sql.extensions: {spark.conf.get('spark.sql.extensions')}"
)

# 4. Чтение исходного Parquet и фильтрация
df = (
    spark.read.parquet(PATH)
    .select("station_id", "date", "tempAvg")
    .filter(F.col("tempAvg") <= EXTREME_TEMP_LIMIT)
)

logging.info("Initial data:")
for row in df.collect():
    logging.info(row)

# 5. Сохранение в Iceberg-таблицу (my_catalog.weather.extreme_cold)
df.writeTo("my_catalog.weather.extreme_cold").createOrReplace()
logging.info("Iceberg table created")

# 6. Получение snapshot_id первой версии
history_df = spark.sql(
    "SELECT * FROM my_catalog.weather.extreme_cold.history"
)

first_version = (
    history_df
    .orderBy("made_current_at", ascending=False)
    .first()["snapshot_id"]
)

logging.info(f"Initial snapshot ID: {first_version}")

# 7. Внесение изменений через SQL UPDATE (ACID операция)
logging.info("Updating tempAvg for AYM00089606 on 1997-07-27")

spark.sql("""
    UPDATE my_catalog.weather.extreme_cold
    SET tempAvg = tempAvg + 10
    WHERE CAST(station_id AS STRING) = 'AYM00089606'
      AND date = DATE '1997-07-27'
""")

logging.info("Update completed")

# 8. Чтение текущей (актуальной) версии таблицы
df_current = spark.read.format("iceberg").load(
    "my_catalog.weather.extreme_cold"
)
logging.info("Current data:")
for row in df_current.collect():
    logging.info(row)

# 9. Time Travel: Чтение сохраненного ранее снапшота
df_previous = (
    spark.read.format("iceberg")
    .option("snapshot-id", first_version)
    .load("my_catalog.weather.extreme_cold")
)
logging.info("First version data:")
for row in df_previous.collect():
    logging.info(row)

spark.stop()