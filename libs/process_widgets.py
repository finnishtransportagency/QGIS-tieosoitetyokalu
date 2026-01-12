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


from qgis.PyQt import QtCore, QtWidgets
from collections import defaultdict
import re


class WidgetValidator:
    def __init__(self):
        self.url_regex = re.compile(r"""
        ^
        https?://                                    # scheme: http or https, case-insensitive
        (?:                                          
            # optional user:pass authentication (URL encoded characters allowed)
            (?:[A-Za-z0-9\-._~%!$&'()*+,;=]+@)?
        )
        (                                             # begin host group
            (?:                                         
                # IPv4 address, each octet 0-255 (approximate, enforces 0-255)
                (?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}
                (?:25[0-5]|2[0-4]\d|1?\d{1,2})
            )
            |
            (?:                                         
                # IPv6 address in brackets (basic check; does not fully validate IPv6 rules)
                \[[0-9A-Fa-f:.]+\]
            )
            |
            (?:                                         
                # hostnames: multiple labels (label.label.tld). Labels may contain letters, digits, hyphens,
                # cannot start or end with hyphen, and TLD is alphabetic (2+ chars).
                (?:(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)\.)+
                (?:[A-Za-z]{2,})
            )
            |
            (?:localhost)                               # allow localhost
            |
            (?:                                         
                # single-label host (intranets), 1-63 chars, letters/digits/hyphen allowed
                [A-Za-z0-9-]{1,63}
            )
        )
        (?::\d{1,5})?                                 # optional port (1-5 digits; does not enforce <= 65535)
        (?:[/?#][^\s]*)?                              # optional path, query, fragment (no whitespace)
        $
        """, re.VERBOSE | re.IGNORECASE)

    def _collect_widgets_by_group(self, widgets: list[QtWidgets.QWidget]):
        """Collect interactive widgets by their settings group.

        Args:
            widgets (list[QtWidgets.QWidget]): A list of QT widgets to sort.

        Returns:
            dict[str, list]: A dictionary of lists of widgets. Each list contains widgets specific to their settings group.
        """
        widgets_by_group = defaultdict(list)
        for w in widgets:
            widgets_by_group[w.property("settingsGroup")].append(w)
        return widgets_by_group

    def validate_widgets(self, widgets: list[QtWidgets.QWidget]):
        """Validate interactive QT widgets based on their group (= a custom widget property) and type.

        Args:
            widgets (list[QtWidgets.QWidget]): A list of QT widgets to validate.

        Returns:
            invalid_groups (set): The names of the groups that contain invalid widget inputs.
        """
        widgets_by_group = self._collect_widgets_by_group(widgets)
        invalid_groups = set()
        for group_name, widget_group in widgets_by_group.items():
            if group_name == "proxySettings":
                if not self._validate_proxy_widgets(widget_group):
                    invalid_groups.add(self.tr(u"Proxy-asetukset"))
        return invalid_groups

    def _validate_proxy_widgets(self, widget_group: list[QtWidgets.QWidget]):
        """Validate widgets of 'proxySettings' group by counting the sum of invalid inputs.

        Args:
            widget_group (list[QtWidgets.QWidget]): Proxy settings widgets. (So far only QLineEdit types).

        Returns:
            bool: Returns True if the count of invalid inputs is above zero.
        """
        invalid_inputs = 0

        for w in widget_group:
            ok = self._validate_proxy_lineedit(w, allow_empty=True)
            if not ok:
                invalid_inputs += 1
        return invalid_inputs == 0
    
    def _validate_proxy_lineedit(self, lineedit: QtWidgets.QLineEdit, allow_empty: bool = True):
        """
        Validate a single QLineEdit using self.url_regex.
        - allow_empty=True treats empty string as valid (useful to allow "no proxy").
        - Returns True if valid.
        - Sets a red/green border and a helpful tooltip.
        """
        text = lineedit.text().strip()

        if not text:
            if allow_empty:
                lineedit.setStyleSheet("")        # clear style for default look
                lineedit.setToolTip("")          # clear any tooltip
                return True
            else:
                lineedit.setStyleSheet("border: 1px solid red;")
                lineedit.setToolTip("Proxy URL required (e.g. http://host:port)")
                return False

        # fullmatch ensures the entire value matches (your pattern already uses ^...$)
        if self.url_regex.fullmatch(text):
            lineedit.setStyleSheet("border: 1px solid #2ecc71;")   # green
            lineedit.setToolTip("")
            return True
        else:
            lineedit.setStyleSheet("border: 1px solid #e74c3c;")   # red
            lineedit.setToolTip(self.tr(u'Virheellinen URL-osoite – täytyy alkaa skeemasta: "http://" tai "https://"'))
            return False
        
    @staticmethod
    def tr(message, disambiguation="", n=-1):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QtCore.QCoreApplication.translate('WidgetValidator', message, disambiguation, n)