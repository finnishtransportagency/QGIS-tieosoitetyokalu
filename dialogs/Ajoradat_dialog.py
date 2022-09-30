import os

from PyQt5.QtWidgets import QFileDialog
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

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
        filename,_ = QFileDialog.getSaveFileName(self, 'Valitse tallennussijainti', "", 'csv (*.csv)', options=options)
        if filename:
            self.PathlineEdit.setText(filename)


    def get_file_path(self):
        """Returns the path of the file once the Download button is pressed.

        Returns:
            (str): File path.
        """
        return self.PathlineEdit.text()