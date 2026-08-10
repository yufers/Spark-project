import os
import logging
from pyspark.sql import functions as F, SparkSession

logging.basicConfig(format="OUR_APP: %(message)s", level=logging.INFO)

spark = SparkSession.builder \
    .appName("RainDaysCount") \
    .config("spark.hadoop.fs.s3a.access.key", os.environ["MINIO_ACCESS_KEY"]) \
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["MINIO_SECRET_KEY"]) \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Указать путь к файлу в формате: "s3a://имя-бакета/имя-файла"
PATH = "s3a://course-bucket/weather.parquet"

# Загрузить содержимое файла в датафрейм
df = spark.read.parquet(PATH)

# Отфильтровать датафрейм по station_id и date, чтобы получить такие же исходные данные, как и в предыдущем уроке
# А также преобразовать байтовое поле station_id в строку
df = df.filter(
    (F.col('station_id') == 'ASM00094998') &
    F.col('date').isin(['2022-07-30', '2022-07-31', '2022-08-01', '2022-08-02'])
).select('date', F.col('station_id').cast('string'), 'tempAvg', 'precipitation')

# Вывести первые 10 строк входных данных. Поскольку после фильтрации останется 4 строки, таким образом мы выведем все данные
# Использовали построчный вывод для того, чтобы иметь возможность добавить префикс при логировании
logging.info('Input data:')
for row in df.head(10):
    logging.info(row)

total_rain_days = df.filter(F.col("precipitation") > 0).count()

logging.info(f"Общее количество дождливых дней: {total_rain_days}")