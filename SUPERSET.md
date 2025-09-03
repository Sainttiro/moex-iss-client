# Руководство по использованию Apache Superset

Этот документ предоставляет инструкции по настройке и использованию Apache Superset в проекте `moex-iss-client`.

## 1. Запуск окружения

Для работы с Superset используется Docker. Убедитесь, что у вас установлен и запущен Docker, затем выполните в корневой директории проекта:
```bash
docker-compose up -d
```
Эта команда поднимет следующие контейнеры:
- `clickhouse-server`: Сервер ClickHouse.
- `grafana`: Веб-интерфейс Grafana.
- `superset`: Веб-интерфейс Superset, доступный по адресу `http://localhost:8088`.

## 2. Первоначальная настройка Superset

При первом запуске Superset необходимо выполнить несколько команд для его инициализации.

1.  **Создание администратора:**
    Выполните следующую команду, чтобы создать пользователя-администратора. Замените `admin` на желаемое имя пользователя.
    ```bash
    docker-compose exec superset superset-init --username admin --firstname Superset --lastname Admin --email admin@superset.com --password admin
    ```

2.  **Инициализация базы данных:**
    ```bash
    docker-compose exec superset superset db upgrade
    ```

3.  **Установка драйвера ClickHouse:**
    Для подключения к ClickHouse необходимо установить соответствующий драйвер.
    ```bash
    docker-compose exec superset pip install clickhouse-connect
    ```

## 3. Подключение ClickHouse в Superset

1.  Откройте Superset в браузере: `http://localhost:8088`.
2.  Войдите, используя учетные данные, созданные на предыдущем шаге.
3.  Перейдите в `Data > Databases`.
4.  Нажмите на кнопку `+ DATABASE`.
5.  В поле `DATABASE NAME` введите `MOEX ClickHouse`.
6.  В поле `SQLALCHEMY URI` введите следующую строку подключения:
    ```
    clickhouse+native://default:@clickhouse-server:9000/moex
    ```
7.  Нажмите `Test Connection`. Если все настроено правильно, вы увидите сообщение `Connection looks good!`.
8.  Нажмите `ADD`.

Теперь вы можете создавать чарты и дашборды в Superset, используя данные из вашей базы данных ClickHouse.
