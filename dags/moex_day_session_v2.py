from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import requests
import json
import logging

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

# Создание DAG с новым ID
dag = DAG(
    'moex_tqbr_summary_old_dag',  # Изменен ID DAG
    default_args=default_args,
    description='Получение промежуточных итогов по акциям MOEX TQBR (старая версия)',
    schedule_interval='0 19 * * 1-5',  # Каждый рабочий день в 19:00 (после закрытия торгов)
    max_active_runs=1,
    tags=['moex', 'tqbr', 'stocks', 'old']
)

def get_moex_tqbr_summary(**context):
    """
    Функция для получения промежуточных итогов по акциям MOEX TQBR
    """
    logger = logging.getLogger(__name__)
    
    # URL для промежуточных итогов по акциям (shares), board TQBR, основная сессия (1)
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/secstats.json"
    
    params = {
        'boardid': 'TQBR',       # Только режим TQBR
        'tradingsession': '1',   # 1 - Основная сессия
        'iss.meta': 'off',       # Отключаем метаданные для упрощения
        'iss.only': 'secstats'   # Только блок secstats
    }
    
    try:
        logger.info("Отправляем запрос к MOEX API...")
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            error_msg = f"Ошибка запроса: {response.status_code}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        json_data = response.json()
        secstats = json_data.get('secstats', {})
        columns = secstats.get('columns', [])
        data = secstats.get('data', [])
        
        if not data:
            logger.warning("Получены пустые данные от API")
            return {'columns': columns, 'data': []}
        
        # Фильтр для оставления только записей с BOARDID = TQBR
        filtered_data = [row for row in data if row[1] == 'TQBR']  # Индекс 1 соответствует BOARDID
        
        logger.info(f"Получено {len(filtered_data)} записей для TQBR (основная сессия)")
        
        # Логирование первых 5 строк для проверки
        for i, row in enumerate(filtered_data[:5]):
            logger.info(f"Строка {i+1}: {dict(zip(columns, row))}")
        
        # Формирование результата
        result = {'columns': columns, 'data': filtered_data}
        
        # Передача данных в XCom для следующих задач
        context['task_instance'].xcom_push(key='moex_data', value=result)
        
        logger.info("Данные успешно получены и переданы в XCom")
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка при запросе к API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Непредвиденная ошибка: {str(e)}"
        logger.error(error_msg)
        raise

def save_moex_data_to_file(**context):
    """
    Функция для сохранения данных в JSON файл
    """
    logger = logging.getLogger(__name__)
    
    # Получение данных из XCom
    moex_data = context['task_instance'].xcom_pull(task_ids='get_moex_data', key='moex_data')
    
    if not moex_data:
        logger.error("Не удалось получить данные из предыдущей задачи")
        raise Exception("Данные отсутствуют в XCom")
    
    try:
        # Путь к файлу (в продакшене лучше использовать настраиваемый путь)
        file_path = "/tmp/moex_tqbr_summary.json"
        
        # Сохранение данных в JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(moex_data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Данные сохранены в {file_path}")
        logger.info(f"Сохранено {len(moex_data.get('data', []))} записей")
        
        return file_path
        
    except Exception as e:
        error_msg = f"Ошибка при сохранении файла: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

# Определение задач
get_data_task = PythonOperator(
    task_id='get_moex_data',
    python_callable=get_moex_tqbr_summary,
    dag=dag,
    provide_context=True
)

save_data_task = PythonOperator(
    task_id='save_data_to_file',
    python_callable=save_moex_data_to_file,
    dag=dag,
    provide_context=True
)

# Определение зависимостей задач
get_data_task >> save_data_task
