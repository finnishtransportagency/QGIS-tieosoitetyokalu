import requests
from requests.adapters import HTTPAdapter, Retry
from typing import Optional
from qgis.PyQt import QtCore, QtWidgets

class VKMAPIRequests:
    def __init__(self) -> None:
        self.vkm_url = "https://avoinapi.vaylapilvi.fi/viitekehysmuunnin/"
        
    def create_session():
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.trust_env = True
        return session

    def load_proxies_from_settings(subgroup: str = "proxySettings", same_for_both: bool = True) -> dict[str, str] | None:
        """Loads saved proxy settings if they exist.

        Args:
            subgroup (str, optional): Specifiy proxy settings group name. Defaults to "proxySettings".
            same_for_both (bool, optional): If HTTPS-address is missing, use given HTTP-address for both proxy settings: http and https. Defaults to True.

        Returns:
            proxies (dict[str, str] | None): Returns a dictionary of proxies or None. Both can be used in session.get(proxies=proxies)
        """
        s = QtCore.QSettings()
        s.beginGroup("QGIS-tieosoitetyokalu")
        try:
            http = s.value(f"{subgroup}/http", "", type=str).strip()
            https = s.value(f"{subgroup}/https", "", type=str).strip()
        finally:
            s.endGroup()

        proxies = {}
        if http:
            proxies["http"] = http if "://" in http else f"http://{http}"
            if same_for_both and not https:
                proxies["https"] = proxies["http"]
        if https:
            proxies["https"] = https if "://" in https else f"http://{https}"
        # NOTE: requests doesn’t accept no_proxy in the proxies dict;
        # it uses the NO_PROXY env if session.trust_env=True.

        return proxies or None
