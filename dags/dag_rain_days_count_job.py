import os
import pendulum
from airflow.models.dag import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
    dag_id="dag_rain_days_count_job",
    start_date=pendulum.datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    run_spark_job = SparkSubmitOperator(
        task_id="rain_days_count_task",
        conn_id="spark_default",
        application="/opt/airflow/spark_jobs/rain_days_count_job.py",
        name="RainDaysCount",
        num_executors=2,
        executor_cores=4,
        verbose=True,
        packages="org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262",
        conf={
            "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            "spark.hadoop.fs.s3a.endpoint": "http://minio:9000",
            "spark.hadoop.fs.s3a.path.style.access": "true",
            "spark.hadoop.fs.s3a.connection.ssl.enabled": "false",
            "spark.hadoop.fs.s3a.aws.credentials.provider": "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        },
        env_vars={
            "MINIO_ACCESS_KEY": os.environ["MINIO_ACCESS_KEY"],
            "MINIO_SECRET_KEY": os.environ["MINIO_SECRET_KEY"],
        },
    )

    run_spark_job