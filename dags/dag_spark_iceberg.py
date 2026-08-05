import os
import pendulum
from airflow.models.dag import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
    dag_id="dag_spark_iceberg",
    start_date=pendulum.datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    run_spark_job = SparkSubmitOperator(
        task_id="spark_iceberg_task",
        application="/opt/airflow/spark_jobs/spark_iceberg_job.py",
        conn_id="spark_default",
        name="PySpark Iceberg Local MinIO",
        num_executors=2,
        executor_cores=4,
        verbose=True,
        env_vars={
            "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
            "MINIO_ROOT_USER": os.getenv("MINIO_ROOT_USER", "minioadmin"),
            "MINIO_ROOT_PASSWORD": os.getenv("MINIO_ROOT_PASSWORD", "Mila.Mila1"),
        },
        conf={
            "spark.executorEnv.MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
            "spark.executorEnv.MINIO_ROOT_USER": os.getenv("MINIO_ROOT_USER", "minioadmin"),
            "spark.executorEnv.MINIO_ROOT_PASSWORD": os.getenv("MINIO_ROOT_PASSWORD", "Mila.Mila1"),
        },
        jars=",".join([
            "/opt/extra-jars/iceberg-spark-runtime-3.5_2.12-1.5.2.jar",
            "/opt/extra-jars/hadoop-aws-3.3.4.jar",
            "/opt/extra-jars/aws-java-sdk-bundle-1.12.262.jar",
        ]),
    )

    run_spark_job