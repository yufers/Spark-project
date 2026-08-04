import os
import pendulum
from airflow.models.dag import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

with DAG(
    dag_id="dag_spark_valkey",
    start_date=pendulum.datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    run_spark_job = SparkSubmitOperator(
        task_id="spark_valkey_task",
        application="/opt/airflow/spark_jobs/spark_valkey_job.py",
        conn_id="spark_default",
        name="spark_valkey_job",
        num_executors=2,
        executor_cores=4,
        verbose=True,
        env_vars={
            "VALKEY_NAME": os.environ["VALKEY_NAME"],
            "VALKEY_PASSWORD": os.environ["VALKEY_PASSWORD"],
        },
        conf={
            "spark.executorEnv.VALKEY_NAME": os.environ["VALKEY_NAME"],
            "spark.executorEnv.VALKEY_PASSWORD": os.environ["VALKEY_PASSWORD"],
        }
    )

    run_spark_job