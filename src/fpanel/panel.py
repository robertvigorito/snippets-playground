import sys
import typing as _typing
from PySide6 import QtCore, QtGui, QtWidgets
from fpanel import pspecial
from collections import OrderedDict as _OrderedDict


NUKE_SUBMISSION_PANEL_LAYOUT: _typing.Dict[str, _typing.Any] = _OrderedDict()
NUKE_SUBMISSION_PANEL_LAYOUT["farm_selection"] = (pspecial.SimpleQComboBox, {"items": ["race", "local"]})
NUKE_SUBMISSION_PANEL_LAYOUT["range"] = (
    pspecial.ValLineEdit,
    {"validator": QtGui.QRegularExpressionValidator(r"\d+-\d+|[\d ]+"), "placeholder": "e.g. 1001-1150"},
)
NUKE_SUBMISSION_PANEL_LAYOUT["farm_batch_size"] = (
    pspecial.ValLineEdit,
    {"validator": QtGui.QIntValidator(), "placeholder": "e.g. 3"},
)
NUKE_SUBMISSION_PANEL_LAYOUT["max_timeout"] = (
    pspecial.ValLineEdit,
    {"validator": QtGui.QIntValidator(), "placeholder": "e.g. 3"},
)
# Add split line
NUKE_SUBMISSION_PANEL_LAYOUT["split_line"] = (pspecial.HorizontalLine, {})
NUKE_SUBMISSION_PANEL_LAYOUT["cores"] = (
    pspecial.SimpleQComboBox,
    {"items": ["1", "2", "4", "8", "16", "32"], "default": 1},
)
NUKE_SUBMISSION_PANEL_LAYOUT["ram"] = (
    pspecial.SimpleQComboBox,
    {"items": ["1", "2", "4", "8", "16", "32"], "default": 2},
)
# Add split line
NUKE_SUBMISSION_PANEL_LAYOUT["split_line_2"] = (pspecial.HorizontalLine, {})
NUKE_SUBMISSION_PANEL_LAYOUT["notes"] = (pspecial.ClearMultiLineEdit, {"placeholder": "Add any notes here"})
NUKE_SUBMISSION_PANEL_LAYOUT["mail_notification"] = (
    pspecial.ValLineEdit,
    {"placeholder": "", "validator": QtGui.QRegularExpressionValidator(r"\w+@\w+\.\w+")},
)
# Add split line
NUKE_SUBMISSION_PANEL_LAYOUT["split_line_3"] = (pspecial.HorizontalLine, {})
# Add submit layout
# NUKE_SUBMISSION_PANEL_LAYOUT["submit_layout"] = (pspecial.SubmitLayout, {})

CHECKBOX_ACTIONS = (
    ("Farm Each View", False),
    ("Farm Each Node", False),
    ("Enable Render Orders", False),
    ("Use only gpu", False),
    ("Nuke Proxy Mode", False),
    ("Verbose", False),
    ("Start on hold", False),
)


class NukeSubmission(QtWidgets.QWidget):
    """This is a simple window that allows the user to submit a Nuke job to a farm.

    The user can select the farm, range, farm batch size, max timeout, cores, ram, notes, mail notification,
    and other options.

    """

    def __init__(self):
        super().__init__()
        # Default window parameters
        self.setWindowTitle("Nuke Submission")
        self.setGeometry(100, 100, 400, 300)
        # Important attributes
        self.buttons_layout = pspecial.SubmitLayout()
        # Create the layout
        self.build_layout()
        # Add the shortcuts
        QtGui.QShortcut(QtGui.QKeySequence("alt+w"), self, self.close)

        self.buttons_layout.submit.clicked.connect(self.settings)

    def settings(self) -> dict:
        """Return the settings from the submission window.

        Returns:
            dict: The settings from the submission window.
        """

        settings = {}
        for key, (widget, _) in NUKE_SUBMISSION_PANEL_LAYOUT.items():
            widget_instance = self.findChild(widget, name=key.replace("_", "_"))
            if hasattr(widget_instance, "results"):
                settings[key] = widget_instance.results()

        for checkbox_text, _ in CHECKBOX_ACTIONS:
            checkbox = self.findChild(QtWidgets.QCheckBox, checkbox_text.replace(" ", "_"))
            if hasattr(checkbox, "isChecked"):
                settings[checkbox_text] = checkbox.isChecked()

        return settings

    def build_layout(self) -> bool:
        """Build the layout for the submission window using the NUKE_SUBMISSION_PANEL_LAYOUT.

        Returns:
            bool: True if the layout was built successfully, False otherwise.
        """

        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        for key, (widget, kwargs) in NUKE_SUBMISSION_PANEL_LAYOUT.items():
            widget_instance = widget(**kwargs)
            # Set the object name
            widget_instance.setObjectName(key.replace("_", "_"))
            if widget is pspecial.HorizontalLine:
                layout.addRow(widget_instance)
                continue
            layout.addRow(key.replace("_", " ").title(), widget_instance)

        for checkbox_text, checked in CHECKBOX_ACTIONS:
            checkbox = QtWidgets.QCheckBox(checkbox_text)
            # Set the object name
            checkbox.setObjectName(checkbox_text.replace(" ", "_"))
            checkbox.setChecked(checked)
            layout.addRow("", checkbox)

        # Add another horizontal line
        layout.addRow(pspecial.HorizontalLine())
        layout.addRow(self.buttons_layout)
        self.setLayout(layout)

        return True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = NukeSubmission()
    window.show()
    sys.exit(app.exec_())
