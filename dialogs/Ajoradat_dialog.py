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


import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QFileDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Ajoradat_dialog.ui'))


class Ajoradat_dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(Ajoradat_dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setFixedSize(811, 340)

        self.PathlineEdit.textChanged.connect(self.enable_download)
        self.enable_download()
        self.PathlineEdit.clear()
        self.pushButton_Path.clicked.connect(self.select_output_file)


    def enable_download(self):
        if self.PathlineEdit.text() or self.PathlineEdit.text() != "":
            self.pushButton_Download.setEnabled(True)
        else:
            self.pushButton_Download.setEnabled(False)


    def select_output_file(self):
        """User chooses location for the downloadable CSV-file."""
        options = QFileDialog.Options()
        filename,_ = QFileDialog.getSaveFileName(self, self.tr(u'Valitse tallennussijainti'), "", 'csv (*.csv)', options=options)
        if filename:
            self.PathlineEdit.setText(filename)


    def get_file_path(self):
        """Returns the path of the file once the Download button is pressed.

        Returns:
            (str): File path.
        """
        return self.PathlineEdit.text()


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
        return QCoreApplication.translate('Ajoradat_dialog', message, disambiguation, n)
