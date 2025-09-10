import requests
import json
from typing import List, Dict, Any
import time
from datetime import datetime

class MOEXTQBRFetcher:
    """
    Класс для получения данных промежуточных итогов дня по инструментам режима TQBR
    только для основной (дневной) торговой сессии
    """
    
    def __init__(self, delay: float = 0.1):
        """
        Инициализация
        
        Args:
            delay: задержка между запросами в секундах
        """
        self.base_url = "https://iss.moex.com/iss"
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Python MOEX API Client'
        })
    
    def get_tqbr_securities_list(self) -> List[str]:
        """
        Получить список всех инструментов режима TQBR
        
        Returns:
            Список тикеров инструментов
        """
        url = f"{self.base_url}/engines/stock/markets/shares/boards/TQBR/securities.json"
        params = {
            'iss.only': 'securities',
            'securities.columns': 'SECID'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            securities = []
            if 'securities' in data and 'data' in data['securities']:
                securities = [row[0] for row in data['securities']['data'] if row[0]]
            
            print(f"Найдено {len(securities)} инструментов в режиме TQBR")
            return securities
            
        except requests.RequestException as e:
            print(f"Ошибка при получении списка инструментов: {e}")
            return []
    
    def get_secstats_batch(self, securities_batch: List[str], session: int = 1) -> Dict[str, Any]:
        """
        Получить промежуточные итоги дня для группы инструментов
        
        Args:
            securities_batch: список тикеров (не более 10)
            session: номер торговой сессии (1 - дневная, 2 - вечерняя, 3 - итого)
            
        Returns:
            Данные по промежуточным итогам
        """
        if len(securities_batch) > 10:
            raise ValueError("Максимальное количество инструментов в одном запросе: 10")
        
        url = f"{self.base_url}/engines/stock/markets/shares/secstats.json"
        params = {
            'securities': ','.join(securities_batch),
            'tradingsession': session
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            print(f"Получены данные для {len(securities_batch)} инструментов")
            return data
            
        except requests.RequestException as e:
            print(f"Ошибка при получении данных для {securities_batch}: {e}")
            return {}
    
    def get_all_tqbr_day_session_data(self) -> List[Dict[str, Any]]:
        """
        Получить промежуточные итоги дня для всех инструментов TQBR
        только для основной (дневной) торговой сессии
        
        Returns:
            Список результатов по всем батчам
        """
        print("Начинаем получение данных по TQBR для дневной сессии...")
        
        # Получаем список всех инструментов TQBR
        all_securities = self.get_tqbr_securities_list()
        if not all_securities:
            print("Не удалось получить список инструментов")
            return []
        
        # Разбиваем на группы по 10
        batches = [all_securities[i:i+10] for i in range(0, len(all_securities), 10)]
        results = []
        
        print(f"Будет выполнено {len(batches)} запросов для {len(all_securities)} инструментов")
        
        for i, batch in enumerate(batches, 1):
            print(f"\nОбрабатываем батч {i}/{len(batches)}: {', '.join(batch)}")
            
            # Получаем данные для текущего батча (сессия 1 = дневная)
            data = self.get_secstats_batch(batch, session=1)
            if data:
                results.append({
                    'batch_number': i,
                    'securities': batch,
                    'data': data
                })
            
            # Задержка между запросами
            if i < len(batches):
                time.sleep(self.delay)
        
        print(f"\nЗавершено. Получены данные для {len(results)} батчей")
        return results
    
    def process_and_combine_data(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Обработать и объединить данные из всех батчей
        
        Args:
            batch_results: результаты всех батчей
            
        Returns:
            Объединенные данные
        """
        if not batch_results:
            return {}
        
        # Берем структуру из первого результата
        combined_data = {
            'secstats': {
                'columns': None,
                'data': []
            },
            'metadata': {
                'total_batches': len(batch_results),
                'total_securities': 0,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        for result in batch_results:
            if 'data' in result and 'secstats' in result['data']:
                secstats = result['data']['secstats']
                
                # Устанавливаем колонки из первого результата
                if combined_data['secstats']['columns'] is None:
                    combined_data['secstats']['columns'] = secstats.get('columns', [])
                
                # Добавляем данные
                if 'data' in secstats:
                    combined_data['secstats']['data'].extend(secstats['data'])
                    combined_data['metadata']['total_securities'] += len(secstats['data'])
        
        return combined_data
    
    def save_to_file(self, data: Dict[str, Any], filename: str = None):
        """
        Сохранить данные в JSON файл
        
        Args:
            data: данные для сохранения
            filename: имя файла (если не указано, будет сгенерировано автоматически)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tqbr_day_session_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Данные сохранены в файл: {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")


def main():
    """
    Основная функция для запуска получения данных
    """
    # Создаем экземпляр класса
    fetcher = MOEXTQBRFetcher(delay=0.2)  # задержка 200мс между запросами
    
    # Получаем все данные
    batch_results = fetcher.get_all_tqbr_day_session_data()
    
    if batch_results:
        # Объединяем данные
        combined_data = fetcher.process_and_combine_data(batch_results)
        
        # Выводим статистику
        total_instruments = combined_data.get('metadata', {}).get('total_securities', 0)
        print(f"\nИтого обработано инструментов: {total_instruments}")
        
        # Сохраняем в файл
        fetcher.save_to_file(combined_data)
        
        # Выводим пример данных
        if combined_data.get('secstats', {}).get('data'):
            print("\nПример данных (первые 3 строки):")
            columns = combined_data['secstats']['columns']
            for i, row in enumerate(combined_data['secstats']['data'][:3]):
                print(f"Строка {i+1}: {dict(zip(columns, row))}")
    
    else:
        print("Не удалось получить данные")


if __name__ == "__main__":
    main()