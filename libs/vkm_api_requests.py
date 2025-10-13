"""
/*

* Copyright 2022 Finnish Transport Infrastructure Agency
*

* Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the European Commission - subsequent versions of the EUPL (the "Licence");
* You may not use this work except in compliance with the Licence.
* You may obtain a copy of the Licence at:
*
* https://joinup.ec.europa.eu/sites/default/files/custom-page/attachment/2020-03/EUPL-1.2%20EN.txt
*
* Unless required by applicable law or agreed to in writing, software distributed under the Licence is distributed on an "AS IS" basis,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the Licence for the specific language governing permissions and limitations under the Licence.
*/
"""


import requests
from requests.adapters import HTTPAdapter, Retry
from qgis.PyQt import QtCore

class VKMAPIRequests:
    def __init__(self) -> None:
        self.vkm_url = "https://avoinapi.vaylapilvi.fi/viitekehysmuunnin/"
        
    def create_session(self):
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.trust_env = True
        return session

    def load_proxies_from_settings(self, subgroup: str = "proxySettings", same_for_both: bool = True) -> dict[str, str] | None:
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
