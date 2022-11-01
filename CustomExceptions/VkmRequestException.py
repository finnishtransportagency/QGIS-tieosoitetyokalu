from qgis.PyQt.QtCore import QCoreApplication


class VkmRequestException(Exception):
    def __init__(self, message):
        self.message = message
        self.error_message = self.tr(u'VKM-API virhe: ')

        
    def __str__(self):
        return f'{self.error_message}{self.message}'

    
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
        return QCoreApplication.translate('VkmRequestException', message, disambiguation, n)
