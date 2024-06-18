# pylint: disable=c-extension-no-member,too-few-public-methods
"""This module contains special widgets for the fpanel module.

Instead of using the standard widgets, these special widgets are used to
enhance the appearance of the application and reduce the amount of code.
"""

from typing import Optional as _Optional
from typing import Union as _Union

from PySide6 import QtCore as _QtCore
from PySide6 import QtGui as _QtGui
from PySide6 import QtWidgets as _QtWidgets


class RightAlignedLabel(_QtWidgets.QLabel):
    """A QLabel with right-aligned text."""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setAlignment(_QtCore.Qt.AlignmentFlag.AlignRight | _QtCore.Qt.AlignmentFlag.AlignVCenter)


class HorizontalLine(_QtWidgets.QFrame):
    """A horizontal line."""

    def __init__(self):
        super().__init__()
        self.setFrameShape(_QtWidgets.QFrame.Shape.HLine)
        self.setFrameShadow(_QtWidgets.QFrame.Shadow.Sunken)



class ValLineEdit(_QtWidgets.QLineEdit):
    """A QLineEdit with a validator and placeholder text."""

    def __init__(
        self, text: _Optional[str] = None, validator: _Optional[_QtGui.QValidator] = None, placeholder: str = ""
    ) -> None:
        super().__init__(text)
        if isinstance(validator, _QtGui.QValidator):
            self.setValidator(validator)
        self.setPlaceholderText(placeholder)
        # Add the clear action to the QLineEdit
        self.setClearButtonEnabled(True)

        self.results = self.text



class SubmitLayout(_QtWidgets.QHBoxLayout):
    """A QHBoxLayout for the submit button."""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.submit = _QtWidgets.QPushButton("Submit")
        self.cancel = _QtWidgets.QPushButton("Cancel")
        margins = kwargs.get("margins", (0, 100, 0, 0))
        self.setContentsMargins(*margins)
        self.addWidget(self.submit)
        self.addWidget(self.cancel)


class ClearMultiLineEdit(_QtWidgets.QPlainTextEdit):
    """A QPlainTextEdit with a clear button."""

    def __init__(self, placeholder: str = "") -> None:
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFrameStyle(_QtWidgets.QFrame.Shape.Panel | _QtWidgets.QFrame.Shadow.Sunken)
        self.setVerticalScrollBarPolicy(_QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMaximumHeight(40)

        self.clear_button = _QtWidgets.QPushButton(self)
        self.clear_button.setStyleSheet("border: none; padding: 0;")
        self.clear_button.setVisible(False)
        self.clear_button.move(250, 5)
        # Get the standard icon for the clear button
        clear_icon = self.style().standardIcon(_QtWidgets.QStyle.StandardPixmap.SP_LineEditClearButton)
        self.clear_button.setIcon(clear_icon)
        # Connect the textChanged signal to the has_text method
        self.textChanged.connect(self.has_text)
        self.clear_button.clicked.connect(lambda: self.setPlainText(""))

        self.results = self.toPlainText

    def has_text(self) -> bool:
        """Check if the QPlainTextEdit has text."""
        has_text = bool(self.toPlainText())
        self.clear_button.setVisible(has_text)

        return has_text


class SimpleQComboBox(_QtWidgets.QComboBox):
    """A QComboBox with a simple constructor."""

    def __init__(self, items: _Union[list[str], tuple[str]], default: _Optional[_Union[str, int]] = None) -> None:
        super().__init__()
        self.addItems(items)
        self.setMaximumWidth(self.sizeHint().width())

        if isinstance(default, int):
            self.setCurrentIndex(default)
        elif isinstance(default, str):
            self.setCurrentText(default)
        
        self.results = self.currentText

            
