import click
import json
import datetime
from rich.console import Console
from rich.progress import track

from ..client import MoexClient
from ..config import Settings
from ..clickhouse import ClickHouseClient


@click.group()
def cli():
    """
    CLI for the MOEX ISS Client.
    """
    pass


@cli.command()
@click.option("--engine", required=True, help="Engine")
@click.option("--market", required=True, help="Market")
@click.option("--board", required=True, help="Board")
@click.option("--from-date", required=True, help="Start date in YYYY-MM-DD format")
@click.option("--to-date", required=True, help="End date in YYYY-MM-DD format")
@click.option("--output", help="Output file path (JSON)")
@click.option("--to-clickhouse", is_flag=True, help="Load data directly to ClickHouse")
def history(engine: str, market: str, board: str, from_date: str, to_date: str, output: str, to_clickhouse: bool):
    """
    Retrieves historical securities data for a date range.
    """
    console = Console()
    try:
        settings = Settings()
        client = MoexClient(settings)
        
        start_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
        
        total_days = (end_date - start_date).days + 1
        
        if to_clickhouse:
            ch_client = ClickHouseClient(settings)
            console.print("[bold cyan]Creating ClickHouse table if not exists...[/bold cyan]")
            ch_client.create_table()
            
            for i in track(range(total_days), description="Fetching and loading to ClickHouse..."):
                current_date = start_date + datetime.timedelta(days=i)
                date_str = current_date.strftime("%Y-%m-%d")
                
                data = client.get_historical_securities(
                    engine=engine, market=market, board=board, date=date_str
                )
                if data:
                    # Convert TRADEDATE string to datetime.date object
                    for row in data:
                        row['TRADEDATE'] = datetime.datetime.strptime(row['TRADEDATE'], '%Y-%m-%d').date()
                    ch_client.insert_data(data)
            console.print("[bold green]Data successfully loaded to ClickHouse.[/bold green]")
        else:
            all_data = []
            for i in track(range(total_days), description="Fetching data..."):
                current_date = start_date + datetime.timedelta(days=i)
                date_str = current_date.strftime("%Y-%m-%d")
                
                data = client.get_historical_securities(
                    engine=engine, market=market, board=board, date=date_str
                )
                all_data.extend(data)

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=4)
                console.print(f"[bold green]Data saved to {output}[/bold green]")
            else:
                console.print(all_data)

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


if __name__ == "__main__":
    cli()
