from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    MOEX_USERNAME: str
    MOEX_PASSWORD: str
    MOEX_BASE_URL: str = "https://iss.moex.com"
    MOEX_AUTH_URL: str = "https://passport.moex.com/authenticate"

    # ClickHouse settings
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_DB: str = "moex"
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""

    # ClickHouse day session settings
    CLICKHOUSE_DAY_SESSION_DB: str = "moex_day_session"
