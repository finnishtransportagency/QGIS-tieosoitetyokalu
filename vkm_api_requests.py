import requests
from requests.adapters import HTTPAdapter, Retry

class VKMAPIRequests:
    def __init__(self) -> None:
        self.vkm_url = "https://avoinapi.vaylapilvi.fi/viitekehysmuunnin/"
        self.proxy_urls = None
        self.session = None
        
    def create_session(self):
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def add_proxy_url(self, proxy_url:str):
        """Adds a proxy address to a dictionary which is within all GET-requests.

        Args:
            proxy_url (str): Proxy address given by the user through Settings dialog.
        """
        if not proxy_url:
            return
        
        proxy_url = proxy_url.strip().lower()
        proxy_prefix = proxy_url.split(":")[0]
        if self.proxy_urls:
            self.proxy_urls[proxy_prefix] = proxy_url
        else:
            self.proxy_urls = {proxy_prefix: proxy_url}