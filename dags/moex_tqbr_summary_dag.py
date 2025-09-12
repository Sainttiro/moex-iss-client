from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

# Настройки по умолчанию для DAG
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# Создание DAG
dag = DAG(
    'moex_tqbr_summary_dag',
    default_args=default_args,
    description='Получение промежуточных итогов по акциям MOEX TQBR и загрузка в ClickHouse',
    schedule_interval='0 19 * * 1-5',  # Каждый рабочий день в 19:00 (после закрытия торгов)
    max_active_runs=1,
    tags=['moex', 'tqbr', 'stocks', 'summary']
)

# Команда для выполнения
# Примечание: предполагается, что moex-client установлен в окружении, где работает Airflow
command = "moex-client session-summary --to-clickhouse"

# Определение задачи
load_summary_to_clickhouse = BashOperator(
    task_id='load_tqbr_summary_to_clickhouse',
    bash_command=command,
    dag=dag,
)
