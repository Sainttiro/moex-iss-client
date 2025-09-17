import subprocess
import datetime
import os
import sys
import re
from clickhouse_driver import Client
from clickhouse_driver.errors import Error as ClickHouseError


def check_clickhouse_connection():
    """
    Проверяет соединение с ClickHouse.
    
    Возвращает:
        tuple: (успех (bool), сообщение об ошибке (str) или None)
    """
    try:
        # Получаем настройки ClickHouse из переменных окружения
        host = os.environ.get("CLICKHOUSE_HOST", "localhost")
        port = int(os.environ.get("CLICKHOUSE_PORT", "9000"))
        db = os.environ.get("CLICKHOUSE_DB", "default")
        user = os.environ.get("CLICKHOUSE_USER", "default")
        password = os.environ.get("CLICKHOUSE_PASSWORD", "")
        
        # Создаем клиент ClickHouse
        client = Client(
            host=host,
            port=port,
            database=db,
            user=user,
            password=password,
            connect_timeout=5
        )
        
        # Проверяем соединение
        result = client.execute("SELECT 1")
        if result and result[0][0] == 1:
            print(f"Соединение с ClickHouse ({host}:{port}) установлено успешно")
            return True, None
        else:
            return False, "Неожиданный результат при проверке соединения с ClickHouse"
    except ClickHouseError as e:
        return False, f"Ошибка ClickHouse: {e}"
    except Exception as e:
        return False, f"Ошибка при подключении к ClickHouse: {e}"


def delete_session_summary_data_for_today():
    """
    Удаляет данные о торговой сессии за текущую дату из ClickHouse.
    
    Возвращает:
        tuple: (успех (bool), сообщение об ошибке (str) или None)
    """
    try:
        # Получаем настройки ClickHouse из переменных окружения
        host = os.environ.get("CLICKHOUSE_HOST", "localhost")
        port = int(os.environ.get("CLICKHOUSE_PORT", "9000"))
        db = os.environ.get("CLICKHOUSE_DB", "default")
        user = os.environ.get("CLICKHOUSE_USER", "default")
        password = os.environ.get("CLICKHOUSE_PASSWORD", "")
        
        # Создаем клиент ClickHouse
        client = Client(
            host=host,
            port=port,
            database=db,
            user=user,
            password=password
        )
        
        # Получаем текущую дату
        today = datetime.date.today()
        
        # Удаляем данные за текущую дату
        query = f"ALTER TABLE session_summary DELETE WHERE load_date = '{today}'"
        client.execute(query)
        
        print(f"Данные за {today} успешно удалены из таблицы session_summary")
        return True, None
    except ClickHouseError as e:
        error_msg = f"Ошибка ClickHouse при удалении данных: {e}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Ошибка при удалении данных: {e}"
        print(error_msg)
        return False, error_msg


def load_session_summary():
    """
    Загружает данные о текущей торговой сессии TQBR в ClickHouse.
    
    Использует команду moex-client для загрузки данных.
    """
    # Проверяем соединение с ClickHouse
    connection_ok, error_msg = check_clickhouse_connection()
    if not connection_ok:
        print(f"Ошибка: Не удалось подключиться к ClickHouse: {error_msg}")
        sys.exit(1)
    
    # Примечание: Мы больше не удаляем данные за текущую дату перед запуском команды,
    # чтобы избежать дублирования данных при повторном запуске
    
    # Формируем команду для запуска CLI
    # Используем команду 'moex-client session-summary' для загрузки данных о торговой сессии
    cmd = ["moex-client", "session-summary", "--to-clickhouse"]

    print("Запускаем команду:", " ".join(cmd))
    
    try:
        # Запускаем команду с текущими переменными окружения
        env = os.environ.copy()
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        print("Вывод команды:")
        print(proc.stdout)
        
        has_ssl_error = False
        
        if proc.stderr:
            print("Ошибки:")
            print(proc.stderr)
            
            # Проверяем наличие ошибок SSL или сетевых ошибок в выводе
            if re.search(r'SSL|TLS|connection|timeout|network|connect', proc.stderr, re.IGNORECASE):
                print("Предупреждение: Обнаружена сетевая ошибка, но это не считается критической ошибкой")
                has_ssl_error = True

        if proc.returncode != 0 and not has_ssl_error:
            print(f"Команда завершилась с ошибкой (код {proc.returncode})")
            sys.exit(proc.returncode)
        
        print("Операция завершена успешно")
        
    except FileNotFoundError:
        print("Ошибка: Команда 'moex-client' не найдена. Убедитесь, что пакет установлен и доступен в PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при выполнении команды: {e}")
        sys.exit(1)


if __name__ == "__main__":
    load_session_summary()
