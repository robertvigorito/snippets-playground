# pylint: disable=c-extension-no-member,too-few-public-methods
"""This module contains special widgets for the nuke_submission.gui module.

Instead of using the standard widgets, these special widgets are used to
enhance the appearance of the application and reduce the amount of code.
"""
from math import ceil as _ceil
import os as _os
import functools as _functools
import typing as _typing
from typing import Optional as _Optional
from typing import Union as _Union


from PySide2 import QtCore as _QtCore
from PySide2 import QtGui as _QtGui
from PySide2 import QtWidgets as _QtWidgets
from fpanel import facade


class RightAlignedLabel(_QtWidgets.QLabel):
    """A QLabel with right-aligned text."""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setAlignment(_QtCore.Qt.AlignmentFlag.AlignRight | _QtCore.Qt.AlignmentFlag.AlignVCenter)  # type: ignore


class HorizontalLine(_QtWidgets.QFrame):
    """A horizontal line."""

    def __init__(self):
        super().__init__()
        self.setFrameShape(_QtWidgets.QFrame.Shape.HLine)
        self.setFrameShadow(_QtWidgets.QFrame.Shadow.Sunken)


class ValLineEdit(_QtWidgets.QLineEdit):
    """A QLineEdit with a validator and placeholder text."""

    def __init__(
        self,
        text: _Optional[str] = None,
        validator: _Optional[_QtGui.QValidator] = None,
        placeholder: str = "",
        **kwargs,
    ) -> None:
        super().__init__(text)
        if isinstance(validator, _QtGui.QValidator):
            self.setValidator(validator)
        self.setPlaceholderText(placeholder)
        # Add the clear action to the QLineEdit
        self.setClearButtonEnabled(True)
        width = kwargs.get("width")
        if width:
            self.setMaximumWidth(width)

        self.results = self.text
        self.set = self.setText

        # Update the number if the wheel event is detected

    def wheelEvent(self, event: _QtGui.QWheelEvent) -> None:
        """Update the number if the wheel event is detected.

        Args:
            event (QWheelEvent): The wheel event.
        """
        if not self.text().isdigit():
            return
        if event.angleDelta().y() > 0:
            self.setText(str(int(self.text()) + 1))
        elif int(self.results()) > 1:
            self.setText(str(int(self.text()) - 1))


class FrameRangeLineEdit(ValLineEdit):
    """A QLineEdit for the frame range."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        layout = _QtWidgets.QHBoxLayout()
        # Set the alignment to right and center
        layout.setAlignment(_QtCore.Qt.AlignmentFlag.AlignRight | _QtCore.Qt.AlignmentFlag.AlignVCenter)  # type: ignore
        # Offset the menu to compensate the clear icon
        layout.setContentsMargins(0, 0, 19, 0)
        # Create a toolbar
        toolbar = _QtWidgets.QToolBar()
        # Make icons flat
        toolbar.setToolButtonStyle(_QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        # Set the icon size
        toolbar.setIconSize(_QtCore.QSize(16, 16))
        toolbar.setStyleSheet("QToolButton {border: none;} QToolButton:pressed {background: none;}}")

        first_mid_last = toolbar.addAction(_QtGui.QIcon(icon_path("fml")), "Set first middle last.")
        shotgrid = toolbar.addAction(_QtGui.QIcon(icon_path("shotgrid")), "Update frame range from shotgrid.")
        root_range = toolbar.addAction(_QtGui.QIcon(icon_path("range")), "Update frame range from nuke root settings.")

        # Connections
        first_mid_last.triggered.connect(lambda: self.setText(facade.FrameRange.first_middle_last_string()))
        root_range.triggered.connect(lambda: self.setText(facade.FrameRange.root()))

        layout.addWidget(toolbar)
        self.setLayout(layout)


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
        self.setFrameStyle(_QtWidgets.QFrame.Shape.Panel | _QtWidgets.QFrame.Shadow.Sunken)  # type: ignore
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
        self.set = self.setPlainText

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
        self.set = self.setCurrentText


def icon_path(icon_name: str) -> str:
    """Return the path to the icon.

    Args:
        icon_name (str): The name of the icon.

    Returns:
        str: The path to the icon.
    """
    return f"{_os.path.dirname(__file__)}/icons/{icon_name}.png"


class TreeToolbar(_QtWidgets.QVBoxLayout):
    """A QLayout for the tree toolbar."""

    def __init__(self) -> None:
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(_QtCore.Qt.AlignmentFlag.AlignTop | _QtCore.Qt.AlignmentFlag.AlignRight)  # type: ignore

        # Create a mini toolbar, expand all, collapse all, and hide the header, refresh
        self._toolbar = _QtWidgets.QToolBar()
        self._toolbar.setIconSize(_QtCore.QSize(16, 16))
        self._toolbar.setToolButtonStyle(_QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._toolbar.setStyleSheet("* {margin: 0; padding: 0; } ")

        self.refresh = self._toolbar.addAction(_QtGui.QIcon(icon_path("refresh_colored")), "Refresh")
        self.expand = self._toolbar.addAction(_QtGui.QIcon(icon_path("expand_colored")), "Expand")
        self.goto = self._toolbar.addAction(_QtGui.QIcon(icon_path("goto_colored")), "Goto")

        # Set the action connection
        self.addWidget(self._toolbar)
        self._toolbar.setVisible(False)

    def toggle(self, on: bool = True) -> bool:  # pylint: disable=invalid-name
        """Toggle the visibility of the toolbar.

        Args:
            on (bool): The visibility of the toolbar. Defaults to True.

        Returns:
            bool: True if the toolbar is visible, False otherwise.
        """
        self._toolbar.setVisible(on or not self._toolbar.isVisible())
        return self._toolbar.isVisible()


def show_wait_cursor(func: _typing.Callable) -> _typing.Callable:
    """A decorator that shows the wait cursor during the execution of the function.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """

    @_functools.wraps(func)
    def wrapper(*args, **kwargs):
        _QtWidgets.QApplication.restoreOverrideCursor()

        try:
            _QtWidgets.QApplication.setOverrideCursor(_QtGui.QCursor(_QtCore.Qt.CursorShape.WaitCursor))
            result = func(*args, **kwargs)
        finally:
            _QtWidgets.QApplication.restoreOverrideCursor()

        return result

    return wrapper


class FancyMessageBox(_QtWidgets.QMessageBox):
    """A QMessageBox with a fancy icon."""

    COUNTDOWN = 10

    def __init__(self, ids: _typing.List[str], **kwargs) -> None:
        super().__init__(**kwargs)
        self.setWindowFlags(_QtCore.Qt.WindowType.FramelessWindowHint)  # type: ignore[arg-type]
        self.setStyleSheet(
            """
            QMessageBox {
                border: 2px solid rgb(230, 150, 17);
            }
            """
        )
        # Restore the mouse cursor
        _QtWidgets.QApplication.restoreOverrideCursor()
        # Add the custom icon
        support_icon = _QtGui.QPixmap(icon_path("support"))
        support_icon = support_icon.scaledToWidth(100)
        self.setIconPixmap(support_icon)
        # Add the auto-close timer and ok button
        self.ok_button = self.addButton(self.Ok)
        self.ok_button.setText(f"OK ({self.COUNTDOWN})")
        self.ok_button.clicked.connect(self.close)
        self.timer = _QtCore.QTimer()
        self.timer.setInterval(self.COUNTDOWN * 1000)
        self.timer.timeout.connect(self.close)
        self.timer.start()
        self.update_timer = _QtCore.QTimer()
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.update_button_text)
        self.update_timer.start()

        # Add a custom label that has a custom linkable command.
        self.setText("Submission was successful!")
        self.label = _QtWidgets.QLabel()
        self.label.setText(
            f"The jobs <a href='#'>{' '.join(ids)}</a> was submitted successfully, click the link to open race."
        )
        self.label.setOpenExternalLinks(False)
        self.label.linkActivated.connect(lambda: print("Link clicked"))

        # Add the label to the layout
        self.layout().addWidget(self.label, 1, 2, alignment=_QtCore.Qt.AlignTop)  # type: ignore

    def resizeEvent(self, event: _QtGui.QResizeEvent) -> None:  # pylint: disable=unused-argument,invalid-name
        """Resize the QMessageBox.

        Args:
            event (QResizeEvent): The resize event.
        """
        self.setMinimumWidth(450)

    def update_button_text(self) -> None:
        """Update the text of the OK button."""
        remaining_time = self.timer.remainingTime() / 1000
        remaining_time = _ceil(remaining_time)
        self.ok_button.setText(f"OK ({remaining_time})")


class PSettings(_QtCore.QSettings):
    """A QSettings object that saves the settings to the QSettings object."""

    IGNORE_KEYS = ("frame_depencency", "job_depencency", "range")

    def __init__(self) -> None:

        super().__init__("DD", "NukeSubmission")
        # Ignore some keys that are not needed
        self.setFallbacksEnabled(False)

    def save(self, settings: dict) -> bool:
        """Save the settings to the QSettings object.

        Args:
            settings (dict): The settings to save.

        Returns:
            bool: True if the settings were saved successfully, False otherwise.
        """
        for key, value in settings.items():
            if key in self.IGNORE_KEYS:
                continue
            self.setValue(key, value)

        # Make sure the settings are saved
        self.sync()

        return True

    def get(self, key: str) -> _typing.Optional[_typing.Union[str, bool]]:
        """Get the value of the key.

        Args:
            key (str): The key to get the value from.

        Returns:
            Optional[Union[str, bool]]: The value of the key.
        """
        # If the value is true or false, return a boolean
        if key in self.IGNORE_KEYS:
            return None
        value: str = self.value(key)  # type: ignore
        if value in ["true", "false"]:
            return value == "true"

        return value
