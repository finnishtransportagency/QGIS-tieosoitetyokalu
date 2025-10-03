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

from qgis.PyQt import QtCore, QtGui, QtWidgets, uic

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "Settings_dialog.ui"))


class Settings_dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Optional: use a QDialogButtonBox with an Apply button
        # self.apply_btn = self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply)
        # If you already have a custom QPushButton named applyButton, keep it:
        self.apply_btn = self.applyButton

        # Decide which widgets to watch:
        self._watched = self._collect_watched_from_container()

        # Load data (block signals)
        self._load_settings()

        # Snapshot original values
        self._original = {w: self._get_value(w) for w in self._watched}

        # Wire signals per type
        self._connect_change_signals(self._watched)

        self._update_apply_button()
        self.apply_btn.clicked.connect(self._apply)

    # ----- Helpers -----
    
    def _collect_watched_from_container(self) -> list[QtWidgets.QWidget]:
        """Collect all interactive inputs from the entire Settings_dialog.

        Returns:
            result (list[QWidget]): A list of all interactive input widgets found in Settings_dialog.
        """
        watched_types = (
            QtWidgets.QLineEdit, QtWidgets.QCheckBox, QtWidgets.QComboBox,
            QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox, QtWidgets.QDateEdit
        )

        widgets = self.findChildren(QtWidgets.QWidget)  # recursive
        result = []
        for w in widgets:
            # Include only the types we care about
            if not isinstance(w, watched_types):
                continue
            # Skip intentionally excluded widgets: in Designer set dynamic property watch=False
            if w.property("watch") is False:
                continue
            # Skip disabled or read-only inputs
            if not w.isEnabled():
                continue
            if hasattr(w, "isReadOnly") and w.isReadOnly():
                continue
            result.append(w)
        return result


    def _load_settings(self):
        settings = QtCore.QSettings()
        blockers = [QtCore.QSignalBlocker(w) for w in self._watched]
        try:
            self.HTTPAddressLineEdit.setText(settings.value("QGIS-tieosoitetyokalu/http", ""))
            self.HTTPSAddressLineEdit.setText(settings.value("QGIS-tieosoitetyokalu/https", ""))
        finally:
            del blockers

    def _get_value(self, w):
        """Normalize each widget's value for comparison."""
        if isinstance(w, QtWidgets.QLineEdit):
            return w.text().strip()
        if isinstance(w, QtWidgets.QTextEdit):
            return w.toPlainText().strip()
        if isinstance(w, QtWidgets.QPlainTextEdit):
            return w.toPlainText().strip()
        if isinstance(w, QtWidgets.QCheckBox):
            return w.isChecked()
        if isinstance(w, QtWidgets.QComboBox):
            # Prefer text for editable combos, index for fixed lists
            return (w.currentText().strip() if w.isEditable() else w.currentIndex())
        if isinstance(w, QtWidgets.QSpinBox):
            return w.value()
        if isinstance(w, QtWidgets.QDoubleSpinBox):
            return w.value()
        if isinstance(w, QtWidgets.QDateEdit):
            return w.date()
        # Fallback: try "text" property
        return getattr(w, "text", lambda: "")().strip()

    def _connect_change_signals(self, widgets):
        for w in widgets:
            if isinstance(w, QtWidgets.QLineEdit):
                w.setModified(False)
                w.textEdited.connect(self._on_user_change)
                w.editingFinished.connect(self._on_user_change)
                w.textChanged.connect(self._on_user_change)  # re-check validity live
            elif isinstance(w, QtWidgets.QTextEdit) or isinstance(w, QtWidgets.QPlainTextEdit):
                w.textChanged.connect(self._on_user_change)
            elif isinstance(w, QtWidgets.QCheckBox):
                w.toggled.connect(self._on_user_change)
            elif isinstance(w, QtWidgets.QComboBox):
                w.currentIndexChanged.connect(self._on_user_change)
                w.currentTextChanged.connect(self._on_user_change)
            elif isinstance(w, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
                w.valueChanged.connect(self._on_user_change)
            elif isinstance(w, QtWidgets.QDateEdit):
                w.dateChanged.connect(self._on_user_change)
            else:
                # Generic fallback: listen for any changed property if available
                try:
                    w.changed.connect(self._on_user_change)
                except Exception:
                    pass

    def _validate(self) -> bool:
        """Centralize validation; respect validators if present."""
        for w in self._watched:
            if isinstance(w, QtWidgets.QLineEdit):
                v = w.validator()
                if v:
                    state, _, _ = v.validate(w.text(), 0)
                    if state != QtGui.QValidator.Acceptable:
                        return False
                else:
                    if not w.text().strip():
                        return False
        return True

    def _is_dirty(self) -> bool:
        return any(self._get_value(w) != self._original[w] for w in self._watched)

    # ----- Slots -----

    @QtCore.pyqtSlot()
    def _on_user_change(self, *args):
        self._update_apply_button()

    def _update_apply_button(self):
        changed = self._is_dirty()
        valid = self._validate()
        self.apply_btn.setEnabled(changed and valid)
        self.setWindowModified(changed)

    def _apply(self):
        settings = QtCore.QSettings()
        settings.setValue("QGIS-tieosoitetyokalu/http", self.HTTPAddressLineEdit.text().strip())
        settings.setValue("QGIS-tieosoitetyokalu/https", self.HTTPSAddressLineEdit.text().strip())
        settings.sync()

        # Reset the baseline & modified flags
        self._original = {w: self._get_value(w) for w in self._watched}
        for w in self._watched:
            if isinstance(w, QtWidgets.QLineEdit):
                w.setModified(False)
        self._update_apply_button()
