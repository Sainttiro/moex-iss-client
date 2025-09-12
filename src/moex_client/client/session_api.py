import logging
from typing import List, Dict, Any

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class MoexSessionClient:
    """
    Клиент для получения данных о торговой сессии с MOEX ISS API.
    """

    def __init__(self):
        self._base_url = "https://iss.moex.com"

    def get_tqbr_summary(self) -> List[Dict[str, Any]]:
        """
        Получает промежуточные итоги по акциям MOEX TQBR.

        :return: Список словарей с данными по ценным бумагам.
        :raises RequestException: В случае ошибки сети.
        :raises ValueError: В случае ошибки парсинга JSON.
        """
        url = f"{self._base_url}/iss/engines/stock/markets/shares/secstats.json"
        params = {
            'boardid': 'TQBR',
            'tradingsession': '1',
            'iss.meta': 'off',
            'iss.only': 'secstats'
        }

        logger.info("Отправляем запрос к MOEX API для получения итогов сессии...")
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()  # Проверка на HTTP ошибки

            json_data = response.json()
            secstats = json_data.get('secstats', {})
            columns = secstats.get('columns', [])
            data = secstats.get('data', [])

            if not data:
                logger.warning("Получены пустые данные от API")
                return []

            # Фильтруем данные, чтобы убедиться, что boardid='TQBR'
            filtered_data = [row for row in data if row[1] == 'TQBR']
            logger.info(f"Получено {len(filtered_data)} записей для TQBR (основная сессия)")

            # Преобразуем список списков в список словарей
            result = [dict(zip(columns, row)) for row in filtered_data]
            return result

        except RequestException as e:
            logger.error(f"Ошибка при запросе к API: {e}")
            raise
        except ValueError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            raise
