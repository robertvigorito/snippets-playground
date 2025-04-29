from contextlib import contextmanager
from PySide2 import QtCore as _QtCore
from PySide2 import QtGui as _QtGui
from PySide2 import QtWidgets as _QtWidgets

@contextmanager
def block_signals(widget):
    widget.blockSignals(True)
    yield
    widget.blockSignals(False)


class TagLabel(_QtWidgets.QPushButton):  # pylint: disable=too-few-public-methods
    """The custom tag label widget."""

    STYLE_SHEET = """
        QPushButton:hover { background-color: rgb(230, 130, 10); } 
        QPushButton {border-radius: 4px; background-color: rgb(170, 100, 5); border: 0px; padding: 0px; margin: 0px; font-weight: none; font-size: 12px; color: white;}
    """

    def __init__(self, text: str = "", parent=None, **kwargs) -> None:
        """

        Args:
            text (str, optional): The text to display on the label. Defaults to "".
            parent ([type], optional): The parent widget. Defaults to None.

        Keyword Args:
            content_margins (tuple): The content margins for the label, defaults to (10, 0, 10, 0).
            height (int): The height of the label, defaults to 20.
            width (int): The width of the label, defaults to 50.
        """
        super().__init__(text, parent)

        # Extract the keyword arguments
        content_margins = kwargs.get("content_margins", (0, 0, 0, 0))

        # Set the default values
        padding = kwargs.get("padding", 20)
        self.setFixedHeight(kwargs.get("height", 20))
        # Set the width to wrap the text
        self.setFixedWidth(self.fontMetrics().width(text) + padding)
        self.setContentsMargins(*content_margins)
        self.setStyleSheet(self.STYLE_SHEET)


class HorizontalLine(_QtWidgets.QFrame):  # pylint: disable=too-few-public-methods
    """The horizontal line widget."""

    def __init__(self, parent=None) -> None:
        """The initiation method.

        Args:
            parent ([type], optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setFrameShape(_QtWidgets.QFrame.HLine)
        self.setFrameShadow(_QtWidgets.QFrame.Sunken)


class LineEditValidator(_QtWidgets.QLineEdit):  # pylint: disable=too-few-public-methods
    """The line edit with a validator."""

    VALIDATOR_PATTERN = r"[a-zA-Z]+[a-zA-Z0-9_]+"

    def __init__(self, parent=None, text="", validator=None) -> None:
        """The initiation method.

        Args:
            parent ([type], optional): The parent widget. Defaults to None.
            text (str, optional): The text to display on the line edit. Defaults to "".
        """
        super().__init__(parent)
        self.setText(str(text))
        self.setValidator(_QtGui.QRegExpValidator(validator or self.VALIDATOR_PATTERN))  # type: ignore
        self.setClearButtonEnabled(True)


class LineEditWithCompleter(LineEditValidator):
    """The line edit supports an inline completer and a popup completer.

    Unfortunately, the default completer can only support one and this class provides both options.
    """

    def __init__(self, parent=None, text="", items=None, validator=None, force_case_sensitive=True) -> None:
        """The initiation method.

        Args:
            parent ([type], optional): The parent widget. Defaults to None.
            text (str, optional): The text to display on the line edit. Defaults to "".
            items ([type], optional): The items to display in the completer. Defaults to None.
        """
        super().__init__(parent)
        self.complete_items = items or []
        # Needs to be the first line or the overwritten setText will not work
        self.setText(str(text))
        self.setCompleter(_QtWidgets.QCompleter())
        self.completer().setModel(_QtCore.QStringListModel(self.complete_items))
        self.setValidator(_QtGui.QRegExpValidator(validator or self.VALIDATOR_PATTERN))  # type: ignore
        if force_case_sensitive:
            self.textEdited.connect(self.force_case_sensitivity)
        self.textEdited.connect(self._inline_auto_complete)

    def force_case_sensitivity(self) -> bool:
        """Force the case sensitivity when the user types.

        Returns:
            bool: True if the case sensitivity has been forced, False otherwise.
        """
        last_input = self.text()[-1]
        user_existing_input = self.text()[:-1]
        for potential_match in self.complete_items:
            if potential_match.startswith(user_existing_input + last_input.upper()):
                self.setText(user_existing_input + last_input.upper())
                break
            if potential_match.startswith(user_existing_input + last_input.lower()):
                self.setText(user_existing_input + last_input.lower())
                break
        else:
            return False
        return True

    def _inline_auto_complete(self):
        """The method to auto complete the text inline.

        Returns:
            bool: True if the text has been auto completed, False otherwise.
        """
        # Set the completion prefix
        self.completer().setCompletionPrefix(self.text())
        # Get the closest match from the completion model
        completion_model = self.completer().completionModel()
        if completion_model.rowCount() < 0 or self.text().isdigit():
            return False

        closest_match = completion_model.index(0, 0).data()
        # Display hint text inline by showing the rest of the closest match in a subtle way
        typed_text = self.text()
        if closest_match and closest_match.startswith(typed_text):
            hint_text = closest_match[len(typed_text) :]  # Get only the hint part of the completion
            self.setText(typed_text + hint_text)
            # Select the hint part to indicate it's a suggestion
            self.setSelection(len(typed_text), len(hint_text))

        return True

    def keyPressEvent(self, event) -> None:  # pylint: disable=invalid-name
        """The key press event handler - Show the popup completer.

        Args:
            event (QKeyEvent): The key event.
        """
        if event.key() in [_QtCore.Qt.Key_Backspace] and self.text():
            self.blockSignals(True)
            # Remove the selected text
            self.setText(self.text().replace(self.selectedText(), ""))
            super().keyPressEvent(event)
            self.blockSignals(False)
            return None
        if event.key() == _QtCore.Qt.Key_Right and self.text():
            if self._inline_auto_complete():
                return None

        if self.completer() and not self.completer().popup().isVisible() and event.key() != _QtCore.Qt.Key_Enter:
            self.completer().setCompletionPrefix(self.text())
            self.completer().complete()
            # If there are suggestions, show the popup
            if self.completer().completionCount():
                self.completer().popup().show()
        if event.key() in [_QtCore.Qt.Key_Up, _QtCore.Qt.Key_Down] and self.text().isdigit():
            value = 1 if event.key() == _QtCore.Qt.Key_Up else -1
            self.setText(str(int(self.text()) + value))

        return super().keyPressEvent(event)

    def items_only(self, pattern: str = "") -> bool:
        """The input provide will only match to the completion items.

        Args:
            pattern (str): The pattern to apply to the validator.

        Returns:
            bool: True if the validation has been set.
        """
        pattern = "|".join(self.complete_items) + pattern
        # Define a case-sensitive regex pattern
        regex = _QtCore.QRegExp(pattern)
        regex.setCaseSensitivity(_QtCore.Qt.CaseInsensitive)  # Ensure case sensitivity

        self.setValidator(_QtGui.QRegExpValidator(regex))  # type: ignore

        return True


class TagLineEdit(LineEditWithCompleter):
    """The line edit that supports adding tags."""

    TAG_PADDING = 1
    TEXT_PADDING = 5
    LIMIT: int = 1

    def __init__(self, parent=None, items=None, text="") -> None:
        """The initiation method.

        Args:
            parent ([type], optional): The parent widget. Defaults to None.
            items ([type], optional): The items to display in the completer. Defaults to None.
        """
        super().__init__(parent, items=items, force_case_sensitive=False)
        self.tags: "list[TagLabel]" = []
        layout = _QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 0, 0)
        layout.setAlignment(_QtCore.Qt.AlignLeft)
        layout.setSpacing(self.TAG_PADDING)

        self.setClearButtonEnabled(True)
        self.setMinimumHeight(26)
        # Add the tag label to the layout

        self.items_only(r"|(\d+)")
        self.editingFinished.connect(lambda: self.add_tag(self.text()))
        self.set_text(text)

    def keyPressEvent(self, event) -> None:
        """The key press event handler.

        Args:
            event (QKeyEvent): The key event.
        """
        if event.key() == _QtCore.Qt.Key_Backspace and self.tags and not self.text():
            with block_signals(self):
                self.remove_last_tag()

        return super().keyPressEvent(event)

    def add_tag(self, text: str):
        """Add a tag to the line edit.

        Args:
            text (str): The text to add as a tag.
        """
        if self.LIMIT and len(self.tags) >= self.LIMIT:
            self.clear()
            return False
        if text not in self.complete_items or text in self.tag_names():
            return False
        self.clear()
        tag_label = TagLabel(text)
        self.layout().addWidget(tag_label)
        self.tags.append(tag_label)
        self.setTextMargins(self.tags_width(), 0, 0, 0)

        return True

    def remove_last_tag(self):
        """Remove the last tag from the line edit."""
        if not self.tags:
            return False
        if self.text().strip():
            return False
        # Adjust the text margins
        self.tags.pop().deleteLater()
        self.setTextMargins(self.tags_width(), 0, 0, 0)
        return True

    def tag_names(self) -> "tuple[str, ...]":
        """Get the tag names from the tags.

        Returns:
            tuple[str]: The tag names.
        """
        return tuple(str(tag.text()) for tag in self.tags)

    def tags_width(self) -> int:
        """Get the total width of the tags.

        Returns:
            int: The total width of the tags.
        """
        return sum(tag.width() + self.TAG_PADDING for tag in self.tags)

    def get_text(self) -> str:
        """Get the text from the line edit or the last tag.

        Returns:
            str: Text from the existing edit or the last tag.
        """
        if self.tags:
            return self.tags[-1].text()
        return super().text()
        

    def set_text(self, text: str) -> None:
        """Set the text to the line edit or the last tag.

        Args:
            text (str): The text to set.
        """
        self.blockSignals(True)
        if text in self.complete_items:
            self.add_tag(text)
            return None

        super().setText(str(text))
        self.blockSignals(False)
        return None


class DropDownTagger(_QtWidgets.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.form_layout = _QtWidgets.QFormLayout()
        self.setLayout(self.form_layout)

        tag = TagLineEdit(items=["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "Honeydew"])
        tag.LIMIT = 1
        self.form_layout.addRow("Labels", tag)
        self.delete_me()

    def delete_me(self):
        self.setGeometry(0, 0, 300, 200)
        screen = _QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        window_size = self.size()
        x = (screen_size.width() - window_size.width()) / 2
        y = (screen_size.height() - window_size.height()) / 2 - 300
        self.move(x, y)

        close_shortcut = _QtWidgets.QShortcut(_QtGui.QKeySequence("alt+w"), self)
        close_shortcut.activated.connect(self.close)


if __name__ == "__main__":
    import sys

    app = _QtWidgets.QApplication(sys.argv)
    window = DropDownTagger()
    window.show()
    sys.exit(app.exec_())
