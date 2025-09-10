import sys
import os
from typing import List, Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.moex_client.client.today_api import MOEXTQBRFetcher
from src.moex_client.clickhouse import ClickHouseDaySessionClient
from src.moex_client.config import Settings

def main():
    """
    Main function to fetch and save TQBR day session data.
    """
    settings = Settings()
    
    # Initialize the fetcher and ClickHouse client
    fetcher = MOEXTQBRFetcher(delay=0.2)
    ch_client = ClickHouseDaySessionClient(settings)
    
    # Create the table if it doesn't exist
    ch_client.create_table()
    
    # Get all data
    batch_results = fetcher.get_all_tqbr_day_session_data()
    
    if batch_results:
        # Combine data
        combined_data = fetcher.process_and_combine_data(batch_results)
        
        # Extract data for ClickHouse
        secstats_data = combined_data.get('secstats', {}).get('data', [])
        
        if secstats_data:
            # Insert data into ClickHouse
            ch_client.insert_data(secstats_data)
            print(f"\nSuccessfully inserted {len(secstats_data)} rows into ClickHouse.")
        else:
            print("\nNo data to insert into ClickHouse.")
            
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main()
