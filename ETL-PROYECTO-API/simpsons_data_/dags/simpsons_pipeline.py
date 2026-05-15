
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from etl.pipeline import run_pipeline

with DAG(
    dag_id="simpsons_pipeline",
    start_date=datetime(2024,1,1),
    schedule="@daily",
    catchup=False
) as dag:

    etl_task = PythonOperator(
        task_id="run_etl",
        python_callable=run_pipeline
    )
