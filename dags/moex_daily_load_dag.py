from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="moex_daily_load",
    schedule="0 6 * * *",
    start_date=pendulum.datetime(2025, 9, 4, tz="Europe/Moscow"),
    catchup=False,
    tags=["moex"],
) as dag:
    load_daily_data = BashOperator(
        task_id="load_daily_data",
        bash_command="python /opt/airflow/scripts/daily_load.py",
    )
