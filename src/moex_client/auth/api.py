import requests
from http.cookiejar import CookieJar
from ..config.settings import Settings


class MoexAuth:
    """
    Handles authentication with the MOEX ISS API.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.passport_cookie = None

    def authenticate(self):
        """
        Authenticates with the MOEX Passport service and retrieves the passport cookie.
        """
        response = self.session.get(
            self.settings.MOEX_AUTH_URL,
            auth=(self.settings.MOEX_USERNAME, self.settings.MOEX_PASSWORD),
        )
        response.raise_for_status()

        self.passport_cookie = self.session.cookies.get("MicexPassportCert")
        if not self.passport_cookie:
            raise Exception("Authentication failed: MicexPassportCert cookie not found.")

    def get_cookies(self) -> CookieJar:
        """
        Returns the cookie jar from the session.
        """
        return self.session.cookies

    def is_authenticated(self) -> bool:
        """
        Checks if the authentication cookie is present.
        """
        # In a real application, you might want to check for cookie expiration as well.
        return self.passport_cookie is not None
