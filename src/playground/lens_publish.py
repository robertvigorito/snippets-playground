"""The new lens publish dialog is an improved version of the LensPublish dialog. The new dialog supports handling
multiple overscan values. The new dialog is also a class that can be used to load the dialog in Nuke.
"""

from ctypes import alignment
from enum import Enum as _Enum
from functools import partial as _partial
from PySide2 import QtCore as _QtCore
from PySide2 import QtGui as _QtGui
from PySide2 import QtWidgets as _QtWidgets

# DCC imports
import nuke as _nuke  # isort:skip

# Package imports

__all__ = ["LensPublishOption", "LensPublish", "load_nuke"]


from dataclasses import InitVar as _InitVar
from dataclasses import dataclass as _dataclass

import nuke as _nuke



class CollapseGroup(_QtWidgets.QWidget):
    def __init__(self, parent=None, expand_text="", collapse_text="") -> None:
        super().__init__(parent)
        self.expand_text = expand_text
        self.collapse_text = collapse_text
        self._button = _QtWidgets.QToolButton()
        self._button.setToolButtonStyle(_QtCore.Qt.ToolButtonTextBesideIcon)
        self._button.setStyleSheet("QToolButton {border: none; background-color: none;}")
        self._button.setCheckable(True)

        self._button.setArrowType(_QtCore.Qt.RightArrow)

        layout = _QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._button)
        
        # Toggle conection
        self._button.clicked.connect(self.toggle)
        self.toggle()

    def toggle(self):
        widgets = self.layout().itemAt(1)
        if not widgets:
            return
        
        if self._button.isChecked():
            self._button.setArrowType(_QtCore.Qt.DownArrow)
            self._button.setText(self.collapse_text)
            widgets.widget().show()

        else:
            self._button.setArrowType(_QtCore.Qt.RightArrow)
            self._button.setText(self.expand_text)
            widgets.widget().hide()
    






@_dataclass(eq=True)
class _NukeOverscan:
    """A class for managing image format overscan.

    Attributes:
        left (float): The left overscan value.
        bottom (float): The bottom overscan value.
        right (float): The right overscan value.
        top (float): The top overscan value.
    """

    # Dont sort, order matters
    left: float
    top: float
    right: float
    bottom: float

    _MULTIPLIER: _InitVar[int] = 2

    @classmethod
    def from_node(cls, node: "_nuke.Node") -> "_NukeOverscan":
        """Create an Overscan object from a Nuke node.

        Args:
            node (nuke.Node): The Nuke node.

        Returns:
            NukeOverscan: The overscan object.
        """
        boundary_box = node.bbox()
        width, height = node.format().width(), node.format().height()

        overscan = (
            abs(boundary_box.x()) / (abs(boundary_box.x()) + width),
            abs(boundary_box.y()) / (abs(boundary_box.y()) + height),
            (boundary_box.w() + boundary_box.x() - width) / width,
            (boundary_box.h() + boundary_box.y() - height) / height,
        )
        overscan = tuple(round(value, 3) for value in overscan)
        return cls(*overscan)

    @classmethod
    def from_x_y(cls, x: float, y: float) -> "_NukeOverscan":
        """Return an overscan object from x and y values.

        Args:
            x (float): The x overscan value.
            y (float): The y overscan value.

        Returns:
            NukeOverscan: The overscan object.
        """
        divided_x = x / cls._MULTIPLIER
        divided_y = y / cls._MULTIPLIER

        return cls(divided_x, divided_y, divided_x, divided_y)

    @classmethod
    def from_uniform(cls, value: float) -> "_NukeOverscan":
        """Return an overscan object from a uniform value.

        Args:
            value (float): The uniform overscan value.

        Returns:
            NukeOverscan: The overscan object.
        """
        divided_value = value / cls._MULTIPLIER
        return cls(divided_value, divided_value, divided_value, divided_value)

    def __iter__(self):
        return iter((self.left, self.top, self.right, self.bottom))

    def max(self) -> float:
        """Get the maximum overscan value.

        Returns:
            float: The maximum overscan value.
        """
        return max(iter(self)) * self._MULTIPLIER

    def max_x(self) -> float:
        """Get the maximum x overscan value.

        Returns:
            float: The maximum x overscan value.
        """
        return max(self.left, self.right) * self._MULTIPLIER

    def max_y(self) -> float:
        """Get the maximum y overscan value.

        Returns:
            float: The maximum y overscan value.
        """
        return max(self.top, self.bottom) * self._MULTIPLIER


class LensPublishOption(_Enum):
    """The LensPublishOption enum class."""

    PUBLISH_AND_LINK_TO_RANKED_PLATE = "Publish and Link to Ranked Plate"
    PUBLISH_AND_LINK_TO_SELECTED_PLATE = "Publish and Link to Selected Plate"
    JUST_PUBLISH = "Just Publish"


class _NumericButton(_QtWidgets.QPushButton):
    """This class is mimicking the number button you see in nuke."""

    def __init__(self, value):
        super().__init__(str(value))
        self.value = int(value)
        size = 20
        self.setMaximumWidth(size)
        self.setMaximumHeight(size)
        self.setCheckable(True)


class _SpecialLineEdit(_QtWidgets.QLineEdit):
    """This class is a line edit that has a placeholder and a validator."""

    def __init__(self, default=None, placeholder=None, validator=None, clear_button=True):
        super().__init__(str(default))
        self.setClearButtonEnabled(clear_button)
        self.setPlaceholderText(placeholder)
        if validator:
            self.setValidator(validator)


class _SpecialNumericLayout(_QtWidgets.QHBoxLayout):
    """This class is a layout that contains multiple line edits and buttons. The layout is used to handle
    multiple overscan values.

    """

    def __init__(self):
        super().__init__()
        self.format_button_one = _NumericButton("1")
        self.format_button_two = _NumericButton("2")
        self.overscan = _NukeOverscan.from_node(_nuke.selectedNode())

        # Create three line edits
        # Set float validator
        self.line_edit_one = _SpecialLineEdit(validator=_QtGui.QDoubleValidator(), clear_button=False)
        self.line_edit_two = _SpecialLineEdit(validator=_QtGui.QDoubleValidator(), clear_button=False)
        self.line_edit_three = _SpecialLineEdit(validator=_QtGui.QDoubleValidator(), clear_button=False)
        self.line_edit_four = _SpecialLineEdit(validator=_QtGui.QDoubleValidator(), clear_button=False)

        # Add to layout
        for line_edit in [self.line_edit_one, self.line_edit_two, self.line_edit_three, self.line_edit_four]:
            # Make the edit not editable
            line_edit.setReadOnly(True)
            self.addWidget(line_edit)

        for widget in [self.format_button_one, self.format_button_two]:
            self.addWidget(widget)
            widget.clicked.connect(_partial(self.layout_change, widget))

        # Default layout
        self.layout_change(self.format_button_one)

    def layout_change(self, widget):
        """Change the layout based on the button clicked.

        Args:
            widget (NumericButton): The button clicked.

        Returns:
            bool: True if successful
        """
        self.active = [
            self.line_edit_one,
            self.line_edit_two,
            self.line_edit_three,
            self.line_edit_four,
        ]
        for value, line_widget in zip(
            self.overscan, [self.line_edit_one, self.line_edit_two, self.line_edit_three, self.line_edit_four]
        ):
            # Multiply to whole number vs float
            value = value * 100
            line_widget.setText(str(value))
        hide = []
        if int(widget.text()) == 1 and widget.isChecked():
            self.active = [self.line_edit_one]
            self.line_edit_one.setText(str(self.overscan.max()))
            hide = [
                self.line_edit_two,
                self.line_edit_three,
                self.line_edit_four,
            ]
        elif int(widget.text()) == 2 and widget.isChecked():
            self.active = [self.line_edit_one, self.line_edit_two]
            hide = [self.line_edit_three, self.line_edit_four]
            self.line_edit_one.setText(str(self.overscan.max_x()))
            self.line_edit_two.setText(str(self.overscan.max_y()))

        for line_edit in self.active:
            line_edit.show()
        for line_edit in hide:
            line_edit.hide()

        for buttons in (self.format_button_one, self.format_button_two):
            if buttons != widget:
                buttons.setChecked(False)

        return True

    def update_overscan(self):
        """Update the overscan values.

        Returns:
            NukeOverscan: The overscan object.
        """
        left, top, right, bottom = (
            self.line_edit_one.text(),
            self.line_edit_two.text(),
            self.line_edit_three.text(),
            self.line_edit_four.text(),
        )

        self.overscan = _NukeOverscan(
            float(left or 0),
            float(top or 0),
            float(right or 0),
            float(bottom or 0),
        )
        return self.overscan

    def calculate_overscan(self):
        """Calculate the overscan values.

        Returns:
            NukeOverscan: The overscan object.
        """
        if len(self.active) == 1:
            self.overscan = _NukeOverscan.from_uniform(float(self.line_edit_one.text()))
        elif len(self.active) == 2:
            self.overscan = _NukeOverscan.from_x_y(float(self.line_edit_one.text()), float(self.line_edit_two.text()))
        else:
            self.overscan = self.update_overscan()

        return self.overscan


class RankedTree(_QtWidgets.QTreeView):
    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(True)
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(_QtWidgets.QHeaderView.ResizeToContents)

        import playground.ranked_snapshots as _ranked_plates

        self.setModel(_QtGui.QStandardItemModel())

        # Add the headers
        headers = ["name"] + list(_ranked_plates.Snapshot._fields)
        headers = [header.capitalize() for header in headers]
        headers = list(set(headers))
        self.model().setHorizontalHeaderLabels(["name"] + list(_ranked_plates.Snapshot._fields))

        for snapshot in _ranked_plates.snapshots:
            # Create a new item
            item = _QtGui.QStandardItem(snapshot.name)
            appendable_item = []

            for i, key in enumerate(headers):
                if i:
                    child_item = _QtGui.QStandardItem(str(getattr(snapshot, key.lower())))
                    appendable_item.append(child_item)
            self.model().invisibleRootItem().appendRow(item)
 
            # Add the item to the tree
            item.appendRow(appendable_item)

        # Select the top index
        self.selectionModel().select(
            self.model().index(0, 0), _QtCore.QItemSelectionModel.Select | _QtCore.QItemSelectionModel.Rows)
        
        # Adjust the height  by the number of rows
        self.setMinimumHeight((self.sizeHintForRow(0) + 10) * len(_ranked_plates.snapshots) + 10)
        self.hide()

    

class LensPublish:
    """The gui is an improved version of the LensPublish dialog. The new gui supports handling multiple
    multiple overscan values.

    """

    def __init__(self):
        super().__init__()

        self._main_dialog = _QtWidgets.QDialog(_QtWidgets.QApplication.activeWindow())
        self._main_dialog.setObjectName("LensPublish")
        self._main_dialog.setWindowTitle("Lens Publish")
        self._main_dialog.setMaximumWidth(500)

        # Build the code and lens line edit
        self._line_edit_name = _SpecialLineEdit(placeholder="Lens Name")
        self._line_edit_code = _SpecialLineEdit(
            placeholder="Serial #", default="00000"
        )  # I dont know why this is the default
        self._padding_line_edit = _SpecialLineEdit(default=3, validator=_QtGui.QIntValidator(), clear_button=False)
        self._padding_line_edit.setFixedWidth(75)

        self._special_numeric_layout = _SpecialNumericLayout()

        # Treeview
        self.tree_view = RankedTree()

        # groupbox
        group_box = CollapseGroup()
        group_box.layout().addWidget(self.tree_view)


        # Create a button that has multiple options
        self._publish_button = _QtWidgets.QPushButton("Publish Options")
        self._publish_button.setMenu(_QtWidgets.QMenu(self._publish_button))
        for option in LensPublishOption:
            action = self._publish_button.menu().addAction(option.value)
            action.triggered.connect(_partial(self.process, option=option))

        self.close_button = _QtWidgets.QPushButton("Close")
        self.close_button.clicked.connect(self._main_dialog.close)

        # Button layout
        button_layout = _QtWidgets.QHBoxLayout()
        button_layout.setAlignment(_QtCore.Qt.AlignRight | _QtCore.Qt.AlignBottom)
        button_layout.addWidget(self._publish_button)
        button_layout.addWidget(self.close_button)

        spacer_widget = _QtWidgets.QWidget()
        spacer_widget.setFixedHeight(35)

        # Add to layout

        layout = _QtWidgets.QVBoxLayout()
        form_layout = _QtWidgets.QFormLayout()
        form_layout.addRow("Code", self._line_edit_name)
        form_layout.addRow("Serial #", self._line_edit_code)
        form_layout.addRow("Padding", self._padding_line_edit)
        form_layout.addRow("Overscan", self._special_numeric_layout)
        form_layout.addRow(group_box)
        form_layout.addRow(spacer_widget)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout, alignment=_QtCore.Qt.AlignBottom)
        self._main_dialog.setLayout(layout)


        self._main_dialog.show()

    def results(self):
        """Get the results from the LensPublish dialog."""
        return {
            "name": self._line_edit_name.text(),
            "code": self._line_edit_code.text(),
            "overscan": [
                self._special_numeric_layout.line_edit_one.text(),
                self._special_numeric_layout.line_edit_two.text(),
                self._special_numeric_layout.line_edit_three.text(),
                self._special_numeric_layout.line_edit_four.text(),
            ],
        }

    def process(self, option):
        """Process the LensPublish dialog."""
        print(self._special_numeric_layout.calculate_overscan())


def load_nuke():
    """The function to load the LensPublish dialog in Nuke.

    Returns:
        LensPublish: The LensPublish dialog instance.
    """
    # Close any opened LensPublish dialog
    for widget in _QtWidgets.QApplication.allWidgets():
        if widget.objectName() == "LensPublish":
            widget.close()

    lens_publish = LensPublish()
    return lens_publish

