"""The panel module contains the submission panel for Nuke.
"""
import typing as _typing

from PySide2 import QtGui, QtWidgets
from collections import OrderedDict as _OrderedDict

from fpanel import pspecial
from fpanel.ptree import NodeTreeView


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


class Panel(QtWidgets.QDialog):
    """This is a simple window that allows the user to submit a Nuke job to a farm.

    The user can select the farm, range, farm batch size, max timeout, cores, ram, notes, mail notification,
    and other options.

    """

    def __init__(self):
        super().__init__(QtWidgets.QApplication.activeWindow())
        # Default window parameters
        self.setWindowTitle("Nuke")
        # self.setGeometry(100, 100, 400, 300)
        # Important attributes
        self.buttons_layout = pspecial.SubmitLayout()
        self.node_tree_view = NodeTreeView()
        # Create the layout
        self.build_layout()
        # Add the shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence("alt+w"), self, self.close)

        self.buttons_layout.submit.clicked.connect(self.settings)
        self.buttons_layout.cancel.clicked.connect(self.close)

    def settings(self) -> dict:
        """Return the settings from the submission window.

        Returns:
            dict: The settings from the submission window.
        """

        settings = {}
        for key, (widget, _) in NUKE_SUBMISSION_PANEL_LAYOUT.items():
            widget_instance = self.findChild(widget, key.replace("_", "_"))
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
        layout.setContentsMargins(25, 20, 0, 0)
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
            checkbox.setStyleSheet("spacing: 2px; margin: 0px;")
            # Set the object name
            checkbox.setObjectName(checkbox_text.replace(" ", "_"))
            checkbox.setChecked(checked)
            layout.addRow("", checkbox)

        # Add another horizontal line
        vertical_layout = QtWidgets.QVBoxLayout()
        layout.addRow(pspecial.HorizontalLine())
        vertical_layout.addLayout(layout)
        vertical_layout.addStretch()
        vertical_layout.addWidget(self.node_tree_view)
        vertical_layout.addLayout(self.buttons_layout)

        self.setLayout(vertical_layout)

        return True

    def show(self) -> None:
        """Show the submission window."""

        # If there is another instance of the submission window, close it and create a new one
        for widget in QtWidgets.QApplication.allWidgets():
            if isinstance(widget, QtWidgets.QDialog) and widget.windowTitle() == self.windowTitle():
                widget.close()

        return super().show()
