"""The module contains the tree view and the model for the tree view.
"""

from re import T
import typing as _typing
from PySide2 import QtWidgets as _QtWidgets, QtGui as _QtGui, QtCore as _QtCore

nodes = [
    {
        "node": None,
        "name": "Write1",
        "full_name": "DDWrite6.Write1",
        "class_": "Write",
        "basename": "rd1212_comp_v002.%04d.exr",
        "order": 1.0,
        "frange": "",
    },
    {
        "node": None,
        "name": "Write1",
        "full_name": "DDWrite3.Write1",
        "class_": "Write",
        "basename": "rd1212_tempcomp_bla_v002.%04d.exr",
        "order": 2.0,
        "frange": "",
    },
    {
        "node": None,
        "name": "Write1",
        "full_name": "DDWrite4.Write1",
        "class_": "Write",
        "basename": "rd1212_tests_precomp_somethjing_v001.%04d.exr",
        "order": 3.0,
        "frange": "1010-1183",
    },
    {
        "node": None,
        "name": "Write1",
        "full_name": "DDWrite2.Write1",
        "class_": "Write",
        "basename": "rd1212_comp_v006.%04d.exr",
        "order": 4.0,
        "frange": "",
    },
    {
        "node": None,
        "name": "Write1",
        "full_name": "DDWrite1.Write1",
        "class_": "Write",
        "basename": "rd1212_comp_v006.%04d.exr",
        "order": 4.0,
        "frange": "",
    },
]


class TreeviewPipeDelegate(_QtWidgets.QStyledItemDelegate):
    """A custom delegate for the tree view that draws a pipe between the parent and child items."""

    def __init__(self, parent: "_QtWidgets.QTreeView"):
        super().__init__(parent)
        self.parent_view = parent
        self.orange_pen = _QtGui.QPen(_QtGui.QColor(210, 122, 17), 2, _QtCore.Qt.SolidLine)
        self.light_orange_pen = _QtGui.QPen(_QtGui.QColor(210, 122, 17, 150), 2, _QtCore.Qt.SolidLine)
        self.light_blue_pen = _QtGui.QPen(_QtGui.QColor(0, 0, 255, 50), 5, _QtCore.Qt.SolidLine)

    def paint(self, painter: _QtGui.QPainter, option: _QtWidgets.QStyleOptionViewItem, index: _QtCore.QModelIndex):
        """Override the paint method to draw a pipe between the parent and child items.

        Args:
            painter (QPainter): The painter object used to draw the item.
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The model index of the item.

        Returns:
            bool: True if the item was painted. Otherwise, False.
        """
        super().paint(painter, option, index)
        if index.column() != 0:
            return False

        painter.save()
        has_children = index.model().hasChildren(index)
        not_last = index.model().index(index.row() + 1, index.column(), index.parent()).isValid()

        painter.setPen(self.orange_pen)

        left, top, right, bottom = (  # pylint: disable=unused-variable
            option.rect.left(),
            option.rect.top(),
            option.rect.right(),
            option.rect.bottom(),
        )
        offset_left = left - 30

        # if index.parent().isValid() and not has_children and not_last:
        #     painter.drawLine(offset_left, top, offset_left, bottom)

        # # Draw the horizontal line at the end of the children with no children
        # if index.parent().isValid() and not not_last and not has_children:
        #     painter.drawLine(offset_left, top, offset_left, bottom - 10)
        #     painter.drawLine(offset_left, bottom - 10, left - 10, bottom - 10)

        # Ignore if you are the last parent

        # Get the next item in your row
        next_item = index.model().index(index.row() + 1, index.column(), index.parent())

        # Find the name of the next item
        
        if has_children and not index.parent().isValid() and next_item.data():
            print(index.data())
            next_item_name = next_item.data()
            print(next_item_name)

            # Print the rect of the next item
            next_item_rect = option.widget.visualRect(next_item)
            print(next_item_rect)
            print("--------------------")
            painter.setPen(self.light_orange_pen)
            painter.drawLine(left - 10, bottom, left - 10, next_item_rect.top())



        painter.restore()
        return True


class NukeNodeTreeView(_QtWidgets.QTreeView):
    """A custom tree view for displaying Nuke nodes and interacting with them."""

    def __init__(self, parent: _typing.Optional["_QtWidgets.QWidget"] = None) -> None:
        """Initialize the tree view with the given parent widget.

        Args:
            parent (QWidget, optional): The parent widget of the tree view. Defaults

        """
        super().__init__(parent)

        model = _QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name", "Class", "Basename", "Order", "Frange"])
        self.resize(800, 600)
        self.move(3490, 200)

        for node in nodes:
            parent_item = _QtGui.QStandardItem(node["full_name"])
            model.appendRow(parent_item)

            # Top level items
            top = _QtGui.QStandardItem(node["name"])

            parent_item.appendRow(
                [
                    top,
                    _QtGui.QStandardItem(node["class_"]),
                    _QtGui.QStandardItem(node["basename"]),
                    _QtGui.QStandardItem(str(node["order"])),
                    _QtGui.QStandardItem(node["frange"]),
                ]
            )
            # Add some dummy children
            for i in range(3):
                child_item = _QtGui.QStandardItem(f"Child {i}")
                top.appendRow(child_item)

        self.setModel(model)
        self.setItemDelegate(TreeviewPipeDelegate(self))

        self.expandAll()

        # Increase the font
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        # Hide the header
        self.header().hide()
        _QtWidgets.QShortcut("alt+w", self, self.close)
        for column in range(model.columnCount()):
            self.resizeColumnToContents(column)
            # Add some padding to the column width
            self.setColumnWidth(column, self.columnWidth(column) + 10)

        self.setAlternatingRowColors(True)


# Create the application and the model
app = _QtWidgets.QApplication([])
# Create the tree view
tree = NukeNodeTreeView()
tree.show()
app.exec_()
