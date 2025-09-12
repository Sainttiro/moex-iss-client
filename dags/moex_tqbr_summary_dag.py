from __future__ import annotations
import os
import subprocess
import pendulum
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

def load_session_summary():
    """
    Загружает данные о текущей торговой сессии TQBR в ClickHouse.
    """
    # Определяем host/port ClickHouse
    clickhouse_host = os.environ.get("CLICKHOUSE_HOST", "localhost")
    clickhouse_port = os.environ.get("CLICKHOUSE_PORT", "9000")

    # Вытаскиваем MOEX логин/пароль из env
    moex_user = os.environ.get("MOEX_USERNAME")
    moex_pass = os.environ.get("MOEX_PASSWORD")

    if not moex_user or not moex_pass:
        raise RuntimeError("MOEX_USERNAME или MOEX_PASSWORD не установлены")

    # Формируем команду для запуска CLI
    cmd = ["python", "-m", "moex_client.cli.main", "session-summary", "--to-clickhouse"]

    print("Запускаем команду:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)

    print(proc.stdout)
    print(proc.stderr)

    if proc.returncode != 0:
        raise RuntimeError("session-summary завершился с ошибкой")

with DAG(
    dag_id="moex_tqbr_summary_cli_dag",
    schedule="0 19 * * 1-5",  # Каждый рабочий день в 19:00 (после закрытия торгов)
    start_date=pendulum.datetime(2025, 9, 4, tz="Europe/Moscow"),
    catchup=False,
    is_paused_upon_creation=False,
    tags=["moex", "tqbr", "stocks", "summary"],
) as dag:

    load_task = PythonOperator(
        task_id="load_session_summary",
        python_callable=load_session_summary
    )
