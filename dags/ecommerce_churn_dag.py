from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="ecommerce_churn_data_platform",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["portfolio", "data-engineering", "churn"],
) as dag:
    run_pipeline = BashOperator(
        task_id="run_ecommerce_churn_pipeline",
        bash_command="cd /opt/airflow/project && python -m pipeline.run_pipeline",
    )

