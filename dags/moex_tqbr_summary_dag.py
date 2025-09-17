from __future__ import annotations
import os
import subprocess
import pendulum
import datetime
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

def load_session_summary():
    """
    Загружает данные о текущей торговой сессии TQBR в ClickHouse.
    
    Использует скрипт session_summary_load.py для загрузки данных.
    """
    # Формируем команду для запуска скрипта
    cmd = ["python", "/opt/airflow/scripts/session_summary_load.py"]

    print("Запускаем команду:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)

    print(proc.stdout)
    print(proc.stderr)

    if proc.returncode != 0:
        raise RuntimeError("session_summary_load.py завершился с ошибкой")

# Настройки по умолчанию для DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,  # Количество повторных попыток
    'retry_delay': datetime.timedelta(minutes=2),  # Задержка между попытками
    'retry_exponential_backoff': True,  # Экспоненциальная задержка
    'max_retry_delay': datetime.timedelta(minutes=10),  # Максимальная задержка
    'execution_timeout': datetime.timedelta(minutes=10),  # Таймаут выполнения
}

with DAG(
    dag_id="moex_tqbr_summary_dag",
    default_args=default_args,
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
