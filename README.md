# MOEX ISS Client

Современный Python клиент для работы с API Информационно-статистического сервера (ИСС) Московской Биржи.

## Возможности

- 🔐 Безопасная аутентификация через переменные окружения
- 📈 Загрузка исторических данных по ценным бумагам
- 📊 Получение промежуточных итогов торговой сессии TQBR
- 🗄️ Экспорт данных в JSON и ClickHouse
- 🖥️ Удобный командный интерфейс (CLI)
- 📊 Прогресс-бары для длительных операций
- 🧪 Покрытие тестами
- 🛠️ Modern Python packaging (pyproject.toml)

## Использование

Подробное руководство по установке, настройке и использованию клиента доступно в файле [USAGE.md](USAGE.md).

## Установка

### Требования
- Python 3.8+
- Docker и Docker Compose
- Аккаунт в MOEX ISS для доступа к историческим данным

### Настройка проекта

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Sainttiro/moex-iss-client.git
cd moex-iss-client
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -e .
```

4. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив свои учетные данные MOEX
```

## Конфигурация

Создайте файл `.env` с вашими учетными данными:

```env
MOEX_USERNAME=your_username
MOEX_PASSWORD=your_password
MOEX_BASE_URL=https://iss.moex.com
MOEX_AUTH_URL=https://passport.moex.com/authenticate
```

## Использование

### Командная строка

```bash
# Загрузить данные за одну дату в JSON
moex-client history --engine stock --market shares --board TQBR --date 2023-10-01 --output data.json

# Загрузить данные за период в JSON
moex-client history --engine stock --market shares --board TQBR \
  --from-date 2023-10-01 --to-date 2023-10-05 --output data.json

# Загрузить данные за одну дату напрямую в ClickHouse
moex-client history --engine stock --market shares --board TQBR --date 2023-10-01 --to-clickhouse

# Загрузить данные за период напрямую в ClickHouse
moex-client history --engine stock --market shares --board TQBR \
  --from-date 2023-10-01 --to-date 2023-10-05 --to-clickhouse

# Получить данные о текущей торговой сессии TQBR
moex-client session-summary --output session_data.json

# Загрузить данные о текущей торговой сессии в ClickHouse
moex-client session-summary --to-clickhouse
```

### Python API

```python
from moex_client import MoexClient
from moex_client.config import Settings

# Инициализация клиента
settings = Settings()
client = MoexClient(settings)

# Аутентификация
client.authenticate()

# Получение исторических данных
data = client.get_historical_securities(
    engine="stock",
    market="shares", 
    board="tqbr",
    date="2023-01-15"
)

# Получение данных о текущей торговой сессии
from moex_client.client.session_api import MoexSessionClient
session_client = MoexSessionClient()
session_data = session_client.get_tqbr_summary()
```

## Разработка

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
```

## Структура проекта

```
src/moex_client/
├── auth/          # Аутентификация
├── client/        # API клиенты
├── config/        # Конфигурация
├── models/        # Модели данных
└── cli/           # Командная строка
```

## Автоматизация с Airflow

В проект интегрирован Apache Airflow для автоматизации ежедневной загрузки данных.

### Запуск Airflow

1.  **Запустите все сервисы:**
    ```bash
    docker-compose up -d
    ```
    Эта команда запустит все сервисы, включая ClickHouse, Grafana, Superset и Airflow.

2.  **Доступ к Airflow UI:**
    Веб-интерфейс Airflow будет доступен по адресу `http://localhost:8080`.
    *   **Логин:** `admin`
    *   **Пароль:** `admin`

### DAGs для Airflow

- **`moex_daily_load`**: DAG настроен для ежедневного запуска в 6 утра по московскому времени. Он выполняет скрипт `scripts/daily_load.py`, который загружает исторические данные за предыдущий торговый день в ClickHouse.

- **`moex_tqbr_summary_dag`**: DAG настроен для запуска каждый рабочий день в 19:00 (после закрытия торгов). Он вызывает команду `moex-client session-summary --to-clickhouse` для получения промежуточных итогов по акциям TQBR и сохранения их в ClickHouse.

## Лицензия

MIT License
