from qgis.PyQt.QtCore import QCoreApplication


class VkmApiException(Exception):
    def __init__(self, url):
        self.message = self.tr(u'VKM-rajapintaan ei saada yhteyttä.')
        self.url = url


    def __str__(self):
        return f'{self.message} VKM-URL: {self.url}'


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
        return QCoreApplication.translate('VkmApiException', message, disambiguation, n)
