import requests
from typing import Any, Dict, List

from ..auth import MoexAuth
from ..config import Settings


class MoexClient:
    """
    Client for the Moscow Exchange ISS API.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.auth = MoexAuth(settings)
        self.session = requests.Session()

    def authenticate(self):
        """
        Authenticates the client.
        """
        self.auth.authenticate()
        self.session.cookies.update(self.auth.get_cookies())

    def get_historical_securities(
        self, engine: str, market: str, board: str, date: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves historical securities data for a given date.
        """
        if not self.auth.is_authenticated():
            self.authenticate()

        url = f"{self.settings.MOEX_BASE_URL}/iss/history/engines/{engine}/markets/{market}/boards/{board}/securities.json"
        params = {"date": date}
        
        all_data = []
        start = 0
        while True:
            params["start"] = start
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            history_data = data.get("history", {})
            columns = history_data.get("columns", [])
            rows = history_data.get("data", [])

            if not rows:
                break

            for row in rows:
                all_data.append(dict(zip(columns, row)))

            start += len(rows)

        return all_data
