from qgis.PyQt import QtCore, QtWidgets
from collections import defaultdict
from ..CustomExceptions.InvalidSettingsException import InvalidSettingsException
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

    def _collect_widgets_by_group(self, widgets: list[QtWidgets.QWidget]) -> dict[str, list]:
        widgets_by_group = defaultdict(list)
        for w in widgets:
            widgets_by_group[w.property("settingsGroup")].append(w)
        return widgets_by_group

    def validate_widgets(self, widgets: list[QtWidgets.QWidget]):
        widgets_by_group = self._collect_widgets_by_group(widgets)
        invalid_groups = set()
        for group_name, widget_group in widgets_by_group.items():
            if group_name == "proxySettings":
                if not self._validate_proxy_widgets(widget_group):
                    invalid_groups.add(self.tr(u"Proxy-asetukset"))
        return invalid_groups

    def _validate_proxy_widgets(self, widget_group: list[QtWidgets.QWidget]) -> bool:
        invalid_inputs = 0

        for w in widget_group:
            ok = self._validate_proxy_lineedit(w, allow_empty=True)
            if not ok:
                invalid_inputs += 1
        return invalid_inputs == 0
    
    def _validate_proxy_lineedit(self, lineedit: QtWidgets.QLineEdit, allow_empty: bool = True) -> bool:
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
            lineedit.setToolTip("Valid URL")
            return True
        else:
            lineedit.setStyleSheet("border: 1px solid #e74c3c;")   # red
            lineedit.setToolTip("Invalid URL — must start with http:// or https:// and be a valid host[:port]")
            return False
        
    @staticmethod
    def tr(message, disambiguation="", n=-1) -> str:
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QtCore.QCoreApplication.translate('WidgetValidator', message, disambiguation, n)