import os
import logging
from redis.sentinel import Sentinel
from pyspark.sql import SparkSession

logging.basicConfig(format="OUR_APP: %(message)s", level=logging.INFO)

VALKEY_NAME = os.environ["VALKEY_NAME"]
VALKEY_PASSWORD = os.environ["VALKEY_PASSWORD"]

SENTINELS_HOSTS = ["valkey-sentinel-1", "valkey-sentinel-2", "valkey-sentinel-3"]
SENTINELS = [(h, 26379) for h in SENTINELS_HOSTS]

sentinel = Sentinel(SENTINELS, socket_timeout=0.5)
master = sentinel.master_for(
    VALKEY_NAME,
    password=VALKEY_PASSWORD,
    decode_responses=True
)

master.hset("user:42", mapping={"country": "RU", "segment": "premium"})
master.hset("user:17", mapping={"country": "KZ", "segment": "standard"})

spark = SparkSession.builder.appName("spark_valkey_job").getOrCreate()
events_df = spark.createDataFrame(
    [
        (1, 42, 100.0),
        (2, 17, 250.0),
    ],
    ["event_id", "user_id", "amount"]
)

def enrich_partition(rows):
    valkey_name = os.environ["VALKEY_NAME"]
    valkey_password = os.environ["VALKEY_PASSWORD"]
    sentinels = [("valkey-sentinel-1", 26379), ("valkey-sentinel-2", 26379), ("valkey-sentinel-3", 26379)]
    
    sentinel_client = Sentinel(sentinels, socket_timeout=0.5)
    slave_client = sentinel_client.slave_for(
        valkey_name,
        password=valkey_password,
        decode_responses=True
    )

    for row in rows:
        user_data = slave_client.hgetall(f"user:{row.user_id}") or {}
        yield (
            row.event_id,
            row.user_id,
            row.amount,
            user_data.get("country"),
            user_data.get("segment"),
        )

enriched_df = events_df.rdd.mapPartitions(enrich_partition).toDF(
    ["event_id", "user_id", "amount", "country", "segment"]
)

logging.info('Result:')
for x in enriched_df.collect():
    logging.info(x)