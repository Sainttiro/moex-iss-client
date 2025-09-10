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


class ClickHouseDaySessionClient:
    """
    Client for interacting with ClickHouse for day session data.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = Client(
            host=self.settings.CLICKHOUSE_HOST,
            port=self.settings.CLICKHOUSE_PORT,
            database=self.settings.CLICKHOUSE_DAY_SESSION_DB,
            user=self.settings.CLICKHOUSE_USER,
            password=self.settings.CLICKHOUSE_PASSWORD,
        )
        self.client.execute(f"CREATE DATABASE IF NOT EXISTS {self.settings.CLICKHOUSE_DAY_SESSION_DB}")

    def create_table(self):
        """
        Creates the day_session_securities table if it doesn't exist.
        """
        query = """
        CREATE TABLE IF NOT EXISTS day_session_securities (
            SECID String,
            BOARDID String,
            UPDATETIME String,
            LASTTRADETIME String,
            TRADINGSESSION Int32,
            SYSTIME DateTime,
            OPEN Float64,
            HIGH Float64,
            LOW Float64,
            LAST Float64,
            LASTCHANGE Float64,
            LASTCHANGEPRCNT Float64,
            QTY Int64,
            VALUE Float64,
            YIELD Float64,
            YIELDDATE String,
            YIELDTOOFFER Float64,
            YIELDTOOFFERDATE String,
            NUMTRADES Int64,
            VOLTODAY Int64,
            VALTODAY Float64,
            VALTODAY_USD Float64,
            LASTTOPREVPRICE Float64,
            AUCTPRICE Float64,
            AUCTVALUE Float64,
            WAPRICE Float64,
            HIGHBID Float64,
            LOWOFFER Float64,
            PRICEMINUSPREVWAPRICE Float64,
            CLOSEPRICE Float64,
            LASTBID Float64,
            LASTOFFER Float64,
            LCLOSEPRICE Float64,
            MARKETPRICETODAY Float64,
            MARKETPRICE Float64,
            OPENPERIODPRICE Float64,
            SEQNUM Int64,
            SYSTIME_DATE Date MATERIALIZED toDate(SYSTIME)
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(SYSTIME_DATE)
        ORDER BY (SYSTIME_DATE, SECID);
        """
        self.client.execute(query)

    def insert_data(self, data: list):
        """
        Inserts data into the day_session_securities table.
        """
        if not data:
            return
        self.client.execute("INSERT INTO day_session_securities VALUES", data)
