# Карта проекта MOEX ISS Client

Этот документ описывает структуру проекта, назначение каждого скрипта и их взаимосвязи.

## 1. Структура проекта

```
.
├── .env.example                  # Пример файла с переменными окружения
├── .gitignore                    # Файлы, исключенные из Git
├── docker-compose.yml            # Конфигурация Docker Compose для запуска сервисов
├── pyproject.toml                # Конфигурация проекта и зависимостей
├── README.md                     # Основная информация о проекте
├── requirements.txt              # Список зависимостей Python
├── SUPERSET.md                   # Руководство по настройке Superset
├── USAGE.md                      # Руководство по использованию клиента
├── airflow/
│   └── Dockerfile                # Dockerfile для сборки образа Airflow
├── dags/
│   ├── moex_daily_load_dag.py    # DAG для Airflow для ежедневной загрузки данных
│   └── moex_tqbr_summary_dag.py  # DAG для Airflow для загрузки итогов сессии
├── scripts/
│   ├── daily_load.py             # Скрипт для загрузки данных за предыдущий день
│   ├── load_history_to_clickhouse.py # Скрипт для загрузки исторических данных
│   └── setup_dev.sh              # Скрипт для настройки окружения разработки
└── src/
    └── moex_client/
        ├── __init__.py
        ├── clickhouse.py         # Клиент для работы с ClickHouse
        ├── auth/
        │   ├── __init__.py
        │   └── api.py            # Логика аутентификации на MOEX
        ├── cli/
        │   ├── __init__.py
        │   └── main.py           # Реализация командного интерфейса (CLI)
        ├── client/
        │   ├── __init__.py
        │   ├── api.py            # Основной клиент для работы с MOEX ISS API
        │   └── session_api.py    # Клиент для получения данных о торговой сессии
        ├── config/
        │   ├── __init__.py
        │   └── settings.py       # Настройки приложения (Pydantic)
        └── models/
            └── __init__.py       # Модели данных (пока пустые)
```

## 2. Описание скриптов и модулей

### `src/moex_client/` - Основной исходный код клиента

*   **`config/settings.py`**: Определяет класс `Settings` с использованием `Pydantic` для управления конфигурацией приложения. Загружает переменные из `.env` файла, такие как учетные данные MOEX и параметры подключения к ClickHouse.
*   **`auth/api.py`**: Содержит класс `MoexAuth`, который отвечает за аутентификацию на сервере MOEX. Он отправляет запрос на `MOEX_AUTH_URL` с логином и паролем и сохраняет полученный cookie `MicexPassportCert`.
*   **`client/api.py`**: Содержит основной класс `MoexClient`. Он использует `MoexAuth` для аутентификации и выполняет запросы к MOEX ISS API для получения исторических данных по ценным бумагам. Реализует пагинацию для получения всех данных.
*   **`client/session_api.py`**: Содержит класс `MoexSessionClient` для получения данных о текущей торговой сессии MOEX TQBR. Не требует аутентификации и возвращает промежуточные итоги по акциям.
*   **`clickhouse.py`**: Содержит класс `ClickHouseClient` для взаимодействия с базой данных ClickHouse. Включает методы для создания таблиц `securities_history` и `session_summary`, а также методы для вставки данных в эти таблицы.
*   **`cli/main.py`**: Реализует командный интерфейс (CLI) с использованием библиотеки `click`. Включает команды:
    * `moex-client history` - загрузка исторических данных, указывая параметры (engine, market, board, даты) и выбирая, куда сохранять данные (JSON-файл или напрямую в ClickHouse).
    * `moex-client session-summary` - получение промежуточных итогов по акциям TQBR с возможностью сохранения в JSON или ClickHouse.

### `scripts/` - Вспомогательные скрипты

*   **`daily_load.py`**: Скрипт, предназначенный для автоматического запуска (например, через cron или Airflow). Он определяет дату предыдущего торгового дня и вызывает `moex-client history` для загрузки данных за этот день в ClickHouse.
*   **`load_history_to_clickhouse.py`**: Скрипт для загрузки исторических данных за указанный диапазон дат. Использует `MoexClient` напрямую. *Примечание: в текущей реализации используется `ClickHousePlaceholder`, что указывает на его возможно демонстрационный или устаревший характер.*
*   **`setup_dev.sh`**: Bash-скрипт для упрощения настройки окружения для разработки (создание виртуального окружения, установка зависимостей).

### `dags/` - Скрипты для Apache Airflow

*   **`moex_daily_load_dag.py`**: Определяет DAG (Directed Acyclic Graph) для Airflow. Этот DAG настроен на ежедневный запуск в 6 утра. Он вызывает скрипт `scripts/daily_load.py` внутри Docker-контейнера Airflow для автоматизации процесса загрузки данных.
*   **`moex_tqbr_summary_dag.py`**: Определяет DAG для Airflow, который запускается каждый рабочий день в 19:00 (после закрытия торгов). Он вызывает команду `moex-client session-summary --to-clickhouse` для получения промежуточных итогов по акциям TQBR и сохранения их в ClickHouse.

### Корневые файлы

*   **`docker-compose.yml`**: Оркестрирует запуск всех необходимых сервисов: ClickHouse, Grafana, Superset и Airflow. Определяет их конфигурации, порты и взаимодействие.
*   **`pyproject.toml`**: Современный стандарт для конфигурации Python-проектов. Содержит метаданные проекта, зависимости и настройки инструментов, таких как `black`, `isort`, `flake8`.

## 3. Взаимосвязи

1.  **Пользователь/CLI -> `cli/main.py`**: Пользователь запускает команды через `moex-client`. `cli/main.py` парсит аргументы.
2.  **`cli/main.py` -> `client/api.py`**: CLI создает экземпляр `MoexClient` для получения исторических данных с MOEX.
3.  **`cli/main.py` -> `client/session_api.py`**: CLI создает экземпляр `MoexSessionClient` для получения данных о текущей торговой сессии.
4.  **`cli/main.py` -> `clickhouse.py`**: Если указан флаг `--to-clickhouse`, CLI использует `ClickHouseClient` для сохранения данных в базу.
5.  **`client/api.py` -> `auth/api.py`**: `MoexClient` использует `MoexAuth` для аутентификации перед отправкой запросов на получение данных.
6.  **`client/api.py` -> `config/settings.py`**: Все ключевые модули (`MoexClient`, `MoexAuth`, `ClickHouseClient`) импортируют `Settings` для доступа к конфигурации.
7.  **Airflow (`dags/moex_daily_load_dag.py`) -> `scripts/daily_load.py`**: DAG в Airflow по расписанию запускает скрипт `daily_load.py`.
8.  **Airflow (`dags/moex_tqbr_summary_dag.py`) -> CLI**: DAG в Airflow по расписанию вызывает команду `moex-client session-summary`.
9.  **`scripts/daily_load.py` -> `cli/main.py`**: Скрипт `daily_load.py` формирует и выполняет команду `moex-client history`, по сути, программно используя CLI.
10. **Docker (`docker-compose.yml`)**: Запускает и связывает все внешние сервисы (ClickHouse, Airflow, Grafana, Superset), создавая единое окружение для работы всего приложения.
