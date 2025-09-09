FROM apache/airflow:2.8.1

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Копируем проект внутрь контейнера
COPY . /opt/moex-iss-client
RUN chown -R airflow /opt/moex-iss-client

USER airflow

# Устанавливаем проект + clickhouse extras
RUN pip install --no-cache-dir --user /opt/moex-iss-client[clickhouse]
