# Руководство по использованию MOEX ISS Client

Этот документ предоставляет подробные инструкции по установке, настройке и использованию клиента MOEX ISS.

## 1. Обзор проекта

`moex-iss-client` — это современный Python-клиент для взаимодействия с API Информационно-статистического сервера (ИСС) Московской Биржи. Он позволяет:
- Безопасно аутентифицироваться.
- Загружать исторические данные по ценным бумагам.
- Экспортировать данные в формате JSON или напрямую в ClickHouse.
- Использовать удобный командный интерфейс (CLI) или Python API.
- Отслеживать прогресс длительных операций с помощью прогресс-баров.

## 2. Установка

### Требования
- Python 3.8+
- Docker и Docker Compose (для работы с ClickHouse)
- Аккаунт в MOEX ISS для доступа к историческим данным

### Настройка проекта

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/Sainttiro/moex-iss-client.git
    cd moex-iss-client
    ```

2.  **Создайте виртуальное окружение:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    # или
    venv\Scripts\activate     # Для Windows
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -e .
    ```

4.  **Настройте переменные окружения:**
    Создайте файл `.env` в корневой директории проекта, скопировав его из `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Отредактируйте файл `.env`, добавив свои учетные данные MOEX:
    ```env
    MOEX_USERNAME=your_username
    MOEX_PASSWORD=your_password
    MOEX_BASE_URL=https://iss.moex.com
    MOEX_AUTH_URL=https://passport.moex.com/authenticate
    ```

## 3. Использование командной строки (CLI)

Клиент предоставляет команду `moex-client history` для загрузки исторических данных.

### Основные опции:
- `--engine <ENGINE>`: Обязательный. Движок (например, `stock`).
- `--market <MARKET>`: Обязательный. Рынок (например, `shares`).
- `--board <BOARD>`: Обязательный. Режим торгов (например, `TQBR`).
- `--date <YYYY-MM-DD>`: Опционально. Конкретная дата для загрузки данных.
- `--from-date <YYYY-MM-DD>`: Опционально. Начальная дата диапазона для загрузки данных.
- `--to-date <YYYY-MM-DD>`: Опционально. Конечная дата диапазона для загрузки данных.
- `--output <FILE_PATH>`: Опционально. Путь к файлу для сохранения данных в формате JSON.
- `--to-clickhouse`: Опционально. Флаг для прямой загрузки данных в ClickHouse.

**Важно:** Вы должны указать либо `--date`, либо обе опции `--from-date` и `--to-date`. Использование `--date` вместе с `--from-date` или `--to-date` приведет к ошибке.

### Примеры использования:

1.  **Загрузка данных за одну дату в JSON:**
    ```bash
    moex-client history --engine stock --market shares --board TQBR --date 2023-10-01 --output data.json
    ```

2.  **Загрузка данных за период в JSON:**
    ```bash
    moex-client history --engine stock --market shares --board TQBR \
      --from-date 2023-10-01 --to-date 2023-10-05 --output data.json
    ```

3.  **Загрузка данных за одну дату напрямую в ClickHouse:**
    ```bash
    moex-client history --engine stock --market shares --board TQBR --date 2023-10-01 --to-clickhouse
    ```

4.  **Загрузка данных за период напрямую в ClickHouse:**
    ```bash
    moex-client history --engine stock --market shares --board TQBR \
      --from-date 2023-10-01 --to-date 2023-10-05 --to-clickhouse
    ```

## 4. Использование Python API

Вы также можете использовать клиент программно:

```python
from moex_client import MoexClient
from moex_client.config import Settings
import datetime

# Инициализация клиента
settings = Settings()
client = MoexClient(settings)

# Аутентификация
client.authenticate()

# Получение данных за одну дату
data_single_date = client.get_historical_securities(
    engine="stock",
    market="shares", 
    board="tqbr",
    date="2023-01-15"
)
print(f"Данные за 2023-01-15: {data_single_date}")

# Пример загрузки данных за период (потребуется цикл)
start_date = datetime.date(2023, 10, 1)
end_date = datetime.date(2023, 10, 5)
all_data_range = []
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    data_day = client.get_historical_securities(
        engine="stock", market="shares", board="tqbr", date=date_str
    )
    all_data_range.extend(data_day)
    current_date += datetime.timedelta(days=1)
print(f"Данные за период: {all_data_range}")
```

## 5. Работа с ClickHouse

### Запуск окружения

Для работы с ClickHouse используется Docker. Убедитесь, что у вас установлен и запущен Docker, затем выполните в корневой директории проекта:
```bash
docker-compose up -d
```
Эта команда поднимет два контейнера:
- `clickhouse-server`: Сервер ClickHouse, доступный по порту `9000` (для нативного протокола) и `8123` (для HTTP).
- `grafana`: Веб-интерфейс для работы с данными, доступный по адресу `http://localhost:3000`.

### Настройка Grafana
1.  Откройте Grafana в браузере: `http://localhost:3000`.
2.  Войдите, используя логин `admin` и пароль `admin`.
3.  Добавьте ClickHouse как источник данных:
    - Перейдите в `Configuration > Data Sources > Add data source`.
    - Выберите `ClickHouse`.
    - В разделе `HTTP`:
        - `URL`: `http://clickhouse-server:8123` (это имя сервиса из `docker-compose.yml`, оно работает из Grafana, так как они находятся в одной Docker-сети).
        - `Access`: `Server (default)`
    - В разделе `ClickHouse Details`:
        - `Default database`: `moex`
        - `Default table`: `securities_history`
        - `User`: `default`
        - `Password`: (оставьте пустым, если не меняли в `docker-compose.yml`)
    - Нажмите `Save & Test`.

Теперь вы можете выполнять SQL-запросы к вашей базе данных ClickHouse через интерфейс Grafana, например:
```sql
SELECT * FROM moex.securities_history LIMIT 10;
```

## 6. Разработка

### Установка для разработки

```bash
pip install -e ".[dev]"
```

### Запуск тестов

```bash
pytest
```

### Форматирование кода

```bash
black src/ tests/
isort src/ tests/
```

### Проверка кода

```bash
flake8 src/ tests/
