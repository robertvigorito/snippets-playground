import random
from typing import Optional
from PySide2 import QtWidgets, QtGui, QtCore


class TreeviewPipeDelegate(QtWidgets.QStyledItemDelegate):
    """A custom delegate for the tree view that draws a pipe between the parent and child items."""

    def __init__(self, parent: "QtWidgets.QTreeView"):
        super().__init__(parent)
        self.parent_view = parent
        self.orange_pen = QtGui.QPen(QtGui.QColor(210, 122, 17), 2, QtCore.Qt.SolidLine)
        self.light_orange_pen = QtGui.QPen(QtGui.QColor(210, 122, 17, 150), 2, QtCore.Qt.SolidLine)
        self.light_blue_pen = QtGui.QPen(QtGui.QColor(0, 0, 255, 50), 2, QtCore.Qt.SolidLine)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        """Override the paint method to draw a pipe between the parent and child items.

        Args:
            painter (QPainter): The painter object used to draw the item.
            option (QStyleOptionViewItem): The style options for the item.
            index (QModelIndex): The model index of the item.

        Returns:
            bool: True if the item was painted. Otherwise, False.
        """
        super().paint(painter, option, index)
        has_children = self.parent_view.model().hasChildren(index)
        not_last = index.model().index(index.row() + 1, index.column(), index.parent()).isValid()

        painter.setPen(self.orange_pen)

        left, top, right, bottom = (  # pylint: disable=unused-variable
            option.rect.left(),
            option.rect.top(),
            option.rect.right(),
            option.rect.bottom(),
        )
        option.rect = QtCore.QRect(left, top, right - left, bottom - top)
        offset_left = left - 10

        if index.parent().isValid() and not has_children:
            if not not_last:
                bottom -= 10
                painter.drawLine(offset_left, bottom, offset_left + 10, bottom)
            painter.drawLine(offset_left, top, offset_left, bottom)

        if has_children:
            next_item = index.model().index(index.row() + 1, index.column(), index.parent())
            print("*" * 50)
            print(index.data())
            if next_item.data() is None:
                next_item = index.model().index(next_item.parent().row() + 1, next_item.column(), next_item.parent().parent())
                print(next_item.data(), "here")
            print(next_item.data())

            painter.setPen(self.light_orange_pen)
            painter.drawLine(offset_left, top, offset_left, bottom)

            # painter.drawLine(left - 10, bottom, left - 10, next_item_rect.top())

        return True


class TreeviewPipe(QtWidgets.QTreeView):

    def __init__(self) -> None:
        super().__init__()

        # self.setIndentation(20)
        # self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.resize(800, 600)
        # self.setAllColumnsShowFocus(True)

        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name", "Class", "Basename", "Order", "Frange"])

        self.setModel(model)

        QtWidgets.QShortcut("alt+w", self, self.close)

        for i in range(3):
            parent = QtGui.QStandardItem(f"Parent {i}")

            for j in range(random.randint(2, 5)):
                child = QtGui.QStandardItem(f"Child {j}")
                parent.appendRow(child)
                for k in range(random.randint(2, 4)):
                    new_child = QtGui.QStandardItem(f"Child {j}.{k}")
                    child.appendRow(new_child)
                    new_child.appendRows([QtGui.QStandardItem(f"{k} column") for k in range(random.randint(2, 7))])

            model.appendRow(parent)
        # Assign the delegate to the tree view
        self.setItemDelegate(TreeviewPipeDelegate(self))

        self.expandAll()
        self.move(3500, 100)

        for column in range(model.columnCount()):
            self.resizeColumnToContents(column)
            # Add some padding to the column width
            self.setColumnWidth(column, self.columnWidth(column) + 50)

        # Increase the font size
        font = self.font()
        font.setPointSize(11)
        self.setFont(font)


app = QtWidgets.QApplication([])

TreeView = TreeviewPipe()
TreeView.show()

app.exec_()
