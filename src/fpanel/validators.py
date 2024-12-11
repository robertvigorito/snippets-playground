from PySide2 import QtWidgets as _QtWidgets
from PySide2 import QtGui as _QtGui
from PySide2 import QtCore as _QtCore

from fpanel import pspecial as _pspecial


from validate import vuke as _vuke


def script_information() -> "_QtWidgets.QWidget()":
    """Create a widget that displays the script information.

    Returns:
        _QtWidgets.QWidget(): The widget that displays the script information.
    """
    node_count = 10
    warnings = 2
    ram_usage = "2.5 GB"
    created = "2021-09-01 12:00:00"
    modified = "2021-09-01 12:00:00"

    widget = _QtWidgets.QWidget()
    form_layout = _QtWidgets.QFormLayout()
    form_layout.setContentsMargins(0, 0, 0, 0)
    form_layout.setLabelAlignment(_QtCore.Qt.AlignRight)
    form_layout.addRow("Node Count", _QtWidgets.QLabel(str(node_count)))
    form_layout.addRow("Warnings", _QtWidgets.QLabel(str(warnings)))
    form_layout.addRow("Ram Usage", _QtWidgets.QLabel(str(ram_usage)))
    form_layout.addRow("Created", _QtWidgets.QLabel(str(created)))
    form_layout.addRow("Modified", _QtWidgets.QLabel(str(modified)))
    widget.setLayout(form_layout)

    return widget


class Validator(_QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.move(4250, 200)

        # Add a toolbar
        toolbar = _QtWidgets.QToolBar()
        toolbar.setStyleSheet("QToolBar {background-color: gray; color: white}")
        action_one = toolbar.addAction("Action One")

        self.setLayout(_QtWidgets.QGridLayout())
        self.layout().setHorizontalSpacing(10)
        row = 0
        for validator in _vuke.process():
            # Icon, prompt, link, if Fixable, fix
            if validator.status == _vuke.Status.UNKNOWN:
                continue
            validator_split_line = _pspecial.HorizontalLine(text=validator.name)
            status_label = _pspecial.IconLabel(validator.status.value, validator.status.name)
            prompt_label = _QtWidgets.QLabel(validator.prompt)

            if validator.fixable:
                fix_button = _QtWidgets.QPushButton("Fix")
                fix_button.clicked.connect(validator.fix)

            self.layout().addWidget(validator_split_line, row, 0, 1, 2)  # type: ignore
            self.layout().addWidget(status_label, row + 1, 0, alignment=_QtCore.Qt.AlignRight | _QtCore.Qt.AlignTop)  # type: ignore
            self.layout().addWidget(prompt_label, row + 1, 1)
            if validator.fixable:
                self.layout().addWidget(fix_button, row + 1, 2)
            row += 2
            # if validator.fixable:
            # self.layout().addWidget(fix_button)

        # Add Shortcut to close
        close_shortcut = _QtWidgets.QShortcut(_QtGui.QKeySequence("alt+w"), self).activated.connect(self.close)

        # Add script information on the bottom

        # self.layout().addWidget(horizontal_line, )  # type: ignore
        self.layout().addWidget(_pspecial.HorizontalLine("Script Information"), row + 1, 0, 1, 2)  # type: ignore
        self.layout().addWidget(script_information(), row + 2, 1, 1, 2)  # type: ignore
        self.layout().setAlignment(_QtCore.Qt.AlignTop)


if __name__ == "__main__":
    import sys

    app = _QtWidgets.QApplication(sys.argv)
    window = Validator()
    window.show()

    sys.exit(app.exec_())
