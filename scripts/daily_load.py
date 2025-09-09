import subprocess
import datetime
import os
import sys


def get_previous_trading_day():
    """
    Возвращает дату предыдущего дня в формате YYYY-MM-DD.
    В будущем можно добавить логику для пропуска выходных и праздничных дней.
    """
    today = datetime.date.today()
    previous_day = today - datetime.timedelta(days=1)
    return previous_day.strftime("%Y-%m-%d")


def run_daily_load():
    """
    Запускает загрузку исторических данных за предыдущий торговый день.
    """
    date_to_load = get_previous_trading_day()
    command = [
        "moex-client",
        "history",
        "--engine", "stock",
        "--market", "shares",
        "--board", "TQBR",
        "--date", date_to_load,
        "--to-clickhouse"
    ]
    
    print(f"Executing command: {' '.join(command)}")
    
    try:
        env = os.environ.copy()
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, env=env
        )
        print(result.stdout)
        print(f"✅ Successfully loaded data for {date_to_load}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error loading data for {date_to_load}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)  # <--- ВАЖНО! Возвращаем ненулевой код
    except FileNotFoundError:
        print("❌ Error: 'moex-client' command not found. Make sure the package is installed and in your PATH.")
        sys.exit(1)  # <--- Тоже падаем


if __name__ == "__main__":
    run_daily_load()
