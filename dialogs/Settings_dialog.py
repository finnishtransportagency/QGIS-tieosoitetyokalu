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
from ..libs.process_widgets import WidgetValidator
from ..CustomExceptions.InvalidSettingsException import InvalidSettingsException

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "Settings_dialog.ui"))


class Settings_dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(410, 160)

        self._settings_group = "QGIS-tieosoitetyokalu"

        self.wv = WidgetValidator()
    
        # Decide which widgets to watch:
        self._watched = self._collect_watched_from_dialog()

        # Load persisted values without triggering dirty state
        self._load_settings()

        # Optional: use a QDialogButtonBox with an Apply button
        # self.apply_btn = self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply)
        # If you already have a custom QPushButton named applyButton, keep it:
        self.apply_btn = self.applyButton

        # Snapshot original values for change tracking
        self._original = {w: self._get_value(w) for w in self._watched}

        # Connect change signals per widget type
        self._connect_change_signals(self._watched)

        # Make sure Apply-button starts in the right state
        self._update_apply_button()

        # Wire Save/Apply
        self.apply_btn.clicked.connect(self._apply)

    # ----- Helpers -----
    
    def _settings_key_for(self, w: QtWidgets.QWidget) -> str:
        """Return full relative key path inside ROOT_GROUP, e.g., 'proxy/http'."""
        # subgroup may come from widget, or inherit from a parent container
        subgroup = self._settings_group_for_widget(w)  # e.g., 'proxy' or ''
        assert subgroup is not None # Widgets have to belong to a group
        key = w.property("settingsKey")
        assert key is not None # A setting key has to be configured for a watched interactive widget
        if not key:
            key = w.objectName()
        return f"{subgroup}/{key}" if subgroup else key

    def _settings_group_for_widget(self, w: QtWidgets.QWidget) -> str:
        """Resolve subgroup by walking up the parent chain for 'settingsGroup'."""
        cur = w
        while cur is not None:
            val = cur.property("settingsGroup")
            if isinstance(val, str) and val.strip():
                return val.strip()
            cur = cur.parent()
        # Fallback to a dialog-level default if you like (e.g., 'proxy')
        return getattr(self, "_default_subgroup", None)

    def _collect_watched_from_dialog(self) -> list[QtWidgets.QWidget]:
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
        """Load all possible saved settings.
        """
        s = QtCore.QSettings()
        s.beginGroup(self._settings_group)  # ROOT_GROUP
        blockers = [QtCore.QSignalBlocker(w) for w in self._watched]
        try:
            for w in self._watched:
                path = self._settings_key_for(w)  # e.g., 'proxy/http'
                default = self._get_value(w)
                # choose type-safe value by widget type
                val = self._typed_read(s, w, path, default)
                self._set_value(w, val)
        finally:
            s.endGroup()
            del blockers

    def _save_settings(self):
        """Save modified settings to QSettings.
        """
        s = QtCore.QSettings()
        s.beginGroup(self._settings_group)  # ROOT_GROUP
        try:
            for w in self._watched:
                path = self._settings_key_for(w)  # e.g., 'proxy/http'
                s.setValue(path, self._get_value(w))
        finally:
            s.endGroup()
            s.sync()

    def _typed_read(self, s: QtCore.QSettings, w: QtWidgets.QWidget, key: str, default=None):
        """
        Read a value from QSettings using a type appropriate for the widget 'w'.
        Returns a Python value or a Qt type (e.g., QDate) that your _set_value() can consume.
        """
        # QLineEdit / text edits: strings
        if isinstance(w, QtWidgets.QLineEdit):
            return s.value(key, default if default is not None else "", type=str)

        if isinstance(w, QtWidgets.QPlainTextEdit) or isinstance(w, QtWidgets.QTextEdit):
            return s.value(key, default if default is not None else "", type=str)

        # CheckBox: bool
        if isinstance(w, QtWidgets.QCheckBox):
            return s.value(key, bool(default) if default is not None else False, type=bool)

        # ComboBox: decide what to store/read
        # - default behavior:
        #     * editable: store/read text (str)
        #     * non-editable: store/read index (int)
        # - optional override via dynamic property 'settingsComboMode' in Designer/programmatically:
        #     * 'text' | 'index'
        if isinstance(w, QtWidgets.QComboBox):
            mode = w.property("settingsComboMode")
            if isinstance(mode, str):
                mode = mode.strip().lower()
            if mode == "text" or (mode is None and w.isEditable()):
                return s.value(key, default if isinstance(default, str) else "", type=str)
            # index mode
            try:
                dflt_idx = int(default) if default is not None else 0
            except Exception:
                dflt_idx = 0
            return s.value(key, dflt_idx, type=int)

        # Spin boxes: int/float
        if isinstance(w, QtWidgets.QSpinBox):
            try:
                dflt = int(default) if default is not None else w.minimum()
            except Exception:
                dflt = w.minimum()
            val = s.value(key, dflt, type=int)
            # Clamp into widget range to avoid invalid values
            return max(w.minimum(), min(w.maximum(), int(val)))

        if isinstance(w, QtWidgets.QDoubleSpinBox):
            try:
                dflt = float(default) if default is not None else w.minimum()
            except Exception:
                dflt = w.minimum()
            val = s.value(key, dflt, type=float)
            return max(w.minimum(), min(w.maximum(), float(val)))

        # DateEdit: read ISO string and return QDate
        if isinstance(w, QtWidgets.QDateEdit):
            iso = s.value(key, default if default is not None else "", type=str)
            if isinstance(iso, QtCore.QDate):
                d = iso
            else:
                d = QtCore.QDate.fromString(str(iso), "yyyy-MM-dd")
            if not d.isValid():
                d = QtCore.QDate.currentDate()
            return d

        # (Optional) support for QTimeEdit/QDateTimeEdit if you add them later
        # if isinstance(w, QtWidgets.QTimeEdit):
        #     hhmmss = s.value(key, default if default is not None else "", type=str)
        #     t = QtCore.QTime.fromString(str(hhmmss), "HH:mm:ss")
        #     return t if t.isValid() else QtCore.QTime.currentTime()
        # if isinstance(w, QtWidgets.QDateTimeEdit):
        #     iso = s.value(key, default if default is not None else "", type=str)
        #     dt = QtCore.QDateTime.fromString(str(iso), QtCore.Qt.ISODate)
        #     return dt if dt.isValid() else QtCore.QDateTime.currentDateTime()

        # Fallback: return as-is (most often a string)
        return s.value(key, default)

    def _get_value(self, w: QtWidgets.QWidget):
        """Read normalized value from a widget for saving and dirty-compare."""
        if isinstance(w, QtWidgets.QLineEdit):
            return w.text().strip()
        if isinstance(w, QtWidgets.QCheckBox):
            return bool(w.isChecked())
        if isinstance(w, QtWidgets.QComboBox):
            # Convention: store text for editable combos, index for fixed lists
            return w.currentText().strip() if w.isEditable() else int(w.currentIndex())
        if isinstance(w, QtWidgets.QSpinBox):
            return int(w.value())
        if isinstance(w, QtWidgets.QDoubleSpinBox):
            return float(w.value())
        if isinstance(w, QtWidgets.QDateEdit):
            # Persist as ISO string; avoids QVariant date portability quirks
            return w.date().toString("yyyy-MM-dd")
        # Fallback: try "text" property if any
        text = getattr(w, "text", lambda: "")()
        return text.strip() if isinstance(text, str) else text
    
    
    def _set_value(self, w: QtWidgets.QWidget, value):
        """Set a value into a widget, handling types safely."""
        if isinstance(w, QtWidgets.QLineEdit):
            w.setText("" if value is None else str(value))
            return
        if isinstance(w, QtWidgets.QCheckBox):
            w.setChecked(bool(value))
            return
        if isinstance(w, QtWidgets.QComboBox):
            if w.isEditable():
                w.setEditText("" if value is None else str(value))
            else:
                # Expecting an index; clamp to valid range
                try:
                    idx = int(value)
                except Exception:
                    idx = -1
                if 0 <= idx < w.count():
                    w.setCurrentIndex(idx)
            return
        if isinstance(w, QtWidgets.QSpinBox):
            try:
                w.setValue(int(value))
            except Exception:
                pass
            return
        if isinstance(w, QtWidgets.QDoubleSpinBox):
            try:
                w.setValue(float(value))
            except Exception:
                pass
            return
        if isinstance(w, QtWidgets.QDateEdit):
            if isinstance(value, QtCore.QDate):
                d = value
            else:
                # Accept ISO string
                d = QtCore.QDate.fromString(str(value), "yyyy-MM-dd")
            if not d.isValid():
                d = QtCore.QDate.currentDate()
            w.setDate(d)
            return
        # Fallback: try text() setter if available
        setter = getattr(w, "setText", None)
        if callable(setter):
            setter("" if value is None else str(value))


    def _connect_change_signals(self, widgets: list[QtWidgets.QWidget]):
        """Track changes of interactive widgets.

        Args:
            widgets (list[QtWidgets.QWidget]): List of widgets that need watching.
        """
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

    # TODO: POISTA
    def _validate(self) -> bool:
        """Centralize validation; respect validators if present."""
        # NOTE: this currently requires all interactive widgets to have valid values
        # TODO: user needs to be able to save modified settings even if some forms are empty or invalid

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
    
    # TODO: POISTA
    # def _get_dirty_widgets(self) -> list:
    #     return [self._get_value(w) for w in self._watched if self._get_value(w) != self._original[w]]

    # ----- Slots -----

    @QtCore.pyqtSlot()
    def _on_user_change(self, *args):
        """Connect interactive widget change and the correct button/action.
        """
        self._update_apply_button()

    def _update_apply_button(self):
        """Enable/disable "Apply" button depending on changes made to watched widgets.
        """
        changed = self._is_dirty()
        self.apply_btn.setEnabled(changed)
        self.setWindowModified(changed)

    def _apply(self):
        """Save dialog settings and reset the baseline for tracking interactive widgets. Update "Apply" button state.
        """
        
        invalid_groups = self.wv.validate_widgets(widgets=self._watched)
        if invalid_groups:
            raise InvalidSettingsException(invalid_groups)
        
        self._save_settings()

        # Reset baseline for dirty tracking
        self._original = {w: self._get_value(w) for w in self._watched}
        for w in self._watched:
            if isinstance(w, QtWidgets.QLineEdit):
                w.setModified(False)
        self._update_apply_button()
