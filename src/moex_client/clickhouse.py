from clickhouse_driver import Client
from .config import Settings

class ClickHouseClient:
    """
    Client for interacting with ClickHouse.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = Client(
            host=self.settings.CLICKHOUSE_HOST,
            port=self.settings.CLICKHOUSE_PORT,
            database=self.settings.CLICKHOUSE_DB,
            user=self.settings.CLICKHOUSE_USER,
            password=self.settings.CLICKHOUSE_PASSWORD,
        )

    def create_table(self):
        """
        Creates the securities_history table if it doesn't exist.
        """
        query = """
        CREATE TABLE IF NOT EXISTS securities_history (
            BOARDID String,
            TRADEDATE Date,
            SHORTNAME String,
            SECID String,
            NUMTRADES Float64,
            VALUE Float64,
            OPEN Float64,
            LOW Float64,
            HIGH Float64,
            LEGALCLOSEPRICE Float64,
            WAPRICE Float64,
            CLOSE Float64,
            VOLUME Float64,
            MARKETPRICE2 Float64,
            MARKETPRICE3 Float64,
            ADMITTEDQUOTE Float64,
            MP2VALTRD Float64,
            MARKETPRICE3TRADESVALUE Float64,
            ADMITTEDVALUE Float64,
            WAVAL Float64
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(TRADEDATE)
        ORDER BY (TRADEDATE, SECID);
        """
        self.client.execute(query)

    def insert_data(self, data: list):
        """
        Inserts data into the securities_history table.
        """
        if not data:
            return
        self.client.execute("INSERT INTO securities_history VALUES", data)

    def create_session_summary_table(self):
        """
        Creates the session_summary table if it doesn't exist.
        """
        query = """
        CREATE TABLE IF NOT EXISTS session_summary (
            SECID String,
            BOARDID String,
            TRADINGSESSION String,
            TIME String,
            PRICEMINUSPREVWAPRICE Float64,
            VOLTODAY Float64,
            VALTODAY Float64,
            HIGHBID Float64,
            LOWOFFER Float64,
            LASTOFFER Float64,
            LASTBID Float64,
            OPEN Float64,
            LOW Float64,
            HIGH Float64,
            LAST Float64,
            LCLOSEPRICE Float64,
            NUMTRADES Float64,
            WAPRICE Float64,
            MARKETPRICE2 Float64,
            LCURRENTPRICE Float64,
            CLOSINGAUCTIONPRICE Float64,
            LASTTOPREVPRICE Float64,
            load_date Date
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(load_date)
        ORDER BY (load_date, SECID);
        """
        self.client.execute(query)

    def insert_session_summary_data(self, data: list):
        """
        Inserts data into the session_summary table.
        """
        if not data:
            return
        self.client.execute("INSERT INTO session_summary VALUES", data)
