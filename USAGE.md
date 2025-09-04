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

*   `--engine <ENGINE>`: **Обязательный.** Указывает движок торговой системы. Например: `stock` (фондовый рынок), `currency` (валютный рынок).
*   `--market <MARKET>`: **Обязательный.** Указывает рынок. Например: `shares` (акции), `bonds` (облигации), `futures` (фьючерсы).
*   `--board <BOARD>`: **Обязательный.** Указывает режим торгов (торговую доску). Например: `TQBR` (основной режим торгов акциями), `SMAL` (акции малой капитализации).

*   `--date <YYYY-MM-DD>`: **Опционально.** Позволяет загрузить данные за одну конкретную дату. Формат даты: `ГГГГ-ММ-ДД`.
*   `--from-date <YYYY-MM-DD>`: **Опционально.** Указывает начальную дату диапазона для загрузки данных. Используется в паре с `--to-date`. Формат даты: `ГГГГ-ММ-ДД`.
*   `--to-date <YYYY-MM-DD>`: **Опционально.** Указывает конечную дату диапазона для загрузки данных. Используется в паре с `--from-date`. Формат даты: `ГГГГ-ММ-ДД`.

    **Важно:** Вы должны указать либо `--date` (для одной даты), либо обе опции `--from-date` и `--to-date` (для диапазона дат). Использование `--date` вместе с `--from-date` или `--to-date` приведет к ошибке.

*   `--output <FILE_PATH>`: **Опционально.** Путь к файлу, в который будут сохранены полученные данные в формате JSON. Если эта опция не указана, данные будут выведены в консоль.
*   `--to-clickhouse`: **Опционально.** Флаг. Если указан, данные будут загружены напрямую в ClickHouse, минуя сохранение в JSON-файл.

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

## 5. Работа с ClickHouse и Superset

### Запуск окружения

Для работы с ClickHouse и Superset используется Docker. Убедитесь, что у вас установлен и запущен Docker, затем выполните в корневой директории проекта:
```bash
docker-compose up -d
```
Эта команда поднимет три контейнера:
- `clickhouse-server`: Сервер ClickHouse, доступный по порту `9000` (для нативного протокола) и `8123` (для HTTP).
- `grafana`: Веб-интерфейс для работы с данными, доступный по адресу `http://localhost:3000`.
- `superset`: Веб-интерфейс Superset, доступный по адресу `http://localhost:8088`.

### Настройка Grafana

Источник данных ClickHouse настраивается автоматически при первом запуске Grafana.

1.  Откройте Grafana в браузере: `http://localhost:3000`.
2.  Войдите, используя логин `admin` и пароль `admin`.
3.  Перейдите в `Configuration > Data Sources`, и вы увидите, что источник данных `ClickHouse` уже добавлен.

Теперь вы можете выполнять SQL-запросы к вашей базе данных ClickHouse через интерфейс Grafana, например:
```sql
SELECT * FROM moex.securities_history LIMIT 10;
```

### Настройка Superset

Подробное руководство по настройке и подключению Superset к ClickHouse доступно в файле [SUPERSET.md](SUPERSET.md).

### Запуск Airflow

Для автоматизации загрузки данных используется Apache Airflow.

1.  **Запустите все сервисы:**
    ```bash
    docker-compose up -d
    ```
2.  **Доступ к Airflow UI:**
    Веб-интерфейс Airflow будет доступен по адресу `http://localhost:8080`.
    *   **Логин:** `admin`
    *   **Пароль:** `admin`

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
