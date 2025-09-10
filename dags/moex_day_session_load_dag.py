from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="moex_day_session_load",
    schedule="0 19 * * 1-5",  # Run at 19:00 on weekdays
    start_date=pendulum.datetime(2023, 10, 1, tz="Europe/Moscow"),
    catchup=False,
    tags=["moex"],
) as dag:
    load_day_session_data = BashOperator(
        task_id="load_day_session_data",
        bash_command="python /opt/airflow/scripts/day_session_load.py",
    )
