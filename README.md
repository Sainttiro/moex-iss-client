# MOEX ISS Client

Современный Python клиент для работы с API Информационно-статистического сервера (ИСС) Московской Биржи.

## Возможности

- 🔐 Безопасная аутентификация через переменные окружения
- 📈 Загрузка исторических данных по ценным бумагам
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

# Получение данных
data = client.get_historical_securities(
    engine="stock",
    market="shares", 
    board="tqbr",
    date="2023-01-15"
)
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

## Лицензия

MIT License
