import logging
import os

from pyspark.sql import functions as F, SparkSession

# Поменять путь под ваш бакет в MinIO
PATH = "s3a://course-bucket/weather.parquet"

logging.basicConfig(format="OUR_APP: %(message)s", level=logging.INFO)

spark = SparkSession.builder \
    .appName("first_job") \
    .config("spark.hadoop.fs.s3a.access.key", os.environ["MINIO_ACCESS_KEY"]) \
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["MINIO_SECRET_KEY"]) \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

sdf = spark.read.parquet(PATH)

logging.info(f"Columns: {sdf.columns}")
logging.info(f"Columns len: {len(sdf.columns)}")
logging.info(f"Schema: {sdf.schema}")
logging.info("Schema columns:")
for e in sdf.schema:
    logging.info(e)
logging.info(f"Row count: {sdf.count()}")

min_date, max_date = sdf.agg(
    F.min("date"),
    F.max("date")
).first()

logging.info(f"Min date: {min_date}")
logging.info(f"Max date: {max_date}")
logging.info(f"Row example: {sdf.head()}")